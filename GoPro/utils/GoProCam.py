import datetime
import inspect
import json
import logging
import time

from goprocam import GoProCamera, constants
from utils import blackboard, GoPro, Logger

# setup logger for network related logs
logger = Logger.getLogger("GoProCam")


class GoProCam(GoPro):
    def __init__(self, quiet: bool, ignore: bool, max_time: int, rec_invisible: bool = False):
        super().__init__(quiet, ignore, max_time, rec_invisible)
        self.__cam = None
        self.__cam_info = {}
        self.__cam_status = {}

    def _init(self):
        while blackboard['network'] != 3 and not self.is_canceled:
            time.sleep(0.5)  # wait until the network is ready/connected
        self.__cam = GoProCamera.GoPro()

    def _unset(self):
        self.__cam = None

    def _update_status(self) -> bool:
        if self.__cam:
            raw = self.__cam.getStatusRaw()
            if raw and self.__cam:
                js = json.loads(raw)
                if constants.Status.Status in js:
                    self.__cam_status['mode'] = self.__cam.parse_value("mode", js[constants.Status.Status][constants.Status.STATUS.Mode])
                    self.__cam_status['recording'] = (js[constants.Status.Status][constants.Status.STATUS.IsRecording] == 1)
                    self.__cam_status['sd_card'] = (js[constants.Status.Status][constants.Status.STATUS.SdCardInserted] == 0)
                    self.__cam_status['lastVideo'] = self.__cam.getMedia()
                    # parse and format datetime data
                    self.__cam_status['datetime'] = "{2:02.0f}.{1:02.0f}.{0} {3:02.0f}:{4:02.0f}:{5:02.0f}".format(*map(lambda h: int(h, 16), filter(None, js[constants.Status.Status]['40'].split('%'))))
                    # update video settings
                    for var, val in vars(constants.Video).items():
                        if not var.startswith("_") and not inspect.isclass(val) and val in js[constants.Status.Settings]:
                            self.cam_settings[var] = (val, js[constants.Status.Settings][val])
                    # {'RESOLUTION': ('2', 8), 'FRAME_RATE': ('3', 8), 'FOV': ('4', 0), 'LOW_LIGHT': ('5', 0), 'SPOT_METER': ('9', 1), 'VIDEO_LOOP_TIME': ('6', 1), 'VIDEO_PHOTO_INTERVAL': ('7', 0), 'PROTUNE_VIDEO': ('10', 0), 'WHITE_BALANCE': ('11', 0), 'COLOR': ('12', 1), 'ISO_LIMIT': ('13', 2), 'ISO_MODE': ('74', 0), 'SHARPNESS': ('14', 3), 'EVCOMP': ('15', 5)}
                    return True
                else:
                    logger.warning("Failed to get status of the gopro: %s", raw)
        return False

    def _info(self) -> dict:
        if self.__cam:
            self.__cam_info = self.__cam.infoCamera()
        return self.__cam_info

    def _mode(self):
        if self.__cam_status:
            return self.__cam_status['mode']
        return 'unknown'

    def _set_video_mode(self):
        if self.__cam:
            self.__cam.mode(constants.Mode.VideoMode)
            # wait for the command to be executed
            time.sleep(0.5)

    def _take_photo(self):
        if self.__cam:
            self.__cam.take_photo()

    def _datetime(self):
        return datetime.datetime.strptime(self.__cam_status['datetime'], '%d.%m.%y %H:%M:%S')

    def _is_recording(self) -> bool:
        return self.__cam_status['recording']

    def _has_sdcard(self) -> bool:
        return self.__cam_status['sd_card']

    def _start_recording(self):
        if self.__cam:
            self.__cam.shutter(constants.start)
            time.sleep(1)  # wait for the command to be executed

    def _stop_recording(self):
        if self.__cam:
            self.__cam.shutter(constants.stop)
            time.sleep(1)  # wait for the command to be executed

    def _last_video(self) -> str:
        return self.__cam_status['lastVideo']

    def __set(self, setting, value):
        if self.__cam:
            response = self.__cam.gpControlSet(str(setting), str(value))
            print(response)
            return len(response) == 0
        return False

    def _fps(self) -> str:
        return self.cam_settings['FRAME_RATE']

    def _set_fps(self, value) -> bool:
        # TODO: map all other fps settings!
        return self.__set(constants.Video.FRAME_RATE, constants.Video.FrameRate.FR30)

    def _fov(self) -> str:
        return self.cam_settings['FOV']

    def _set_fov(self, value) -> bool:
        # TODO: map all other fov settings!
        return self.__set(constants.Video.FOV, constants.Video.Fov.SuperView)

    def _res(self) -> str:
        return self.cam_settings['RESOLUTION']

    def _set_res(self, value) -> bool:
        # TODO: map all other resolution settings!
        return self.__set(constants.Video.RESOLUTION, constants.Video.Resolution.R1080pSV)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    print('Start GoproCam')
    g = GoProCam(False, False, 900)
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
