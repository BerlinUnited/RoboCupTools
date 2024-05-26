import socket
import struct


def run(mac_address: str = 'f6:dd:9e:87:a1:63', ip_address: str = '10.5.5.9'):
    """
    Switches on remote computers using WOL.
    Inspired by: https://github.com/citolen/goproh4/blob/master/lib/index.js
    """

    # Check macaddress format and try to compensate.
    if len(mac_address) == 12:
        pass
    elif len(mac_address) == 12 + 5:
        sep = mac_address[2]
        macaddress = mac_address.replace(sep, '')
    else:
        raise ValueError('Incorrect MAC address format')

    # Pad the synchronization stream.
    data = ''.join(['FFFFFFFFFFFF', mac_address * 20])
    send_data = ''

    # Split up the hex values and pack.
    for i in range(0, len(data), 2):
        send_data = ''.join([send_data, struct.pack('B', int(data[i: i + 2], 16))])

    # Broadcast it to the LAN.
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.sendto(send_data, (ip_address, 9))
