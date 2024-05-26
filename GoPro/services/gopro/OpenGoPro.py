import asyncio
import datetime
import logging
import zmq

from open_gopro import WiredGoPro, Params, constants, exceptions, logger as gp_logger

from services import Messages
from services.gopro.GoPro import GoPro


class OpenGoPro(GoPro):
    def __init__(self,
                 context: zmq.Context,
                 mq_send: int,
                 mq_recv: int,
                 quiet: bool,
                 ignore: bool,
                 max_time: int,
                 rec_invisible: bool = False,
                 update_interval: float = 0.5,
                 logger: logging.Logger = None):

        super().__init__(context, mq_send, mq_recv, quiet, ignore, max_time, rec_invisible, update_interval, logger)
        # TODO: add parameter/config to set the connection timeout
        self.__cam = None  # type: WiredGoPro|None
        self.__cam_state = {}
        self.__cam_presets = {}
        self.__cam_datetime = None

        # set OpenGoPro logging to ERROR (do not spam log)
        lvl = self._logger.level
        gp_logger.setup_logging(self._logger)
        for m in gp_logger.Logger.get_instance().modules:
            logging.getLogger(m).setLevel(logging.ERROR)
        # OpenGopro adds a RichHandler -- we don't want that
        self._logger.handlers.clear()
        # OpenGopro modifies the log level -- reset it
        self._logger.level = lvl
        # also ignore from asyncio
        logging.getLogger('asyncio').setLevel(logging.WARNING)
        logging.getLogger('zeroconf').setLevel(logging.ERROR)

    def _connect(self) -> bool:
        self._logger.info("Connecting to GoPro ...")
        self._update(state=Messages.GoProStatus.State.CONNECTING)

        self.__cam = WiredGoPro()
        try:
            asyncio.run(self._open())
            return True
        except exceptions.FailedToFindDevice:
            self._logger.debug('Failed to find device')
            self.__cam = None

        return False

    async def _open(self):
        """Try to open the camera and stops recoding in case it is currently recording.

           If the camera is recording, while attempting to connect to it, the open_gopro library blocks until the
           recording is manually stopped (). To fix this, we start another method, which waits until the camera is
           found and then sends the stop request, so that the open_gopro library can continue.
           see: https://github.com/gopro/OpenGoPro/issues/405
        """
        async def stop_shutter():
            while True:
                try:
                    self._logger.debug(f"Try to stop recording on open() for {self.__cam.identifier}")
                    break
                except exceptions.GoProNotOpened:
                    await asyncio.sleep(1)

            state = (await self.__cam.http_command.get_camera_state()).data
            if state.get(constants.StatusId.ENCODING) or state.get(constants.StatusId.SYSTEM_BUSY):
                await self.__cam.http_command.set_shutter(shutter=Params.Toggle.DISABLE)

        await asyncio.gather(self.__cam.open(), stop_shutter())

    def _unset(self):
        if self.__cam:
            asyncio.run(self.__cam.close())
            self.__cam = None

    def _keep_alive(self):
        # if recording, the open_gopro library blocks until finished - update status to make sure, we're not recording!
        if self._update_status() and not self.is_recording:
            self._logger.debug('Keep alive...')
            asyncio.run(self.__cam.http_command.set_keep_alive())

    def _update_status(self) -> bool:
        if self.__cam and self.__cam.is_open:
            # get GoPro state
            try:
                response = asyncio.run(self.__cam.http_command.get_camera_state())
                if response.ok:
                    self.__cam_state = response.data
                else:
                    self._logger.warning(f'Unable to get camera state ({response.status})')
            except exceptions.ResponseTimeout:
                self._logger.warning('Lost connection while get camera state?!')
                return False

            # certain commands require, that the GoPro has a certain state (not recording or otherwise busy)
            # the open_gopro library waits for that state (enforce_message_rules, _wait_for_state)
            if not self.is_recording:
                # get GoPro presets
                try:
                    response = asyncio.run(self.__cam.http_command.get_preset_status())
                    if response.ok:
                        # parse and re-order presets
                        for g in response.data['presetGroupArray']:
                            for p in g['presetArray']:
                                self.__cam_presets[p['id']] = p
                                self.__cam_presets[p['id']]['group'] = g['id']
                    else:
                        self._logger.warning(f'Unable to get camera presets ({response.status})')
                except exceptions.ResponseTimeout:
                    self._logger.warning('Lost connection while get preset status?!')
                    return False

                # get GoPro date & time
                try:
                    response = asyncio.run(self.__cam.http_command.get_date_time())
                    if response.ok:
                        self.__cam_datetime = response.data
                    else:
                        self._logger.warning(f'Unable to get camera datetime ({response.status})')
                except exceptions.ResponseTimeout:
                    self._logger.warning('Lost connection while get date/time?!')
                    return False

            return True
        return False

    def _info(self) -> dict:
        # Note: most of the data is only available via bluetooth
        return {
            'model_name': 'Unknown',
            'firmware_version': 'Unknown',
            'serial_number': 'Unknown',
            'ap_ssid': self.__cam_state[constants.StatusId.AP_SSID],
            'battery': self.__cam_state[constants.StatusId.INT_BATT_PER],
            'system_hot': self.__cam_state[constants.StatusId.SYSTEM_HOT],
        }

    def _mode(self):
        if self.__cam_state:
            if self.__cam_state[constants.StatusId.ACTIVE_PRESET] in self.__cam_presets:
                mode = self.__cam_presets[self.__cam_state[constants.StatusId.ACTIVE_PRESET]]
                # TODO: should we be more specific which mode is currently set?
                if mode['group'] == 'PRESET_GROUP_ID_PHOTO':
                    return GoPro.Modes.PHOTO
                elif mode['group'] == 'PRESET_GROUP_ID_VIDEO':
                    return GoPro.Modes.VIDEO
        return 'unknown'

    def _set_video_mode(self):
        # NOTE: STATIONARY mode has limited setting options!
        asyncio.run(self.__cam.http_setting.video_performance_mode.set(Params.PerformanceMode.EXTENDED_BATTERY))
        asyncio.run(self.__cam.http_setting.max_lens_mode.set(Params.MaxLensMode.DEFAULT))
        asyncio.run(self.__cam.http_setting.camera_ux_mode.set(Params.CameraUxMode.PRO))
        asyncio.run(self.__cam.http_command.set_turbo_mode(mode=Params.Toggle.DISABLE))
        asyncio.run(self.__cam.http_command.load_preset_group(group=Params.PresetGroup.VIDEO))

    def _take_photo(self):
        # NOTE: STATIONARY mode has limited setting options!
        asyncio.run(self.__cam.http_setting.video_performance_mode.set(Params.PerformanceMode.EXTENDED_BATTERY))
        asyncio.run(self.__cam.http_setting.max_lens_mode.set(Params.MaxLensMode.DEFAULT))
        asyncio.run(self.__cam.http_setting.camera_ux_mode.set(Params.CameraUxMode.PRO))
        asyncio.run(self.__cam.http_command.set_turbo_mode(mode=Params.Toggle.DISABLE))
        if asyncio.run(self.__cam.http_command.load_preset_group(group=Params.PresetGroup.PHOTO)).ok:
            asyncio.run(self.__cam.http_command.set_shutter(shutter=Params.Toggle.ENABLE))

    def _datetime(self):
        return datetime.datetime.strptime("{2}.{1}.{0} {3}:{4}:{5}".format(*self.__cam_datetime['date'].split('_') + self.__cam_datetime['time'].split('_')), '%d.%m.%Y %H:%M:%S')

    def _is_recording(self) -> bool:
        return self.__cam_state[constants.StatusId.SYSTEM_BUSY] \
            or self.__cam_state[constants.StatusId.ENCODING]

    def _has_sdcard(self) -> bool:
        return self.__cam_state[constants.StatusId.SD_STATUS] == Params.SDStatus.OK \
           and self.__cam_state[constants.StatusId.SPACE_REM] > 100

    def _start_recording(self):
        asyncio.run(self.__cam.http_command.set_shutter(shutter=Params.Toggle.ENABLE))

    def _stop_recording(self):
        asyncio.run(self.__cam.http_command.set_shutter(shutter=Params.Toggle.DISABLE))

    def _last_video(self) -> str:
        return ''  # TODO

    def _fps(self) -> str:
        fps = self.__cam_state[constants.SettingId.FPS]
        if fps == Params.FPS.FPS_24:
            return GoPro.Settings.FrameRate.FR_24
        elif fps == Params.FPS.FPS_25:
            return GoPro.Settings.FrameRate.FR_25
        elif fps == Params.FPS.FPS_30:
            return GoPro.Settings.FrameRate.FR_30
        elif fps == Params.FPS.FPS_50:
            return GoPro.Settings.FrameRate.FR_50
        elif fps == Params.FPS.FPS_60:
            return GoPro.Settings.FrameRate.FR_60
        elif fps == Params.FPS.FPS_100:
            return GoPro.Settings.FrameRate.FR_100
        elif fps == Params.FPS.FPS_120:
            return GoPro.Settings.FrameRate.FR_120
        elif fps == Params.FPS.FPS_240:
            return GoPro.Settings.FrameRate.FR_240

        return 'unknown'

    def _set_fps(self, value) -> bool:
        def set(v):
            try:
                asyncio.run(self.__cam.http_setting.fps.set(v))
                return True
            except:
                pass  # TODO: handle exceptions?!
            return False

        if value == GoPro.Settings.FrameRate.FR_24:
            return set(Params.FPS.FPS_24)
        elif value == GoPro.Settings.FrameRate.FR_25:
            return set(Params.FPS.FPS_25)
        elif value == GoPro.Settings.FrameRate.FR_30:
            return set(Params.FPS.FPS_30)
        elif value == GoPro.Settings.FrameRate.FR_50:
            return set(Params.FPS.FPS_50)
        elif value == GoPro.Settings.FrameRate.FR_60:
            return set(Params.FPS.FPS_60)
        elif value == GoPro.Settings.FrameRate.FR_100:
            return set(Params.FPS.FPS_100)
        elif value == GoPro.Settings.FrameRate.FR_120:
            return set(Params.FPS.FPS_120)
        elif value == GoPro.Settings.FrameRate.FR_240:
            return set(Params.FPS.FPS_240)

        return False

    def _fov(self) -> str:
        fov = self.__cam_state[constants.SettingId.VIDEO_FOV]
        if fov == Params.VideoFOV.NARROW:
            return GoPro.Settings.Fov.NARROW
        elif fov == Params.VideoFOV.LINEAR_HORIZON_LEVELING:
            return GoPro.Settings.Fov.MEDIUM
        elif fov == Params.VideoFOV.WIDE:
            return GoPro.Settings.Fov.WIDE
        elif fov == Params.VideoFOV.SUPERVIEW:
            return GoPro.Settings.Fov.SV
        elif fov == Params.VideoFOV.LINEAR:
            return GoPro.Settings.Fov.LINEAR

        return 'unknown'

    def _set_fov(self, value) -> bool:
        def set(v):
            try:
                asyncio.run(self.__cam.http_setting.video_field_of_view.set(v))
                return True
            except:
                pass  # TODO: handle exceptions?!
            return False

        if value == GoPro.Settings.Fov.NARROW:
            return set(Params.VideoFOV.NARROW)
        elif value == GoPro.Settings.Fov.MEDIUM:
            return set(Params.VideoFOV.LINEAR_HORIZON_LEVELING)
        elif value == GoPro.Settings.Fov.WIDE:
            return set(Params.VideoFOV.WIDE)
        elif value == GoPro.Settings.Fov.SV:
            return set(Params.VideoFOV.SUPERVIEW)
        elif value == GoPro.Settings.Fov.LINEAR:
            return set(Params.VideoFOV.LINEAR)

        return False

    def _res(self) -> str:
        res = self.__cam_state[constants.SettingId.RESOLUTION]
        if res == Params.Resolution.RES_4K:
            return GoPro.Settings.Resolution.R_4K
        elif res == Params.Resolution.RES_2_7K:
            return GoPro.Settings.Resolution.R_2K
        elif res == Params.Resolution.RES_1440:
            return GoPro.Settings.Resolution.R_1440P
        elif res == Params.Resolution.RES_1080:
            return GoPro.Settings.Resolution.R_1080P
        return 'unknown'

    def _set_res(self, value) -> bool:
        def set(v):
            try:
                asyncio.run(self.__cam.http_setting.resolution.set(v))
                return True
            except:
                pass  # TODO: handle exceptions?!
            return False

        if value == GoPro.Settings.Resolution.R_4K:
            return set(Params.Resolution.RES_4K)
        elif value == GoPro.Settings.Resolution.R_2K:
            return set(Params.Resolution.RES_2_7K)
        elif value == GoPro.Settings.Resolution.R_1440P:
            return set(Params.Resolution.RES_1440)
        elif value == GoPro.Settings.Resolution.R_1080P:
            return set(Params.Resolution.RES_1080)

        return False
