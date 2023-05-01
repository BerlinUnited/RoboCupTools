
import threading, time, json, inspect, traceback

from .GameControlData import GameControlData

from open_gopro import WiredGoPro, Params
from open_gopro import constants
from open_gopro import interface

from utils import Logger, blackboard

# setup logger for network related logs
logger = Logger.getLogger("GoPro")

class GoPro(threading.Thread):
    def __init__(self, quiet:bool, ignore:bool, max_time:int, rec_invisible:bool=False):
        super().__init__()

        self.quiet = quiet
        self.ignore = ignore
        self.max_time = max_time
        self.rec_invisible = rec_invisible
        self.take_photo_when_idle = 0 # in seconds
        self.take_photo_timestamp = 0

        self.cam = None
        self.cam_status = { 
            'recording': False, 
            'mode': None, 
            'lastVideo': None, 
            'sd_card': True, 
            'info': {}, 
            'datetime': None 
        }
        self.cam_settings = {}
        self.user_settings = {}
        self.gc_data = GameControlData()

        # init blackboard structure
        blackboard['gopro'] = { 
            'state': 0, 
            'info': None, 
            'lastVideo': None, 
            'datetime': None 
        }

        self.time_since_update = 0

        self.is_connected = False
        self.__cancel = threading.Event()

    def setUserSettings(self, settings):
        self.user_settings = settings
        if self.cam:
            self.__updateUserSettings()

    def run(self):
        # init game state
        previous_state = { 'game': GameControlData.STATE_INITIAL, 'time': time.time(), 'card': True }

        self.connect()

        # run until canceled
        while not self.__cancel.is_set():

            #print(blackboard['gopro'], flush=True)

            try:
                # wait 'till (re-)connected to network and gopro
                # TODO: we don't need network for the USB connection
                if True or blackboard['network'] == 3:
                    blackboard['network'] = 3

                    # retrieve GameController data
                    self.gc_data = blackboard['gamecontroller']
                    # valid cam
                    if self.cam is not None:

                        # update internal cam status
                        if not self.updateStatus():
                            # disconnected?!?
                            self.disconnect()
                        
                        # handling recording state
                        previous_state['game'] = self.handleRecording(previous_state)
                         
                        # take "keep alive" photo;
                        #if self.take_photo_when_idle > 0 and self.take_photo_timestamp + self.take_photo_when_idle < time.time():
                        #    self.takePhoto()

                        # update sd-card status on the blackboard
                        if previous_state['card'] == True and self.cam_status['sd_card'] == False:
                            blackboard['gopro']['state'] = 3 # GoproNoSdcard
                        elif previous_state['card'] == False and self.cam_status['sd_card'] == True:
                            blackboard['gopro']['state'] = 2 # GoproSdcardInserted
                        previous_state['card'] = self.cam_status['sd_card']
                    else:
                        self.is_connected = False
                else:
                    #
                    self.disconnect()

            except Exception as ex:
                # something unexpected happen!?
                Logger.error("{}\n{}".format(str(ex), traceback.format_exc()))

        # if canceled, at least fire the disconnect event
        self.disconnect()
        logger.debug("GoPro thread finished.")

    def connect(self):


        # try to connect
        while not self.is_connected and not self.__cancel.is_set():
            # get GoPro
            print("Connecting to GoPro ...", flush=True)

            # statusMonitor.setConnectingToGoPro(20)
            blackboard['gopro']['state'] = 1 # GoproConnecting
            
            # HACK: we don't need network here
            blackboard['network'] = 3 # network connected

            # TODO
            #self.cam = GoProCamera.GoPro() 
            # "5753" 
            self.cam = WiredGoPro(serial = "8756", rules=[interface.MessageRules.FASTPASS])
            #self.cam = WiredGoPro(serial = "5753", rules=[interface.MessageRules.FASTPASS])
            
            # TODO: what does it do? it seems to make problems.
            # this is buggy
            #self.cam.open()
            self.cam.http_command.wired_usb_control(control=Params.Toggle.ENABLE)
            self.cam._open = True

            # hack: stop recording at the start
            if self.cam.is_encoding:
                self.cam.http_command.set_shutter(shutter=Params.Toggle.DISABLE)

            if self.updateStatus():
                
                # TODO
                #self.cam_status['info'] = self.cam.infoCamera()
                self.cam_status['info'] = {}

                blackboard['gopro']['state'] = 2 # GoproConnected
                blackboard['gopro']['info'] = self.cam_status['info']
                blackboard['gopro']['datetime'] = self.cam_status['datetime']

                # set GoPro to video mode
                self.setCamVideoMode()
                #self.__updateUserSettings()
                self.is_connected = True

                # if cam already recording, raise event
                if self.cam_status['recording']:
                    blackboard['gopro']['state'] = 4 # GoproStartRecording
            else:
                self.disconnect()
                time.sleep(1)


    def disconnect(self):
        if self.is_connected:
            logger.info("Disconnecting from GoPro ...")
            if self.cam is not None:
                self.cam.close()
            self.cam = None
            blackboard['gopro']['state'] = 0 # GoproDisconnected
            self.is_connected = False

    def updateStatus(self):

        return True

       
        if self.cam is not None:

            if True and time.time() < self.time_since_update + 1.0:
                return True
            
            self.time_since_update = time.time()

            response = self.cam.http_command.get_camera_state()
            #raw = self.cam.getStatusRaw()

            if response.is_ok:
                # extract the data from the response
                state = response.flatten

                #self.cam_status['mode'] = self.cam.parse_value("mode", js[constants.Status.Status][constants.Status.STATUS.Mode])
                preset_group_id = state[constants.StatusId.PRESETS_GROUP]
                self.cam_status['mode'] = Params.PresetGroup(preset_group_id).name

                self.cam_status['recording'] = state[constants.StatusId.ENCODING]
                
                # check SD status
                self.cam_status['sd_card'] = (state[constants.StatusId.SD_STATUS] == Params.SDStatus.OK)
                

                #self.cam_status['lastVideo'] = self.cam.getMedia()
                #self.cam.http_command.get_media_list().flatten
                
                # parse and format datetime data
                #CURRENT_TIME_MS

                cam_time_info = self.cam.http_command.get_date_time().flatten
                # example {'date': '2021_01_14', 'time': '19_20_57'}
                self.cam_status['datetime'] = "{}, {}".format(cam_time_info['date'].replace('_','.'), cam_time_info['time'].replace('_',':'))
            
                # update video settings
                '''
                for var, val in vars(constants.Video).items():
                    if not var.startswith("_") and not inspect.isclass(val) and val in js[constants.Status.Settings]:
                        self.cam_settings[var] = (val, js[constants.Status.Settings][val])
                '''

                #print(self.cam_status, flush=True)

                return True
        
            else:
                logger.warning("Failed to get status of the gopro: %s", raw)

        return False


    def takePhoto(self):
        """ Takes a photo. """
        if self.cam_status['recording']:
            self.timestamp = time.time()
        else:
            logger.debug("Take a picture")
            if self.cam is not None:
                self.timestamp = time.time()

                #self.cam.take_photo()
                self.cam.http_command.load_preset_group(group=Params.PresetGroup.PHOTO)
                self.cam.http_command.set_shutter(shutter=Params.Toggle.ENABLE)

                # reset to video mode
                self.setCamVideoMode()

            else:
                logger.error("Not connected to cam!?")

    def handleRecording(self, previous_state):

        if self.gc_data is not None:
            # check if one team is 'invisible'
            both_teams_valid = all([t.teamNumber > 0 for t in self.gc_data.team]) or self.rec_invisible

            # game states for recording
            recording_game_state = self.gc_data.gameState in [
                GameControlData.STATE_READY, 
                GameControlData.STATE_SET,
                GameControlData.STATE_PLAYING
            ]

            # handle output
            if not self.quiet:
                output = "%s | %s | game state: %s | %s" % (
                    self.cam_status['mode'], "RECORDING!" if self.cam_status['recording'] else "Not recording", self.gc_data.getGameState(), self.gc_data.secsRemaining)
                print(output, flush=True)

            print(self.cam_status, flush=True)

            # handle game state changes
            if not self.ignore and self.gc_data.secsRemaining < -self.max_time:
                # only stop, if we're still recording
                if self.cam_status['recording']:
                    self.stopRecording()
            elif self.gc_data.gameState == GameControlData.STATE_SET and previous_state['time'] + self.max_time < time.time():
                # too long in the set state, stop recording!
                if self.cam_status['recording']:
                    logger.debug("Stopped recording because we were too long in set")
                    self.stopRecording()
            elif self.cam_status['sd_card'] and not self.cam_status['recording'] and both_teams_valid and recording_game_state:
                self.startRecording()
            elif self.cam_status['recording'] and not recording_game_state:
                self.stopRecording()

            # handle game changes
            if previous_state['game'] != self.gc_data.gameState:
                logger.debug("Changed game state to: %s @ %d", self.gc_data.getGameState(), time.time())
                previous_state['time'] = time.time()

            return self.gc_data.gameState
        else:
            if self.cam_status['recording']:
                self.stopRecording()

        return GameControlData.STATE_INITIAL


    def setCamVideoMode(self):
        logger.debug("Set GoPro to 'VIDEO' mode")
        #self.cam.mode(constants.Mode.VideoMode)
        self.cam.http_command.load_preset_group(group=Params.PresetGroup.VIDEO)
        # wait for the command to be executed
        time.sleep(0.5)

    def startRecording(self):
        print(">>>>>>>>>>>>>>>>>>>>>>>>> Start recording", flush=True)

        if self.cam_status['mode'] != "VIDEO":
            self.setCamVideoMode()
        #self.__updateUserSettings()

        logger.debug("Start recording")
        blackboard['gopro']['state'] = 4 # GoproStartRecording
        blackboard['gopro']['datetime'] = self.cam_status['datetime']
        self.cam_status['recording'] = True

        #self.cam.shutter(constants.start)
        response = self.cam.http_command.set_shutter(shutter=Params.Toggle.ENABLE)
        logger.debug(response)
        print("start recording", flush=True)


    def stopRecording(self):
        print(">>>>>>>>>>>>>>>>>>>>>>>>> Stop recording", flush=True)

        #self.cam.shutter(constants.stop)
        response = self.cam.http_command.set_shutter(shutter=Params.Toggle.DISABLE)
        logger.debug(response)

        self.updateStatus()
        time.sleep(1)  # wait for the command to be executed
        blackboard['gopro']['lastVideo'] = self.cam_status['lastVideo']
        blackboard['gopro']['state'] = 2 # GoproStopRecording
        blackboard['gopro']['datetime'] = self.cam_status['datetime']
        self.cam_status['recording'] = False

    def cancel(self):
        self.__cancel.set()

    def __updateUserSettings(self):
        logger.debug("Set user video settings")

        for s in self.user_settings:
            # is setting 'valid'
            if s in self.cam_settings:
                # is setting is set and is cam setting different from user settings?
                if self.user_settings[s] is not None and self.user_settings[s] != "" and self.cam_settings[s][1] != int(self.user_settings[s]):
                    
                    res = ""
                    # try to set the user setting on the cam
                    #res = self.cam.gpControlSet(str(self.cam_settings[s][0]), str(self.user_settings[s]))
                    #TODO
                    print("Try set user setting: {} = {}", s, self.user_settings[s], flush=True)

                    if len(res) == 0:
                        logger.warning("The following setting can not be set for this cam: '"+s+"'")
                        # remove from user settings
                        self.user_settings[s] = None
            else:
                logger.warning("Unknown video setting: '"+s+"'")

# some tests
if __name__ == '__main__':
    pass

#10.1.12.74