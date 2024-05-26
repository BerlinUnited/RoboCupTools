import asyncio
import datetime
import inspect
import json
import logging
import re
import shutil
import subprocess
import threading
from abc import ABCMeta, abstractmethod
from enum import Enum

import zmq
from bleak import BLEDevice, AdvertisementData, BleakScanner, BleakClient
from bleak.exc import BleakDeviceNotFoundError, BleakError
from goprocam import GoProCamera, constants

from services import Messages
from services.gopro.GoPro import GoPro
from utils.BiDict import BiDict


class GoProCam(GoPro):
    """Using the 'GoPro API for Python' to communicate with the GoPro: https://github.com/KonradIT/gopro-py-api"""

    RES_MAPPING = BiDict({
        GoPro.Settings.Resolution.R_4K: constants.Video.Resolution.R4kSV,
        GoPro.Settings.Resolution.R_2K: constants.Video.Resolution.R2kSV,
        GoPro.Settings.Resolution.R_1440P: constants.Video.Resolution.R1440p,
        GoPro.Settings.Resolution.R_1080P: constants.Video.Resolution.R1080p,
        GoPro.Settings.Resolution.R_960P: constants.Video.Resolution.R960p,
        GoPro.Settings.Resolution.R_720P: constants.Video.Resolution.R720p,
        GoPro.Settings.Resolution.R_480P: constants.Video.Resolution.R480p,
    })

    FPS_MAPPING = BiDict({
        GoPro.Settings.FrameRate.FR_24: constants.Video.FrameRate.FR24,
        GoPro.Settings.FrameRate.FR_25: constants.Video.FrameRate.FR25,
        GoPro.Settings.FrameRate.FR_30: constants.Video.FrameRate.FR30,
        GoPro.Settings.FrameRate.FR_50: constants.Video.FrameRate.FR50,
        GoPro.Settings.FrameRate.FR_60: constants.Video.FrameRate.FR60,
        GoPro.Settings.FrameRate.FR_100: constants.Video.FrameRate.FR100,
        GoPro.Settings.FrameRate.FR_120: constants.Video.FrameRate.FR120,
        GoPro.Settings.FrameRate.FR_240: constants.Video.FrameRate.FR240,
    })

    FOV_MAPPING = BiDict({
        GoPro.Settings.Fov.LINEAR: constants.Video.Fov.Linear,
        GoPro.Settings.Fov.NARROW: constants.Video.Fov.Narrow,
        GoPro.Settings.Fov.MEDIUM: constants.Video.Fov.Medium,
        GoPro.Settings.Fov.WIDE: constants.Video.Fov.Wide,
        GoPro.Settings.Fov.SV: constants.Video.Fov.SuperView,
    })

    def __init__(self,
                 context: zmq.Context,
                 mq_send: int,
                 mq_recv: int,
                 device: str,
                 ssid: str,
                 passwd: str,
                 ble_mac: str,
                 quiet: bool,
                 ignore: bool,
                 max_time: int,
                 rec_invisible: bool = False,
                 update_interval: float = 0.5,
                 logger: logging.Logger = None):

        super().__init__(context, mq_send, mq_recv, quiet, ignore, max_time, rec_invisible, update_interval, logger)

        self.__network = Network(device, ssid, passwd, ble_mac, logger=self._logger)

        self.__cam: GoProCamera.GoPro | None = None
        self.__cam_info = {}
        self.__cam_status = {}
        self.__cam_settings = {}

    def run(self):
        self.__network.start()
        super().run()
        self.__network.cancel()

    def _connect(self) -> bool:
        self._logger.info('Wait till GoPro is available')
        self._update(state=Messages.GoProStatus.State.DISCONNECTED)
        self.__network.gopro_available.wait()

        self._logger.info("Connecting to GoPro ...")
        self._update(state=Messages.GoProStatus.State.CONNECTING)

        self._logger.info('Wait till GoPro is connecting')
        self.__network.gopro_connecting.wait()

        self._logger.info('Wait till GoPro is connected')
        self.__network.gopro_connected.wait()

        if self.__cam is None:
            self.__cam = GoProCamera.GoPro()

        # keep the GoPro alive forever (see comments in "_keep_alive()") ...
        self.__cam.livestream('start')
        self.__cam.livestream('stop')

        return True

    @property
    def is_connected(self):
        return self.__network.gopro_connected.is_set() and super().is_connected

    def _unset(self):
        self.__cam = None

    def _keep_alive(self):
        """Keep the GoPro and its Wi-fi alive.

        What worked is to enable the livestream once, see above in "_init()"!
        (https://github.com/KonradIT/goprowifihack/issues/101#issuecomment-501999070)

        The following solutions were tried, but didn't work:

        - take "keep alive" photo (https://github.com/KonradIT/goprowifihack/issues/101#issuecomment-831998066)
            `self.take_photo()`
        - repeatedly set the camera mode (https://github.com/KonradIT/goprowifihack/issues/101#issuecomment-402822421)
            if "HERO5 Black" in self.__cam.infoCamera(constants.Camera.Name) or "HERO6" in self.__cam.infoCamera(
                    constants.Camera.Name):
                self.__cam.mode(constants.Mode.PhotoMode, constants.Mode.SubMode.Photo.Single_H5)
            else:
                self.__cam.mode(constants.Mode.PhotoMode)
        - sending a KeepAlive message (https://github.com/KonradIT/goprowifihack/issues/101#issuecomment-361219961)
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto("_GPHD_:0:0:2:0.000000\n".encode(), (self.__cam.ip_addr, 8554))
            time.sleep(2500 / 1000)
        """
        pass

    def _update_status(self) -> bool:
        if self.__cam:
            try:
                raw = self.__cam.getStatusRaw()
            except Exception as ex:
                return False

            if raw and self.__cam:
                js = json.loads(raw)
                if constants.Status.Status in js:
                    self.__cam_status['mode'] = self.__cam.parse_value("mode", js[constants.Status.Status][
                        constants.Status.STATUS.Mode])
                    self.__cam_status['recording'] = (js[constants.Status.Status][
                                                          constants.Status.STATUS.IsRecording] == 1)
                    self.__cam_status['sd_card'] = (js[constants.Status.Status][
                                                        constants.Status.STATUS.SdCardInserted] == 0)
                    self.__cam_status['lastVideo'] = self.__cam.getMedia()
                    # parse and format datetime data
                    self.__cam_status['datetime'] = "{2:02.0f}.{1:02.0f}.{0} {3:02.0f}:{4:02.0f}:{5:02.0f}".format(*map(lambda h: int(h, 16), filter(None, js[
                        constants.Status.Status]['40'].split('%'))))
                    # update video settings
                    for var, val in vars(constants.Video).items():
                        if not var.startswith("_") and not inspect.isclass(val) and val in js[constants.Status.Settings]:
                            self.__cam_settings[var] = js[constants.Status.Settings][val]
                    # {'RESOLUTION': ('2', 8), 'FRAME_RATE': ('3', 8), 'FOV': ('4', 0), 'LOW_LIGHT': ('5', 0), 'SPOT_METER': ('9', 1), 'VIDEO_LOOP_TIME': ('6', 1), 'VIDEO_PHOTO_INTERVAL': ('7', 0), 'PROTUNE_VIDEO': ('10', 0), 'WHITE_BALANCE': ('11', 0), 'COLOR': ('12', 1), 'ISO_LIMIT': ('13', 2), 'ISO_MODE': ('74', 0), 'SHARPNESS': ('14', 3), 'EVCOMP': ('15', 5)}
                    return True
                else:
                    self._logger.warning("Failed to get status of the gopro: %s", raw)
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
            self._cancel.wait(0.5)

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
            self._cancel.wait(1)  # wait for the command to be executed

    def _stop_recording(self):
        if self.__cam:
            self.__cam.shutter(constants.stop)
            self._cancel.wait(1)  # wait for the command to be executed

    def _last_video(self) -> str:
        return self.__cam_status['lastVideo']

    def __set(self, setting, value):
        if self.__cam:
            self.__cam.gpControlSet(str(setting), str(value))

    def _fps(self) -> str:
        return self.FPS_MAPPING.key(self.__cam_settings['FRAME_RATE'])

    def _set_fps(self, value) -> bool:
        self.__set(constants.Video.FRAME_RATE, self.FPS_MAPPING[value])
        self._update_status()
        return str(self.__cam_settings['FRAME_RATE']) == str(self.FPS_MAPPING[value])

    def _fov(self) -> str:
        return self.FOV_MAPPING.key(self.__cam_settings['FOV'])

    def _set_fov(self, value) -> bool:
        self.__set(constants.Video.FOV, self.FOV_MAPPING[value])
        self._update_status()
        return str(self.__cam_settings['FOV']) == str(self.FOV_MAPPING[value])

    def _res(self) -> str:
        return self.RES_MAPPING.key(self.__cam_settings['RESOLUTION'])

    def _set_res(self, value) -> bool:
        self.__set(constants.Video.RESOLUTION, self.RES_MAPPING[value])
        self._update_status()
        return str(self.__cam_settings['RESOLUTION']) == str(self.RES_MAPPING[value])


