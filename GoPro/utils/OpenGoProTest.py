
#import threading, time, json, inspect, traceback

#https://gopro.github.io/OpenGoPro/python_sdk/api.html#wired

import time
from open_gopro import WiredGoPro, Params
from open_gopro import constants

class GoPro:
    def __init__(self):
        pass

    def connect(self):
        pass

    def disconnect(self):
        pass

# some tests
if __name__ == '__main__':
    #gopro = WiredGoPro("5753")
    gopro = WiredGoPro("8820")
    gopro.open()

    print(gopro.http_command.get_media_list().flatten)
    status = gopro.http_command.get_camera_state().flatten
    #print(status)

    print("Battery: {}".format(status[constants.StatusId.INT_BATT_PER]))
    print("WIFI Enabled: {}".format(status[constants.StatusId.WIRELESS_ENABLED]))

    # stop the recording if necessary
    gopro.http_command.set_shutter(shutter=Params.Toggle.DISABLE)

    #print( gopro.http_setting.video_performance_mode.set(Params.PerformanceMode.MAX_PERFORMANCE) )
    print( gopro.http_setting.video_performance_mode.set(Params.PerformanceMode.EXTENDED_BATTERY) )
    print( gopro.http_setting.system_video_mode.set(Params.SystemVideoMode.HIGHEST_QUALITY) )
    print( gopro.http_setting.fps.set(Params.FPS.FPS_30 ) )
    print( gopro.http_setting.video_field_of_view.set(Params.VideoFOV.HYPERVIEW) )

    # activate video
    gopro.http_command.load_preset_group(group=Params.PresetGroup.VIDEO)

    assert gopro.http_command.set_shutter(shutter=Params.Toggle.ENABLE).is_ok
    time.sleep(2)
    assert gopro.http_command.set_shutter(shutter=Params.Toggle.DISABLE).is_ok

    files = gopro.http_command.get_media_list().flatten

    gopro.close()
    
