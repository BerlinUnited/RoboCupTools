import asyncio
from typing import Union

from services.gopro.GoProCam import Bluetooth


async def wakeup_device(mac_address: Union[str, None] = None):

    ble = Bluetooth(mac_address)
    if await ble.connect():
        print('Set beep ON for', ble.address)
        await ble.locate_on()

        print('Beep for 3 seconds ...')
        await asyncio.sleep(3)

        print('Set beep OFF for', ble.address)
        await ble.locate_off()

        #print('Power off')
        #await ble.power_off()

        await ble.disconnect()
    else:
        print('GoPro not found or unable to wakeup!')

    print('Done')


def run(mac_address: Union[str, None] = None):
    """
    Switches the GoPro on using Bluetooth.
    """
    asyncio.run(wakeup_device(mac_address))