class NetworkState(Enum):
    CONNECTING = 0
    CONNECTED = 1
    DISCONNECTED = 2
    NOTAVAILABLE = 3


class Network(threading.Thread):
    """ Handles the connection to the GoPro Wi-Fi network."""

    def __init__(self, device: str, ssid: str, passwd: str, mac: str = None, logger: logging.Logger = None):
        super().__init__()

        self.__logger = logging.getLogger(self.__class__.__name__) if logger is None else logger.getChild(self.__class__.__name__)

        # creates an appropriate manager, based on the available network applications
        self.manager = NetworkManagerNmcli() if shutil.which('nmcli') is not None else NetworkManagerIw()

        self.device = self.manager.getWifiDevice(device)
        self.ssid = ssid
        self.passwd = passwd

        self.bt = Bluetooth(mac, logger=logger)
        self.bt_loop = asyncio.new_event_loop()

        self.gopro_available = threading.Event()
        self.gopro_disconnected = threading.Event()
        self.gopro_connecting = threading.Event()
        self.gopro_connected = threading.Event()

        self.__cancel = threading.Event()

    def __set_event(self, state: NetworkState):
        if state == NetworkState.NOTAVAILABLE:
            self.gopro_available.clear()
            self.gopro_disconnected.clear()
            self.gopro_connecting.clear()
            self.gopro_connected.clear()
        elif state == NetworkState.CONNECTING:
            self.gopro_available.set()
            self.gopro_disconnected.clear()
            self.gopro_connecting.set()
            self.gopro_connected.clear()
        elif state == NetworkState.CONNECTED:
            self.gopro_available.set()
            self.gopro_disconnected.clear()
            self.gopro_connecting.set()
            self.gopro_connected.set()
        elif state == NetworkState.DISCONNECTED:
            self.gopro_available.set()
            self.gopro_disconnected.set()
            self.gopro_connecting.clear()
            self.gopro_connected.clear()


    def setConfig(self, device: str, ssid: str, passwd: str):
        # set the new params
        self.device = self.manager.getWifiDevice(device)
        self.ssid = ssid
        self.passwd = passwd
        # NOTE: auto-reconnects on the next 'isConnected' check

    def connect(self):
        self.__logger.info("Setting up network")
        if not self.is_connected():
            # check Wi-Fi device
            device = self.manager.getWifiDevice(self.device)
            self.__logger.info("Using device %s", device)

            # wait for connection
            while not self.__cancel.is_set():
                self.ble_wifi_enable()
                # check if ssid is available
                if not self.manager.getSSIDExists(device, self.ssid):
                    self.__logger.info("SSID not found: %s", self.ssid)
                    self.__set_event(NetworkState.NOTAVAILABLE)  # NetworkNotAvailable
                    # wait some time, before attempting to scan for the network ssid
                    self.__cancel.wait(2.0)
                else:
                    self.__logger.info("Waiting for connection to %s", self.ssid)
                    self.__set_event(NetworkState.CONNECTING)  # NetworkConnecting
                    network = self.manager.connectToSSID(device, self.ssid, self.passwd)

                    if network is None:
                        self.__logger.error("Couldn't connect to network '%s' with device '%s'!", self.ssid, self.device)
                        self.__set_event(NetworkState.DISCONNECTED)  # NetworkDisconnected
                        # wait some time, before next attempt
                        self.__cancel.wait(10)
                    else:
                        self.__logger.info("Connected to %s @ %s", network, datetime.datetime.now())
                        self.__set_event(NetworkState.CONNECTED)  # NetworkConnected
                        break
        else:
            self.__set_event(NetworkState.CONNECTED)  # NetworkConnected

    def disconnect(self):
        # TODO:
        self.__set_event(NetworkState.DISCONNECTED)  # NetworkDisconnected

    def is_connected(self):
        return self.ssid == self.manager.getCurrentSSID(self.device, False) and self.bt.is_connected

    def ble_wifi_enable(self):
        self.__logger.debug("Trying to activate network via bluetooth")

        async def enable_wifi():
            if await self.bt.connect():
                await self.bt.enable_wifi()
            else:
                self.__logger.warning("Unable to connect to GoPro via bluetooth")

        self.bt_loop.run_until_complete(enable_wifi())

    def run(self):
        # connect and fire connected event
        self.connect()
        while not self.__cancel.is_set():
            if self.is_connected():
                self.__cancel.wait(0.5)
                # TODO: do we need to send a keep alive on the "network layer"?
            else:
                self.__set_event(NetworkState.DISCONNECTED)  # NetworkDisconnected
                self.connect()
        self.__logger.debug("Network thread finished.")

    def cancel(self):
        self.__cancel.set()
        self.manager.cancel()
        if self.bt.is_connected:
            self.bt_loop.run_until_complete(self.bt.disconnect())


