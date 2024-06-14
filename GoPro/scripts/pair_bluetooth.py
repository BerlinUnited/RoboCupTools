import asyncio
import subprocess
from typing import Union

from services.gopro.GoProCam import Bluetooth


def is_device_trusted(address: str):
    # bluetoothctl devices Trusted
    trusted_devices = subprocess.run(['bluetoothctl', 'devices', 'Trusted'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    for dev in trusted_devices.split('\n'):
        if dev and dev.find(address) >= 0:
            return True
    return False


def trust_device(address: str):
    # bluetoothctl trust DE:AD:BE:EF
    result = subprocess.run(['bluetoothctl', 'trust', address], stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)
    if result.find('succeeded') >= 0:
        return True
    return False


def is_device_paired(address: str):
    # bluetoothctl devices Paired
    paired_devices = subprocess.run(['bluetoothctl', 'devices', 'Paired'], stdout=subprocess.PIPE).stdout.decode('utf-8')
    for dev in paired_devices.split('\n'):
        if dev and dev.find(address) >= 0:
            return True
    return False


def pair_device(address: str):
    # bluetoothctl pair DE:AD:BE:EF
    result = subprocess.run(['bluetoothctl', 'pair', address], stdout=subprocess.PIPE).stdout.decode('utf-8')
    print(result)
    if result.find('successful') >= 0:
        return True
    return False


def run(mac_address: Union[str, None] = None):
    """
    Pairs the GoPro on using Bluetooth.
    """
    print('Before you start, you must bring the GoPro into pairing mode:')
    print('Swipe down > Connect > Connect New Device > GoPro App')

    input('Ready? (press a key)')

    if mac_address is None:
        device = asyncio.run(Bluetooth.find_device())
        if device is None:
            print('Unable to find device')
            exit(1)
        print(f'Found device {device.address}')
        mac_address = device.address

    if not is_device_trusted(mac_address):
        if trust_device(mac_address):
            print(f'Trusted device {mac_address}')
        else:
            print(f'Unable to trust device {mac_address}!')
            exit(2)
    else:
        print(f'Device already trusted {mac_address}')

    if not is_device_paired(mac_address):
        if pair_device(mac_address):
            print(f'Paired device {mac_address}')
        else:
            print(f'Unable to pair device {mac_address}!')
            exit(2)
    else:
        print(f'Device already paired {mac_address}')

    print('Done')
    print('You can now cancel the GoPro pairing mode ...')
