import datetime
import logging


from open_gopro import WiredGoPro, Params, constants, interface
from open_gopro.util import setup_logging, Logger as OGLogger

from utils import GoPro, Logger, blackboard

# setup logger for network related logs
logger = Logger.getLogger("OpenGoPro")


class OpenGoPro(GoPro):
    def __init__(self, quiet: bool, ignore: bool, max_time: int, rec_invisible: bool = False):
        super().__init__(quiet, ignore, max_time, rec_invisible)
        # TODO: add parameter/config to set the connection timeout
        self.__cam = None  # type: WiredGoPro|None
        self.__cam_state = {}
        self.__cam_presets = {}
        self.__cam_datetime = None

        # set OpenGoPro logging to ERROR (do not spam log)
        setup_logging(logger)
        for m in OGLogger.get_instance().modules.keys():
            logging.getLogger(m).setLevel(logging.ERROR)

    def _init(self):
        self.__cam = WiredGoPro(None, rules=[interface.MessageRules.FASTPASS])
        self.__cam.open()
        # HACK: a network is not required anymore
        blackboard['network'] = 3

    def _unset(self):
        if self.__cam:
            self.__cam.close()
            self.__cam = None

    def _keep_alive(self):
        if self.__cam:
            self.__cam.http_command.set_keep_alive()

    def _update_status(self) -> bool:
        if self.__cam and self.__cam.is_open:
            # get GoPro state
            response = self.__cam.http_command.get_camera_state()
            if response.is_ok:
                self.__cam_state = response.data
            else:
                logger.warning(f'Unable to get camera state ({response.status})')

            # certain commands require, that the GoPro has a certain state (not recording or otherwise busy)
            # the open_gopro library waits for that state (enforce_message_rules, _wait_for_state)
            if not self.is_recording:
                # get GoPro presets
                response = self.__cam.http_command.get_preset_status()
                if response.is_ok:
                    # parse and re-order presets
                    for g in response.data['presetGroupArray']:
                        for p in g['presetArray']:
                            self.__cam_presets[p['id']] = p
                            self.__cam_presets[p['id']]['group'] = g['id']
                else:
                    logger.warning(f'Unable to get camera presets ({response.status})')

                # get GoPro date & time
                response = self.__cam.http_command.get_date_time()
                if response.is_ok:
                    self.__cam_datetime = response.data
                else:
                    logger.warning(f'Unable to get camera datetime ({response.status})')

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
        self.__cam.http_setting.video_performance_mode.set(Params.PerformanceMode.EXTENDED_BATTERY)
        self.__cam.http_setting.max_lens_mode.set(Params.MaxLensMode.DEFAULT)
        self.__cam.http_setting.camera_ux_mode.set(Params.CameraUxMode.PRO)
        self.__cam.http_command.set_turbo_mode(mode=Params.Toggle.DISABLE)
        self.__cam.http_command.load_preset_group(group=Params.PresetGroup.VIDEO)

    def _take_photo(self):
        # NOTE: STATIONARY mode has limited setting options!
        self.__cam.http_setting.video_performance_mode.set(Params.PerformanceMode.EXTENDED_BATTERY)
        self.__cam.http_setting.max_lens_mode.set(Params.MaxLensMode.DEFAULT)
        self.__cam.http_setting.camera_ux_mode.set(Params.CameraUxMode.PRO)
        self.__cam.http_command.set_turbo_mode(mode=Params.Toggle.DISABLE)
        if self.__cam.http_command.load_preset_group(group=Params.PresetGroup.PHOTO).is_ok:
            self.__cam.http_command.set_shutter(shutter=Params.Toggle.ENABLE)

    def _datetime(self):
        return datetime.datetime.strptime("{2}.{1}.{0} {3}:{4}:{5}".format(*self.__cam_datetime['date'].split('_') + self.__cam_datetime['time'].split('_')), '%d.%m.%Y %H:%M:%S')

    def _is_recording(self) -> bool:
        return self.__cam_state[constants.StatusId.SYSTEM_BUSY] \
            or self.__cam_state[constants.StatusId.ENCODING]

    def _has_sdcard(self) -> bool:
        return self.__cam_state[constants.StatusId.SD_STATUS] == Params.SDStatus.OK \
           and self.__cam_state[constants.StatusId.SPACE_REM] > 100

    def _start_recording(self):
        self.__cam.http_command.set_shutter(shutter=Params.Toggle.ENABLE)

    def _stop_recording(self):
        self.__cam.http_command.set_shutter(shutter=Params.Toggle.DISABLE)

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
                self.__cam.http_setting.fps.set(v)
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
                self.__cam.http_setting.video_field_of_view.set(v)
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
                self.__cam.http_setting.resolution.set(v)
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


# some tests
if __name__ == '__main__':
    print('Start OpenGopro')
    g = OpenGoPro(False, False, 900)
    g.start()
    blackboard['network'] = 3  # simulate network available
    while True:
        cmd = input('>>>')
        if cmd in ['h', 'help']:
            print('start|stop|status|photo|mode|exit')
        elif cmd == 'start':
            g.startRecording()
        elif cmd == 'stop':
            g.stopRecording()
        elif cmd == 'status':
            print(blackboard)
        elif cmd == 'photo':
            g.take_photo()
        elif cmd == 'mode':
            print(g.mode)
        elif cmd in ['e', 'exit']:
            break
    g.cancel()
    g.join()
    print('Done')