class NetworkManager(metaclass=ABCMeta):
    def __init__(self, logger: logging.Logger = None):
        self._cancel = threading.Event()
        self._logger = logging.getLogger(self.__class__.__name__) if logger is None else logger.getChild(self.__class__.__name__)

    @abstractmethod
    def getWifiDevices(self):
        """ Retrieves all Wi-Fi devices.

        :return:        a list of available Wi-Fi devices
        """

        return []

    def getWifiDevice(self, device: str = None):
        """ Checks whether the given Wi-Fi device is available or returns the available Wi-Fi device if nothing given.
            There had to be only one Wi-Fi device if nothing was given. Otherwise, an error is printed out.

        :param device:  the device, which should be checked
        :return:        a Wi-Fi device or None
        """

        if device is None:
            devices = self.getWifiDevices()
            if len(devices) > 1:
                self._logger.error("Multiple devices available!")
            elif len(devices) == 0:
                self._logger.error("No device available!")
            else:
                return devices[0]
        elif device not in self.getWifiDevices():
            self._logger.error("Device '%s' is not available!", device)
        else:
            return device
        return None

    @abstractmethod
    def getCurrentSSID(self, device: str, log=True):
        """ Checks if the given device is currently connected and returns the SSID of the connected network otherwise returns None.

        :param device:  name of the device from which we want to get the current SSID
        :return:        the current SSID of the device
        """

        return None

    @abstractmethod
    def getSSIDExists(self, device: str, ssid: str):
        return False

    def connectToSSID(self, device: str, ssid: str, passwd: str = None):
        """ Connects the given device to the given SSID with the provided password.

        :param device:  name of the device we're like to connect with
        :param ssid:    SSID of the network we're like to connect with
        :param passwd:  the password of the SSID we're like to connect with
        :return:        the SSID of the connected network or 'None' if an error occurred
        """

        if self.getCurrentSSID(device) == ssid:
            return ssid

        return self._connect(device, ssid, passwd)

    @abstractmethod
    def _connect(self, device: str, ssid: str, passwd: str = None):
        return None

    @abstractmethod
    def getAPmac(self, device: str):
        return None

    def cancel(self):
        self._cancel.set()


