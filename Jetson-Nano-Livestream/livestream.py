#!/usr/bin/env python3
import threading, time, json, os
import psutil
os.environ["GST_DEBUG"] = "2"

from utils.GameController import GameController
from utils.GameControlData import GameControlData
from utils.SimpleHttpServer import SimpleHttpServer
from utils import Event, Logger

from PIL import Image, ImageDraw, ImageFont
from operator import itemgetter
import sys, os, traceback
import datetime

logger = Logger.getLogger("LiveStream")

# Required imports
# Gst, GstBase, GObject
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject

# Init Gobject Threads
# Init Gstreamer
GObject.threads_init()
Gst.init(None)

from gst_overlay.gstpipeline import GstPipeline
from gst_overlay.gst_overlay_cairo import GstOverlayCairo, from_pil

def exception_catcher(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            print("Error in " + str(func.__name__))
            traceback.print_exc(file=sys.stdout)
    return wrapper



class LiveStream(threading.Thread):
    ### (Width, Height, Mbit/s) ###
    RESOLUTIONMAP = {"480p": (854, 480, 1.25),
                     "720p": (1280, 720, 2.75),
                     "1080p": (1920, 1080, 4.5),
                     "1080p_wide": (1920, 1080, 4.5, 3280, 1848),
                     "1440p": (2560, 1440, 9.5),
                     "2160p": (3840, 2160, 23.5)}
    TEAMMAP = { 0 : "Invisibles",
                1 : "UT Austin Villa",
                2 : "Austrian Kangaroos",
                3 : "Bembelbots",
                4 : "Berlin United",
                5 : "B-Human",
                6 : "Cerberus",
                7 : "DAInamite",
                8 : "Dutch Nao Team",
                9 : "Edinferno",
                10: "Kouretes",
                11: "MiPal",
                12: "Nao Devils",
                13: "Nao-Team HTWK",
                14: "Northern Bites",
                15: "NTU RoboPAL",
                16: "RoboCanes",
                17: "RoboEireann",
                18: "rUNSWift",
                19: "SPQR Team",
                20: "TJArk",
                21: "UChile",
                22: "UPennalizers",
                23: "Crude Scientists",
                24: "HULKs",
                26: "MRL-SPL",
                27: "Philosopher",
                28: "Rimal Team",
                29: "SpelBots",
                30: "Team-NUST",
                31: "UnBeatables",
                32: "UTH-CAR",
                33: "NomadZ",
                34: "SPURT",
                35: "Blue Spider",
                36: "Camellia Dragons",
                37: "JoiTech-SPL",
                38: "Linkoeping Humanoids",
                39: "WrightOcean",
                40: "Mars",
                41: "Aztlan",
                42: "CMSingle",
                43: "TeamSP",
                44: "Luxembourg United",
                45: "Naova ETS",
                46: "Recife Soccer",
                47: "Rinobot",
                48: "Starkit",
                49: "SABANA Herons",
                90: "Devil SMASH",
                91: "B&B",
                92: "SwiftArk",
                93: "SPQR-Starkit",
                96: "Team-Team",
               }
    COLORMAP = {0: (205, 0, 0, 255),
                1: (0, 0, 255, 255),
                2: (0, 215, 255, 255),
                3: (0, 0, 0, 255),
                4: (255, 255, 255, 255),
                5: (50, 205, 50, 255),
                6: (0, 140, 255, 255),
                7: (128, 0, 128, 255),
                8: (19, 69, 139, 255),
                9: (169, 169, 169, 255),
                }

    OPACITY = 192
    BLUE = (205, 0, 0, OPACITY)
    RED = (0, 0, 255, OPACITY)
    YELLOW = (0, 215, 255, OPACITY)
    BLACK = (0, 0, 0, OPACITY)
    WHITE = (255, 255, 255, OPACITY)
    GREEN = (50, 205, 50, OPACITY)
    ORANGE = (0, 140, 255, OPACITY)
    PURPLE = (128, 0, 128, OPACITY)
    BROWN = (19, 69, 139, OPACITY)
    GRAY = (169, 169, 169, OPACITY)
    COLORMAPTEXT = {0:  (255, 255, 255, 255),
                    1:  (255, 255, 255, 255),
                    2:  (0, 0, 0, 255),
                    3:  (255, 255, 255, 255),
                    4:  (0, 0, 0, 255),
                    5:  (255, 255, 255, 255),
                    6:  (255, 255, 255, 255),
                    7:  (255, 255, 255, 255),
                    8:  (255, 255, 255, 255),
                    9:  (255, 255, 255, 255),
                    }

    TESTING = False
    RESOLUTION = "1440p"
    WIDTH = RESOLUTIONMAP[RESOLUTION][0]
    HEIGHT = RESOLUTIONMAP[RESOLUTION][1]
    CAMERAWIDTH = WIDTH if len(RESOLUTIONMAP[RESOLUTION]) == 3 else RESOLUTIONMAP[RESOLUTION][3]
    CAMERAHEIGHT = HEIGHT if len(RESOLUTIONMAP[RESOLUTION]) == 3 else RESOLUTIONMAP[RESOLUTION][4]
    FRAMERATE = 25
    BITRATE = int(RESOLUTIONMAP[RESOLUTION][2] * 1000 * 1000)

    OVERLAY_PLUGIN_NAME = "overlay"
    CAMERA_PLUGIN_NAME = "nvarguscamerasrc0"
    AUDIO_PLUGIN_NAME = "audiowsincband0"
    UDP_PORT = 5000
    UDP_IP = "192.168.31.2"

    YOUTUBE_ID = "xxxx-xxxx-xxxx-xxxx"
    YOUTUBE_ID2 = None

    def __init__(self):
        self.gst_command = 'nvarguscamerasrc wbmode=5 awblock=false aeantibanding=2 silent=true name={} '.format(self.CAMERA_PLUGIN_NAME)
        self.gst_command += '! capsfilter caps="video/x-raw(memory:NVMM), width=(int){}, height=(int){}, format=(string)NV12, framerate=(fraction){}/1" '.format(self.CAMERAWIDTH, self.CAMERAHEIGHT, self.FRAMERATE)
        self.gst_command += '! nvvidconv '
        self.gst_command += '! capsfilter caps="video/x-raw, width=(int){}, height=(int){}, format=(string)RGBA, framerate=(fraction){}/1" '.format(self.WIDTH, self.HEIGHT, self.FRAMERATE)
        self.gst_command += '! gstoverlaycairo name={} '.format(self.OVERLAY_PLUGIN_NAME)
        self.gst_command += '! nvvidconv '
        self.gst_command += '! capsfilter caps="video/x-raw(memory:NVMM), width=(int){}, height=(int){}, format=(string)NV12, framerate=(fraction){}/1" '.format(self.WIDTH, self.HEIGHT, self.FRAMERATE)
        self.gst_command += '! omxh264enc bitrate={} control-rate=variable '.format(self.BITRATE)
        self.gst_command += '! tee name=videotee '

        self.gst_command += 'alsasrc device=hw:2 '
        self.gst_command += '! audioconvert '
        #self.gst_command += '! audiochebband mode=band-pass lower-frequency=1200 upper-frequency=3000 type=2 '
        self.gst_command += '! audiowsincband mode=band-pass lower-frequency=200 upper-frequency=12000 length=101 window=blackman '
        self.gst_command += '! audioamplify amplification=2.5 clipping-method=wrap-positive '
        self.gst_command += '! audioconvert noise-shaping=4 '
        self.gst_command += '! audioresample '
        self.gst_command += '! capsfilter caps="audio/x-raw,rate=48000" '
        self.gst_command += '! voaacenc bitrate=128000 '
        self.gst_command += '! tee name=audiotee '

        self.gst_command += 'flvmux name=flvMux '
        self.gst_command += '! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/{}" '.format(self.YOUTUBE_ID)
        if self.YOUTUBE_ID2:
            self.gst_command += 'flvmux name=flvMux2 '
            self.gst_command += '! rtmpsink location="rtmp://a.rtmp.youtube.com/live2/{}" '.format(self.YOUTUBE_ID2)
        self.gst_command += 'mpegtsmux name=mp2tMux alignment=7 '
        self.gst_command += '! rtpmp2tpay '
        self.gst_command += '! udpsink host={} port={} '.format(self.UDP_IP, self.UDP_PORT)

        self.gst_command += 'audiotee. ! queue ! aacparse ! flvMux. '
        if self.YOUTUBE_ID2:
            self.gst_command += 'audiotee. ! queue ! aacparse ! flvMux2. '
        self.gst_command += 'audiotee. ! queue ! aacparse ! mp2tMux. '

        self.gst_command += 'videotee. ! queue ! h264parse config-interval=-1 ! flvMux. '
        if self.YOUTUBE_ID2:
            self.gst_command += 'videotee. ! queue ! h264parse config-interval=-1 ! flvMux2. '
        self.gst_command += 'videotee. ! queue ! h264parse config-interval=-1 ! mp2tMux.'

        print("Pipeline: " + str(self.gst_command))
        self.pipeline = GstPipeline(self.gst_command)

        self.img = Image.new('RGBA', (self.WIDTH, self.HEIGHT))
        ret, self.overlay_element = self.pipeline.get_element(self.OVERLAY_PLUGIN_NAME)
        assert ret, "Can't get GstOverlay Element"
        self.overlay_element.overlay = from_pil(self.img)

        self.overlay_lock = threading.Lock()

        self.heightFactor = self.HEIGHT / 1080.0
        self.widthFactor = self.WIDTH / 1920.0

        self.upperLineTopY = int(970 * self.heightFactor)
        self.middleX = int(960 * self.widthFactor)

        self.leftPenaltyX = int(120 * self.widthFactor)
        self.rightPenaltyX = self.WIDTH - self.leftPenaltyX
        self.penaltyBottomY = int(1030 * self.heightFactor)

        self.fontThin = ImageFont.truetype("/home/arne/Livestream/fonts/apexnew-book-opentype.otf", int(40 * max(self.heightFactor, self.widthFactor)))
        self.fontThinSmall = ImageFont.truetype("/home/arne/Livestream/fonts/apexnew-book-opentype.otf", int(20 * max(self.heightFactor, self.widthFactor)))
        self.fontBold = ImageFont.truetype("/home/arne/Livestream/fonts/apexnew-medium-opentype.otf", int(40 * max(self.heightFactor, self.widthFactor)))
        self.maxFontHeight = max(self.fontThin.getsize("89")[1], self.fontBold.getsize("89")[1])

        self.settings = {}
        self.live_text = ""
        self.lastUploadedBytes = 0
        self.loadSettings()

        super(LiveStream, self).__init__()

        # GAMECONTROLLER:
        Event.registerListener(self)
        self.gc_data = GameControlData()
        self.__cancel = threading.Event()

    @exception_catcher
    def loadSettings(self):
        with open('settings.txt') as json_file:
            self.settings = json.load(json_file)

    @exception_catcher
    def saveSettings(self):
        with open('settings.txt', 'w') as json_file:
            json.dump(self.settings, json_file, sort_keys=True, indent=4)

    @exception_catcher
    def checkUpload(self):
        counter = 0
        while True:
            upload_traffic = psutil.net_io_counters(pernic=True)["eth0"].bytes_sent
            diff = upload_traffic - self.lastUploadedBytes
            logger.warning("Uploaded " + str(upload_traffic/1024.0/1024.0) + " Mbyte")
            logger.warning("Diff: " + str(diff / 1024.0 / 1024.0) + " Mbyte -> Min: " + str(self.BITRATE/8.0/1024.0/1024.0/10.0))

            if diff > (self.BITRATE/8.0/10.0) or self.lastUploadedBytes == 0:
                self.lastUploadedBytes = upload_traffic
                return True
            else:
                self.lastUploadedBytes = upload_traffic
                if counter > 5:
                    logger.warning("Upload not working!")
                    return False
                else:
                    counter += 1
                    time.sleep(1)

    @exception_catcher
    def startPipeline(self):
        counter = 0
        while self.pipeline.get_state() != Gst.State.PLAYING:
            logger.warning("Pipeline Offline! Restarting...")
            self.pipeline.start()
            time.sleep(2)
            if counter < 20:
                counter += 1
            else:
                self.stop()
                exit(-1)

    @exception_catcher
    def run(self):
        try:
            # Start pipeline
            self.pipeline.start()
            time.sleep(2)
            self.startPipeline()

            self.updateSettings()
            while not self.__cancel.is_set():
                if not self.checkUpload():
                    self.stop()
                    exit(-1)

                if self.pipeline.get_state() != Gst.State.PLAYING:
                    self.startPipeline()

                start = datetime.datetime.now()
                with self.overlay_lock:
                    if not self.gc_data and not self.TESTING:
                        self.img = Image.new('RGBA', (self.WIDTH, self.HEIGHT))
                        draw = ImageDraw.Draw(self.img)

                        ##############################
                        ### Actual Time -> TopRight ###
                        ##############################
                        marginTime = 20 * self.heightFactor
                        actualTime = self.timeToString()
                        text_size = self.fontThin.getsize(actualTime)
                        actualTimeRightX = self.WIDTH - (5 * self.widthFactor)
                        actualTimeLeftX = actualTimeRightX - (text_size[0] + marginTime)
                        actualTimeTopY = 5 * self.heightFactor
                        actualTimeBottomY = actualTimeTopY + self.maxFontHeight + marginTime
                        draw.font = self.fontThin
                        draw.rectangle([(actualTimeLeftX, actualTimeTopY), (actualTimeRightX, actualTimeBottomY)], fill=self.WHITE, outline=self.WHITE)
                        draw.text((actualTimeLeftX + marginTime / 2, actualTimeTopY + marginTime / 2), actualTime, fill=self.BLACK)

                        #############################
                        ### Live Text -> TopLeft ###
                        #############################
                        if self.live_text != "":
                            marginLiveText = 20 * self.heightFactor
                            text_size = self.fontThin.getsize(self.live_text)
                            liveTextLeftX = marginLiveText
                            liveTextRightX = liveTextLeftX + (text_size[0] + marginLiveText)
                            liveTextTopY = 5 * self.heightFactor
                            liveTextBottomY = liveTextTopY + self.maxFontHeight + marginLiveText
                            draw.font = self.fontThin
                            draw.rectangle([(liveTextLeftX, liveTextTopY), (liveTextRightX, liveTextBottomY)], fill=self.WHITE, outline=self.WHITE)
                            draw.text((liveTextLeftX + marginLiveText / 2, liveTextTopY + marginLiveText / 2), self.live_text, fill=self.BLACK)

                if self.TESTING:
                    self.receivedGC(Event.GameControllerMessage(GameControlData(testing=True)))

                self.overlay_element.overlay = from_pil(self.img)

                end = datetime.datetime.now()
                time.sleep(max(0.0, 1.0 - (end-start).total_seconds()))

            self.pipeline.stop()
        except Exception as e:
            logger.warning("Camera broke!")
            print("-" * 60)
            logger.warning(str(e))
            traceback.print_exc(file=sys.stdout)
            print("-" * 60)

    def timeoutGC(self, evt: Event.GameControllerTimedout):
        """ Is called, when a new GameController times out. """
        #self.set_annotation_text(self.timeToString())
        if not self.TESTING:
            self.gc_data = None

    def secsToString(self, secs):
        m, s = divmod(abs(secs), 60)
        if secs < 0:
            return "-%02d:%02d" % (m, s)
        else:
            return "%02d:%02d" % (m, s)

    def timeToString(self):
        #return time.strftime("%H:%M:%S", time.localtime())
        return format(datetime.datetime.now() + datetime.timedelta(hours=8), '%H:%M:%S')

    def receivedSettings(self, evt: Event.SettingsMessage):
        print("In livestream.py: " + str(evt.settings))
        self.settings.update(evt.settings)
        self.saveSettings()
        self.updateSettings()

    @exception_catcher
    def updateSettings(self):
        if "live_text" in self.settings:
            self.live_text = str(self.settings["live_text"][0])
            self.live_text = self.live_text.replace("\"", "")
            print("Set live_text to: " + self.live_text)

        self.setGStreamerSettingINT(self.CAMERA_PLUGIN_NAME, "wbmode", (0, 1, 9))
        self.setGStreamerSettingINT(self.CAMERA_PLUGIN_NAME, "aeantibanding", (0, 1, 3))
        self.setGStreamerSettingFLOAT(self.CAMERA_PLUGIN_NAME, "saturation", (0.0, 1.0, 2.0))
        self.setGStreamerSettingINT(self.CAMERA_PLUGIN_NAME, "tnr-mode", (0, 1, 2))
        self.setGStreamerSettingFLOAT(self.CAMERA_PLUGIN_NAME, "tnr-strength", (-1.0, -1.0, 1.0))
        self.setGStreamerSettingINT(self.CAMERA_PLUGIN_NAME, "ee-mode", (0, 1, 2))
        self.setGStreamerSettingFLOAT(self.CAMERA_PLUGIN_NAME, "ee-strength", (-1.0, -1.0, 1.0))
        self.setGStreamerSettingFLOAT(self.CAMERA_PLUGIN_NAME, "exposurecompensation", (-2.0, 0.0, 2.0))
        self.setGStreamerSettingINT(self.CAMERA_PLUGIN_NAME, "aelock", (0, 0, 1))
        self.setGStreamerSettingINT(self.CAMERA_PLUGIN_NAME, "awblock", (0, 0, 1))
        self.setGStreamerSettingINT(self.CAMERA_PLUGIN_NAME, "maxperf", (0, 0, 1))
        self.setGStreamerSettingSTRING(self.CAMERA_PLUGIN_NAME, "exposuretimerange")
        self.setGStreamerSettingSTRING(self.CAMERA_PLUGIN_NAME, "gainrange")
        self.setGStreamerSettingSTRING(self.CAMERA_PLUGIN_NAME, "ispdigitalgainrange")

        self.setGStreamerSettingINT(self.AUDIO_PLUGIN_NAME, "length", (11, 101, 501))
        self.setGStreamerSettingINT(self.AUDIO_PLUGIN_NAME, "lower-frequency", (0, 300, 20000))
        self.setGStreamerSettingINT(self.AUDIO_PLUGIN_NAME, "upper-frequency", (0, 9000, 20000))

    def setGStreamerSettingINT(self, element, setting, minDefaultMax):
        if setting in self.settings:
            temp = int(self.settings[setting][0])
            self.setGStreamerSetting(element, setting, temp, minDefaultMax)

    def setGStreamerSettingFLOAT(self, element, setting, minDefaultMax):
        if setting in self.settings:
            temp = float(self.settings[setting][0])
            self.setGStreamerSetting(element, setting, temp, minDefaultMax)

    def setGStreamerSettingSTRING(self, element, setting):
        if setting in self.settings:
            temp = str(self.settings[setting][0])
            self.setGStreamerSetting(element, setting, temp, None)

    @exception_catcher
    def setGStreamerSetting(self, element, setting, value, minDefaultMax=None):
        ret, gstreamer_element = self.pipeline.get_element(element)
        if ret:
            local_value = value
            if minDefaultMax:
                if not minDefaultMax[0] <= local_value <= minDefaultMax[2]:
                    local_value = minDefaultMax[1]
            print("Set {} to: {}".format(str(setting), str(local_value)))
            gstreamer_element.set_property(str(setting), local_value)

    def receivedGC(self, evt: Event.GameControllerMessage):
        """ Is called, when a new GameController message was received. """
        self.gc_data = evt.message
        try:
            with self.overlay_lock:
                self.img = Image.new('RGBA', (self.WIDTH, self.HEIGHT))
                draw = ImageDraw.Draw(self.img)

                ##############################
                ### Actual Time -> TopLeft ###
                ##############################
                marginTime = 20 * self.heightFactor
                actualTime = self.timeToString()
                text_size = self.fontThin.getsize(actualTime)
                actualTimeRightX = self.WIDTH - (5 * self.widthFactor)
                actualTimeLeftX = actualTimeRightX - (text_size[0] + marginTime)
                actualTimeTopY = 5 * self.heightFactor
                actualTimeBottomY = actualTimeTopY + self.maxFontHeight + marginTime
                draw.font = self.fontThin
                draw.rectangle([(actualTimeLeftX, actualTimeTopY), (actualTimeRightX, actualTimeBottomY)], fill=self.WHITE, outline=self.WHITE)
                draw.text((actualTimeLeftX + marginTime / 2, actualTimeTopY + marginTime / 2), actualTime, fill=self.BLACK)

                #############################
                ### Live Text -> TopLeft ###
                #############################
                if self.live_text != "":
                    marginLiveText = 20 * self.heightFactor
                    text_size = self.fontThin.getsize(self.live_text)
                    liveTextLeftX = marginLiveText
                    liveTextRightX = liveTextLeftX + (text_size[0] + marginLiveText)
                    liveTextTopY = 5 * self.heightFactor
                    liveTextBottomY = liveTextTopY + self.maxFontHeight + marginLiveText
                    draw.font = self.fontThin
                    draw.rectangle([(liveTextLeftX, liveTextTopY), (liveTextRightX, liveTextBottomY)], fill=self.WHITE,
                                   outline=self.WHITE)
                    draw.text((liveTextLeftX + marginLiveText / 2, liveTextTopY + marginLiveText / 2), self.live_text,
                              fill=self.BLACK)

                ######################################
                ### Game TimeStamp -> BottomMiddle ###
                ######################################
                marginTimeStamp = 20 * self.heightFactor
                timeStamp = self.secsToString(self.gc_data.secsRemaining)
                text_size = self.fontThin.getsize("89:89")
                timeStampLeftX = self.middleX - ((text_size[0] / 2) + marginTimeStamp / 2)
                timeStampRightX = self.middleX + ((text_size[0] / 2) + marginTimeStamp / 2)
                timeStampBottomY = self.upperLineTopY + self.maxFontHeight + marginTimeStamp
                draw.font = self.fontThin
                draw.rectangle([(timeStampLeftX, self.upperLineTopY), (timeStampRightX, timeStampBottomY)], fill=self.WHITE, outline=self.WHITE)
                draw.text((timeStampLeftX + marginTimeStamp / 2, self.upperLineTopY + marginTimeStamp / 2), timeStamp, fill=self.BLACK)

                ##############
                ### Scores ###
                ##############
                marginScore = 10 * self.heightFactor
                leftScore = str(self.gc_data.team[0].score)
                text_size = self.fontBold.getsize(leftScore)
                leftScoreLeftX = timeStampLeftX - (text_size[0] + marginScore)
                leftScoreRightX = timeStampLeftX
                leftScoreBottomY = timeStampBottomY
                draw.font = self.fontBold
                draw.rectangle([(leftScoreLeftX, self.upperLineTopY), (leftScoreRightX, leftScoreBottomY)], fill=self.RED, outline=self.RED)
                draw.text((leftScoreLeftX + marginScore / 2 + 1, self.upperLineTopY + marginTimeStamp / 2 - 1), leftScore, fill=self.WHITE)

                rightScore = str(self.gc_data.team[1].score)
                text_size = self.fontBold.getsize(rightScore)
                rightScoreLeftX = timeStampRightX
                rightScoreRightX = timeStampRightX + (text_size[0] + marginScore)
                rightScoreBottomY = timeStampBottomY
                draw.font = self.fontBold
                draw.rectangle([(rightScoreLeftX, self.upperLineTopY), (rightScoreRightX, rightScoreBottomY)], fill=self.RED, outline=self.RED)
                draw.text((rightScoreLeftX + marginScore / 2 + 1, self.upperLineTopY + marginTimeStamp / 2 - 1), rightScore, fill=self.WHITE)

                ##################
                ### Team Names ###
                ##################
                variant = 2
                # 0 = Boxes in the size of the Text,
                # 1 = Boxes in the size of the longest Text,
                # 2 = Boxes as in 1, Text is centered

                marginTeam = 20 * self.heightFactor
                leftTeam = self.TEAMMAP[self.gc_data.team[0].teamNumber]
                text_size_left = self.fontThin.getsize(leftTeam)
                rightTeam = self.TEAMMAP[self.gc_data.team[1].teamNumber]
                text_size_right = self.fontBold.getsize(rightTeam)

                text_size = (max(text_size_left[0], text_size_right[0]), max(text_size_left[1], text_size_right[1]))
                if variant == 0:
                    leftTeamLeftX = leftScoreLeftX - (text_size_left[0] + marginTeam)
                else:
                    leftTeamLeftX = leftScoreLeftX - (text_size[0] + marginTeam)
                leftTeamRightX = leftScoreLeftX
                leftTeamBottomY = timeStampBottomY
                draw.font = self.fontThin
                draw.rectangle([(leftTeamLeftX, self.upperLineTopY), (leftTeamRightX, leftTeamBottomY)], fill=self.WHITE, outline=self.WHITE)
                if variant == 2:
                    draw.text((leftTeamLeftX + (text_size[0] / 2 + marginTeam / 2) - text_size_left[0] / 2, self.upperLineTopY + marginTimeStamp / 2), leftTeam, fill=self.BLACK)
                else:
                    draw.text((leftTeamRightX - marginTeam / 2 - text_size_left[0], self.upperLineTopY + marginTimeStamp / 2), leftTeam, fill=self.BLACK)

                rightTeamLeftX = rightScoreRightX
                if variant == 0:
                    rightTeamRightX = rightScoreRightX + (text_size_right[0] + marginTeam)
                else:
                    rightTeamRightX = rightScoreRightX + (text_size[0] + marginTeam)
                rightTeamBottomY = timeStampBottomY
                draw.font = self.fontThin
                draw.rectangle([(rightTeamLeftX, self.upperLineTopY), (rightTeamRightX, rightTeamBottomY)], fill=self.WHITE, outline=self.WHITE)
                if variant == 2:
                    draw.text((rightTeamLeftX + (text_size[0] / 2 + marginTeam / 2) - text_size_right[0] / 2, self.upperLineTopY + marginTimeStamp / 2), rightTeam, fill=self.BLACK)
                else:
                    draw.text((rightTeamLeftX + marginTeam / 2, self.upperLineTopY + marginTimeStamp / 2), rightTeam, fill=self.BLACK)

                ##################
                ### Team Color ###
                ##################
                sizeTeamColorX = (timeStampBottomY - self.upperLineTopY) * 2 / 3
                leftTeamColorLeftX = leftTeamLeftX - sizeTeamColorX
                leftTeamColorRightX = leftTeamLeftX
                leftTeamColorBottomY = timeStampBottomY
                draw.rectangle([(leftTeamColorLeftX, self.upperLineTopY), (leftTeamColorRightX, leftTeamColorBottomY)], fill=self.COLORMAP[self.gc_data.team[0].teamColour], outline=self.COLORMAP[self.gc_data.team[0].teamColour])

                rightTeamColorLeftX = rightTeamRightX
                rightTeamColorRightX = rightTeamRightX + sizeTeamColorX
                rightTeamColorBottomY = timeStampBottomY
                draw.rectangle([(rightTeamColorLeftX, self.upperLineTopY), (rightTeamColorRightX, rightTeamColorBottomY)], fill=self.COLORMAP[self.gc_data.team[1].teamColour], outline=self.COLORMAP[self.gc_data.team[1].teamColour])

                ###################################
                ### Game Status -> BottomMiddle ###
                ###################################
                marginStatus = 10 * self.heightFactor
                status = ""

                if self.gc_data.getGamePhase() != "normal":
                    status = str(self.gc_data.getGamePhase()) + " " + self.secsToString(self.gc_data.secondaryTime)
                elif (self.gc_data.firstHalf and self.gc_data.getGameState() == "finished") or (not self.gc_data.firstHalf and self.gc_data.getGameState() == "initial") and self.gc_data.secondaryTime > 0:
                    status += "half time - " + self.secsToString(self.gc_data.secondaryTime)
                else:
                    if self.gc_data.secondaryTime > 0 and not self.gc_data.getGameState() == "initial" and not self.gc_data.getGameState() == "finished":
                        if self.gc_data.getGameState() == "ready":
                            status = str(self.gc_data.getGameState())
                        else:
                            status = str(self.gc_data.getSetPlay())
                        status += " - " + self.secsToString(self.gc_data.secondaryTime)
                    else:
                        status = str(self.gc_data.getGameState())

                text_size = self.fontThin.getsize(status)
                statusLeftX = self.middleX - ((text_size[0] / 2) + marginStatus / 2)
                statusRightX = self.middleX + ((text_size[0] / 2) + marginStatus / 2)
                statusTopY = timeStampBottomY + (5 * self.heightFactor)
                statusBottomY = statusTopY + (self.maxFontHeight + marginStatus)
                draw.font = self.fontThin
                draw.rectangle([(statusLeftX, statusTopY), (statusRightX, statusBottomY)], fill=self.WHITE, outline=self.WHITE)
                draw.text((statusLeftX + marginStatus / 2, statusTopY + marginStatus / 2), status, fill=self.BLACK)

                ######################################
                ### Which Halftime -> BottomMiddle ###
                ######################################
                marginHalftime = 5 * self.heightFactor
                if self.gc_data.firstHalf:
                    halftime = "1st"
                else:
                    halftime = "2nd"
                text_size = self.fontThin.getsize(halftime)
                halftimeLeftX = self.middleX - ((text_size[0] / 2) + marginHalftime / 2)
                halftimeRightX = self.middleX + ((text_size[0] / 2) + marginHalftime / 2)
                halftimeBottomY = self.upperLineTopY + marginHalftime
                halftimeTopY = halftimeBottomY - (text_size[1] + marginHalftime)
                draw.font = self.fontThin
                draw.rectangle([(halftimeLeftX, halftimeTopY), (halftimeRightX, halftimeBottomY)], fill=self.WHITE, outline=self.WHITE)
                draw.text((halftimeLeftX + marginHalftime / 2, halftimeTopY + marginHalftime / 2), halftime, fill=self.BLACK)

                #################################
                ### PenaltyLeft -> BottomLeft ###
                #################################
                marginPenalty = 10 * self.heightFactor
                marginReason = 5 * self.heightFactor

                penaltyListLeft = []
                penaltyListRight = []

                for id in range(2):
                    for i, player in enumerate(self.gc_data.team[id].player):
                        if player.getPenalty() != "none" and player.getPenalty() != "substitute":
                            if id == 0:
                                penaltyListLeft.append([i+1, player.getPenalty(), player.secsTillUnpenalised])
                            else:
                                penaltyListRight.append([i + 1, player.getPenalty(), player.secsTillUnpenalised])

                penaltyListLeft = sorted(penaltyListLeft, key=itemgetter(2), reverse=True)
                penaltyListRight = sorted(penaltyListRight, key=itemgetter(2), reverse=True)

                text_size_number = self.fontBold.getsize("5")
                text_size_secs = self.fontThin.getsize("89:89")
                text_size_penalty = self.fontThinSmall.getsize("playing with hands")

                for i, penalty in enumerate(penaltyListLeft):
                    # Draw Player Number
                    text_size = text_size_number
                    penaltyNumberLeftX = self.leftPenaltyX
                    penaltyNumberRightX = penaltyNumberLeftX + (text_size[0] + marginPenalty)
                    penaltyNumberBottomY = self.penaltyBottomY - i * (self.maxFontHeight + marginPenalty + text_size_penalty[1] + marginReason)
                    penaltyNumberTopY = penaltyNumberBottomY - self.maxFontHeight - marginPenalty
                    draw.font = self.fontBold
                    draw.rectangle([(penaltyNumberLeftX, penaltyNumberTopY), (penaltyNumberRightX, penaltyNumberBottomY)], fill=self.COLORMAP[self.gc_data.team[0].teamColour], outline=self.COLORMAP[self.gc_data.team[0].teamColour])
                    draw.text((penaltyNumberLeftX + marginPenalty / 2 + 1, penaltyNumberTopY + marginPenalty / 2), str(penalty[0]), fill=self.COLORMAPTEXT[self.gc_data.team[0].teamColour])

                    # Draw SecsTillUnpenalised
                    text_size = text_size_secs
                    penaltySecsLeftX = penaltyNumberRightX
                    penaltySecsRightX = penaltySecsLeftX + (text_size[0] + marginPenalty)
                    penaltySecsBottomY = penaltyNumberBottomY
                    penaltySecsTopY = penaltyNumberTopY
                    draw.font = self.fontThin
                    draw.rectangle([(penaltySecsLeftX, penaltySecsTopY), (penaltySecsRightX, penaltySecsBottomY)], fill=self.WHITE,
                                   outline=self.WHITE)
                    draw.text((penaltySecsLeftX + marginPenalty / 2 + 1, penaltySecsTopY + marginPenalty / 2), self.secsToString(penalty[2]), fill=self.BLACK)

                    # Draw PenaltyReason
                    text_size = self.fontThinSmall.getsize(str(penalty[1]))
                    penaltyReasonLeftX = penaltyNumberLeftX
                    penaltyReasonRightX = penaltyReasonLeftX + (text_size[0] + marginReason)
                    penaltyReasonTopY = penaltyNumberBottomY
                    penaltyReasonBottomY = penaltyReasonTopY + (text_size_penalty[1] + marginReason)
                    draw.font = self.fontThinSmall
                    draw.rectangle([(penaltyReasonLeftX, penaltyReasonTopY), (penaltyReasonRightX, penaltyReasonBottomY)], fill=self.WHITE, outline=self.WHITE)
                    draw.text((penaltyReasonLeftX + marginReason / 2 + 1, penaltyReasonTopY + marginReason / 2), str(penalty[1]), fill=self.BLACK)

                for i, penalty in enumerate(penaltyListRight):
                    # Draw Player Number
                    text_size = text_size_number
                    penaltyNumberRightX = self.rightPenaltyX
                    penaltyNumberLeftX = penaltyNumberRightX - (text_size[0] + marginPenalty)
                    penaltyNumberBottomY = self.penaltyBottomY - i * (self.maxFontHeight + marginPenalty + text_size_penalty[1] + marginReason)
                    penaltyNumberTopY = penaltyNumberBottomY - self.maxFontHeight - marginPenalty
                    draw.font = self.fontBold
                    draw.rectangle([(penaltyNumberLeftX, penaltyNumberTopY), (penaltyNumberRightX, penaltyNumberBottomY)], fill=self.COLORMAP[self.gc_data.team[1].teamColour], outline=self.COLORMAP[self.gc_data.team[1].teamColour])
                    draw.text((penaltyNumberLeftX + marginPenalty / 2 + 1, penaltyNumberTopY + marginPenalty / 2), str(penalty[0]), fill=self.COLORMAPTEXT[self.gc_data.team[1].teamColour])

                    # Draw SecsTillUnpenalised
                    text_size = text_size_secs
                    penaltySecsRightX = penaltyNumberLeftX
                    penaltySecsLeftX = penaltySecsRightX - (text_size[0] + marginPenalty)
                    penaltySecsBottomY = penaltyNumberBottomY
                    penaltySecsTopY = penaltyNumberTopY
                    draw.font = self.fontThin
                    draw.rectangle([(penaltySecsLeftX, penaltySecsTopY), (penaltySecsRightX, penaltySecsBottomY)], fill=self.WHITE, outline=self.WHITE)
                    draw.text((penaltySecsLeftX + marginPenalty / 2 + 1, penaltySecsTopY + marginPenalty / 2), self.secsToString(penalty[2]), fill=self.BLACK)

                    # Draw PenaltyReason
                    text_size = self.fontThinSmall.getsize(str(penalty[1]))
                    penaltyReasonRightX = penaltyNumberRightX
                    penaltyReasonLeftX = penaltyReasonRightX - (text_size[0] + marginPenalty)
                    penaltyReasonTopY = penaltyNumberBottomY
                    penaltyReasonBottomY = penaltyReasonTopY + (text_size_penalty[1] + marginReason)
                    draw.font = self.fontThinSmall
                    draw.rectangle([(penaltyReasonLeftX, penaltyReasonTopY), (penaltyReasonRightX, penaltyReasonBottomY)], fill=self.WHITE, outline=self.WHITE)
                    draw.text((penaltyReasonLeftX + marginReason / 2 + 1, penaltyReasonTopY + marginReason / 2), str(penalty[1]), fill=self.BLACK)

        except Exception as e:
            logger.warning("Annotation error: " + str(e))

    def stop(self):
        self.__cancel.set()

stream = LiveStream()
#stream.setDaemon(True)
gc = GameController()
server = SimpleHttpServer('', 8080)

try:
    gc.start()
    stream.start()
    server.start()
    while True:
        time.sleep(1)
        if not stream.is_alive():
            gc.cancel()
            stream.stop()
            gc.join(timeout=5)
            stream.join(timeout=5)
            server.stop()
            break

except Exception as e:
    str(e)
    gc.cancel()
    stream.stop()
    gc.join(timeout=5)
    stream.join(timeout=5)
    server.stop()
