import datetime
import logging

from open_gopro import WiredGoPro, Params
from open_gopro import constants
from open_gopro import interface

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

    def _init(self):
        self.__cam = WiredGoPro(None, rules=[interface.MessageRules.FASTPASS])
        self.__cam.open()

    def _unset(self):
        if self.__cam:
            self.__cam.close()
            self.__cam = None

    def _update_status(self) -> bool:
        if self.__cam and self.__cam.is_open:
            # get GoPro state
            response = self.__cam.http_command.get_camera_state()
            if response.is_ok:
                self.__cam_state = response.data
            else:
                logger.warning(f'Unable to get camera state ({response.status})')

            # get GoPro presets
            response = self.__cam.http_command.get_preset_status()
            if response.is_ok:
                self.__cam_presets = response.data
            else:
                logger.warning(f'Unable to get camera presets ({response.status})')

            # get GoPro date & time
            response = self.__cam.http_command.get_date_time()
            if response.is_ok:
                self.__cam_datetime = response.data
            else:
                logger.warning(f'Unable to get camera datetime ({response.status})')

            # TODO: get status
            # - mode
            # - recording state
            # - sdcard
            # - lastvideo
            # - datetime
            # - camerasettings
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
            if self.__cam_state[constants.StatusId.ACTIVE_PRESET] == '65536':
                return GoPro.Modes.PHOTO
            elif self.__cam_state[constants.StatusId.ACTIVE_PRESET] == '65536':
                return GoPro.Modes.VIDEO
        return 'unknown'  # TODO

    def _set_video_mode(self):
        self.__cam.http_setting.video_performance_mode.set(Params.PerformanceMode.STATIONARY)
        self.__cam.http_setting.max_lens_mode.set(Params.MaxLensMode.DEFAULT)
        self.__cam.http_setting.camera_ux_mode.set(Params.CameraUxMode.PRO)
        self.__cam.http_command.set_turbo_mode(mode=Params.Toggle.DISABLE)
        self.__cam.http_command.load_preset_group(group=Params.PresetGroup.VIDEO)

    def _take_photo(self):
        self.__cam.http_setting.video_performance_mode.set(Params.PerformanceMode.STATIONARY)
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

    def __set(self, setting, value):
        return False  # TODO

    def _fps(self) -> str:
        return '30'  # TODO

    def _set_fps(self, value) -> bool:
        return False  # TODO

    def _fov(self) -> str:
        return 'medium'  # TODO

    def _set_fov(self, value) -> bool:
        return False  # TODO

    def _res(self) -> str:
        return '1080p'  # TODO

    def _set_res(self, value) -> bool:
        return False  # TODO


# some tests
if __name__ == '__main__':
    #10.1.12.74

    logging.basicConfig(level=logging.ERROR)
    #logger = setup_logging('OpenGoPro')
    #logger.setLevel(logging.CRITICAL)

    print('Start OpenGopro')
    g = OpenGoPro(False, False, 900)
    g.start()
    blackboard['network'] = 3  # simulate network available
    while True:
        cmd = input('>>>')
        if cmd in ['e', 'exit']:
            break
        elif cmd == 'start':
            g.startRecording()
        elif cmd == 'stop':
            g.stopRecording()
        elif cmd == 'status':
            #print(g.__cam_status)
            print(blackboard)
    g.cancel()
    g.join()
    print('Done')