class NetworkManagerNmcli(NetworkManager):

    def getWifiDevices(self):
        """
            getting available devices:  nmcli -t device
        """
        wifi_devices = []

        self._logger.debug("Get all available wifi devices: 'nmcli -t device'")
        devices = subprocess.run(['nmcli', '-t', 'device'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        for dev in devices.split('\n'):
            if dev:
                dev_state = dev.split(':')
                if dev_state[1] == 'wifi':
                    wifi_devices.append(dev_state[0])
        return wifi_devices

    def getCurrentSSID(self, device: str, log=True):
        """
            checking connection:        nmcli -g GENERAL.STATE device show <device>
            determine network:          nmcli -g GENERAL.CONNECTION device show <device>
        """
        if log:
            self._logger.debug("Check device state: 'nmcli -g GENERAL.STATE device show %s'", device)
        state = subprocess.run(['nmcli', '-g', 'GENERAL.STATE', 'device', 'show', device],
                               stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        # do we have an established connection
        if state and state.split()[0] == '100':
            if log:
                self._logger.debug("Get SSID of current connection: 'nmcli -g GENERAL.CONNECTION device show %s'", device)
            # return SSID of current connection
            return subprocess.run(['nmcli', '-g', 'GENERAL.CONNECTION', 'device', 'show', device],
                                  stdout=subprocess.PIPE).stdout.decode('utf-8').strip()
        return None

    def getSSIDExists(self, device: str, ssid: str):
        self._logger.debug("Scan for the SSID: 'nmcli device wifi rescan ifname %s'", device)
        subprocess.run(['nmcli', 'device', 'wifi', 'rescan', 'ifname', device], stdout=subprocess.PIPE,
                       stderr=subprocess.DEVNULL).stdout.decode('utf-8').strip()
        self._logger.debug("Check SSID: 'nmcli device wifi list ifname %s'", device)
        result = subprocess.run(['nmcli', 'device', 'wifi', 'list', 'ifname', device], stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL).stdout.decode('utf-8').strip()
        match = re.search(r'.*\s+' + ssid + '\s+.*', result)
        return (match is not None)

    def getAPmac(self, device: str):
        # TODO: !
        self._logger.debug("Scan for the MAC: 'iwconfig %s'", device)
        result = subprocess.run(['iwconfig', device], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode(
            'utf-8').strip()
        # Access Point: F6:DD:9E:87:A1:63
        match = re.search(r'.*Access Point: (..:..:..:..:..:..).*', result)
        if match is None:
            return None
        else:
            return match.group(1).replace(':', '')

    def _connect(self, device: str, ssid: str, passwd: str = None):
        """
            get existing networks:      nmcli connection show <ssid>
            connect to network:         nmcli connection up <ssid> ifname <device>
            create/connect network:     nmcli device Wi-Fi connect <ssid> password <passwd> ifname <device>
        """
        self._logger.debug("Check if wifi network profile already exists: 'nmcli connection show %s'", ssid)
        # exists a saved wifi network with the given SSID?
        if subprocess.run(['nmcli', 'connection', 'show', ssid], stdout=subprocess.DEVNULL,
                          stderr=subprocess.DEVNULL).returncode == 0:
            self._logger.debug("Connect to existing wifi network profile: 'nmcli connection up %s ifname %s'", ssid, device)
            # try to activate the saved wifi network with the given SSID
            r = subprocess.run(['nmcli', 'connection', 'up', ssid, 'ifname', device], stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)
            if r.returncode != 0:
                self._logger.error("Couldn't connect to network '%s' with device '%s'!\n\twhat: %s", ssid, device,
                             str(r.stderr, 'utf-8').strip())
            else:
                return ssid
        # ... else create new connection - if password given
        elif passwd is not None:
            self._logger.debug(
                "Create a new wifi network profile and connect: 'nmcli device wifi connect %s password %s ifname %s'",
                ssid, passwd, device)
            r = subprocess.run(['nmcli', 'device', 'wifi', 'connect', ssid, 'password', passwd, 'ifname', device])
            if r.returncode != 0:
                self._logger.error("Couldn't connect to network '%s' with device '%s'; wrong credentials?\n\twhat: %s", ssid,
                             device, str(r.stderr, 'utf-8').strip())
            else:
                return ssid
        else:
            self._logger.error("Could not connect to %s, password required!", ssid)
        return None


class NetworkManagerIw(NetworkManager):
    def getWifiDevices(self):
        """
            getting available devices:  iw dev
        """

        wifi_devices = []

        self._logger.debug("Get all available wifi devices: 'iw dev'")
        devices = subprocess.run(['iw', 'dev'], stdout=subprocess.PIPE).stdout.decode('utf-8')
        for dev in devices.split('\n'):
            if dev:
                match = re.search('Interface\s+(\w+)', dev.strip())
                if match:
                    wifi_devices.append(match.group(1))
        return wifi_devices

    def getCurrentSSID(self, device: str, log=True):
        """
            determine current network:  iwgetid <device> -r
        """
        # old: iwgetid %s -r / wpa_cli -i %s status

        self._logger.debug("Get current wifi SSID: 'iwconfig %s'", device)
        result = subprocess.run(['iwconfig', device], stdout=subprocess.PIPE)
        search = re.search(r'ESSID:"(\S+)"', result.stdout.decode('utf-8').strip(), re.M)
        # do we have an established connection
        if search:
            # return SSID of current connection
            return search.group(1).strip()

        return None

    def getSSIDExists(self, device: str, ssid: str):
        # make sure the device is up
        self.__checkDeviceState(device)
        self._logger.debug("Scan for the SSID: 'iwlist %s scanning essid %s'", device, ssid)
        result = subprocess.run(['iwlist', device, 'scanning', 'essid', ssid], stdout=subprocess.PIPE,
                                stderr=subprocess.DEVNULL).stdout.decode('utf-8').strip()
        match = re.search(r'.*(' + ssid + ').*', result)
        return (match is not None)

    def getAPmac(self, device: str):
        self._logger.debug("Scan for the MAC: 'iwconfig %s'", device)
        result = subprocess.run(['iwconfig', device], stdout=subprocess.PIPE, stderr=subprocess.DEVNULL).stdout.decode(
            'utf-8').strip()
        # Access Point: F6:DD:9E:87:A1:63
        match = re.search(r'.*Access Point: (..:..:..:..:..:..).*', result)
        if match is None:
            return None
        else:
            return match.group(1).replace(':', '')

    def _connect(self, device: str, ssid: str, passwd: str = None):
        """
            activate device:            ifconfig <device> up
            check existing networks:    wpa_cli -i <device> list_networks
            connect to network:         wpa_cli -i <device> select_network <network_id>
            configure new network:      wpa_cli -i <device> reconfigure
        """
        # make sure the device is up
        self.__checkDeviceState(device)

        # stop running wpa_supplicant instance
        subprocess.run(['wpa_cli', '-i', device, 'terminate'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        wpa_file = "/tmp/wpa_gopro.conf"
        self._logger.debug("Create a new wifi network profile in '%s'", wpa_file)
        try:
            f = open(wpa_file, "w")
            f.writelines([
                'ctrl_interface=/run/wpa_supplicant\n'
                'update_config=1\n\n'
                'network={\n',
                '\tssid="' + str(ssid) + '"\n',
                '\tpsk="' + str(passwd) + '"\n',
                '}\n'
            ])
            # f.writelines(['network={\n', 'ssid="' + ssid + '"\n', 'psk="' + passwd + '"\n', '}\n'])
            f.close()

            # (re-)start the wpa_supplicant deamon
            self._logger.debug("Start wpa_supplicant with config: '%s'", wpa_file)
            subprocess.run(['wpa_supplicant', '-B', '-i', device, '-c', wpa_file], stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)

            # wait max. 10s or until connected
            it = 0
            while (self.getCurrentSSID(device) is None or self.getCurrentSSID(
                    device) != ssid) and it < 10 and not self._cancel.is_set():
                self._cancel.wait(1)
                it += 1
            # check if connection was successful and return
            if self.getCurrentSSID(device) == ssid:
                return ssid
        except:
            self._logger.critical("Error creating wifi network config file ({})!".format(wpa_file))

        return None

    def __checkDeviceState(self, device):
        self._logger.debug("Bringing device up: 'ifconfig %s up'", device)
        subprocess.run(['ifconfig', device, 'up'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


class Bluetooth:
    """
    Based on the work of KonradIT:
    - https://github.com/KonradIT/gopro-ble-py/blob/opengopro/main.py
    - https://github.com/KonradIT/goprowifihack/blob/master/Bluetooth/bluetooth-api.md
    - https://github.com/KonradIT/goprowifihack/blob/master/Bluetooth/Platforms/RaspberryPi.md
    - https://github.com/KonradIT/goprowifihack/blob/master/Bluetooth/Platforms/ArchLinux.md

    """
    BLE_CHAR_V2_STRING = "{}-aa8d-11e3-9046-0002a5d5c51b"

    def __init__(self, address: str = None, timeout: int = 5, retries: int = 5, logger: logging.Logger = None):
        self.__logger = logging.getLogger(self.__class__.__name__) if logger is None else logger.getChild(
            self.__class__.__name__)

        self.__ble: BleakClient | None = None
        self.__address: str = address
        self.__timeout: int = timeout
        self.__retries: int = retries

        self.characteristics = {
            'control': self.BLE_CHAR_V2_STRING.format("b5f90072"),
            'control_notify': self.BLE_CHAR_V2_STRING.format("b5f90073"),
            'setting': self.BLE_CHAR_V2_STRING.format("b5f90074"),
            'setting_notify': self.BLE_CHAR_V2_STRING.format("b5f90075"),
            'status': self.BLE_CHAR_V2_STRING.format("b5f90076"),
            'status_notify': self.BLE_CHAR_V2_STRING.format("b5f90077")
        }

    @staticmethod
    async def find_device(timeout: int = 5, retries: int = 5) -> BLEDevice|None:
        device = None

        def scan_callback(d: BLEDevice, adv_data: AdvertisementData) -> None:
            nonlocal device
            if (name := adv_data.local_name or d.name) and name.startswith('GoPro'):
                device = d
                stop_event.set()

        for r in range(retries):
            stop_event = asyncio.Event()
            async with BleakScanner(timeout=timeout, detection_callback=scan_callback):
                try:
                    await asyncio.wait_for(stop_event.wait(), timeout)
                except asyncio.TimeoutError as e:
                    pass
            if device:
                return device

        return None

    async def connect(self) -> bool:
        self.__logger.info('Try to connect to GoPro')
        if self.__ble is not None:
            if not self.__ble.is_connected:
                try:
                    await self.__ble.connect()
                    self.__logger.info('Connected to GoPro')
                except BleakDeviceNotFoundError:
                    self.__logger.error('Unable to connect GoPro')
                except BleakError as e:
                    self.__logger.error('An error occurred: %s', str(e))
            return self.is_connected

        # if MAC address is not set, try to find GoPro
        if self.__address is None:
            self.__address = await self.find_device(self.__timeout, self.__retries)

        # still not set? Unable to connect!
        if self.__address is None:
            self.__logger.error('Unable to find GoPro')
            return False

        self.__ble = BleakClient(self.__address)
        try:
            await self.__ble.connect()
            self.__logger.info('Connected to GoPro')
        except BleakDeviceNotFoundError:
            self.__logger.error('Unable to connect GoPro')

        return self.is_connected

    async def disconnect(self):
        if self.__ble is not None:
            self.__logger.info('Disconnect from GoPro')
            await self.__ble.disconnect()

    @property
    def is_connected(self) -> bool:
        return self.__ble is not None and self.__ble.is_connected

    @property
    def address(self):
        if self.is_connected:
            return self.__ble.address

    async def __wait_for_response(self, characteristics, command):
        recv_event = asyncio.Event()

        def cb(sender, data: bytearray):
            recv_event.set()

        await self.__ble.start_notify(self.characteristics['control_notify'], cb)
        await self.__ble.write_gatt_char(characteristics, command)
        await asyncio.wait_for(recv_event.wait(), self.__timeout)
        await self.__ble.stop_notify(self.characteristics['control_notify'])

    async def enable_wifi(self):
        if self.is_connected:
            self.__logger.info('Enable Wifi')
            await self.__wait_for_response(self.characteristics['control'], bytearray(b'\x03\x17\x01\x01'))  # Wifi ON

    async def disable_wifi(self):
        if self.is_connected:
            self.__logger.info('Disable Wifi')
            await self.__wait_for_response(self.characteristics['control'], bytearray(b'\x03\x17\x01\x00'))  # Wifi OFF

    async def locate_on(self):
        if self.is_connected:
            self.__logger.info('Beep on')
            await self.__wait_for_response(self.characteristics['control'], bytearray(b'\x03\x16\x01\x01'))  # Locate ON

    async def locate_off(self):
        if self.is_connected:
            self.__logger.info('Beep off')
            await self.__wait_for_response(self.characteristics['control'], bytearray(b'\x03\x16\x01\x00'))  # Locate OFF

    async def video_mode(self):
        if self.is_connected:
            self.__logger.info('Set mode to video')
            await self.__wait_for_response(self.characteristics['control'], bytearray(b'\x03\x02\x01\x00'))  # video mode

    async def photo_mode(self):
        if self.is_connected:
            self.__logger.info('Set mode to photo')
            await self.__wait_for_response(self.characteristics['control'], bytearray(b'\x03\x02\x01\x01'))  # photo mode

    async def power_off(self):
        if self.is_connected:
            self.__logger.info('Power off GoPro')
            await self.__wait_for_response(self.characteristics['control'], bytearray(b'\x01\x05'))  # power off


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    n = Network('wifi0', 'GP26297683', 'epic0546', -1, '')
    n.start()

    print('Wait till GoPro is available')
    n.gopro_available.wait()

    print('Wait till GoPro is connecting')
    n.gopro_connecting.wait()

    print('Wait till GoPro is connected')
    n.gopro_connected.wait()

    n.join()

    '''
    ctx = zmq.Context.instance()

    print('Start GoproCam')
    g = GoProCam(ctx, False, False, 900)
    g.start()
    #blackboard['network'] = 3  # simulate network available
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
            #print(blackboard)
            pass
    g.cancel()
    g.join()
    '''

    print('Done')
