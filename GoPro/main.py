#!/usr/bin/env python3
# -*- coding: utf8 -*-

import logging
import re
import signal
import sys
import argparse
import threading
import time
import zmq

from scripts import check_gamecontroller, check_bluetooth, video_rename, wake_up_gopro, pair_bluetooth
from services import MessageBus, GameController, GameLogger, LEDController, GoProController, Webserver
from utils.Configuration import Configuration


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', '-c', type=argparse.FileType(), default='config.ini')
    parser.add_argument('--verbose', '-v', action='count', default=0)

    subparsers = parser.add_subparsers(dest='action', required=True)
    subparsers.add_parser('gopi', help='Starts the application with all required services')

    services = subparsers.add_parser('service', help='services help')\
                         .add_subparsers(required=True, dest='service')

    services.add_parser('bus', help='Starts the message bus')
    services.add_parser('led', help='Starts the LED service')
    services.add_parser('gl', help='Starts the gamelogger')
    services.add_parser('gc', help='Starts the gamecontroller')
    services.add_parser('gopro', help='Starts the GoPro service')
    services.add_parser('web', help='Starts the Webserver service')

    scripts = subparsers.add_parser('script', help='scripts help')\
                        .add_subparsers(dest='script', required=True)

    scripts_ble = scripts.add_parser('ble', help='Tests the bluetooth functionality')
    scripts_ble.add_argument('mac', type=check_mac_address, default=None, nargs='?', help='default: tries to find GoPro')

    scripts_ble = scripts.add_parser('pair', help='Pairs the GoPro via bluetooth')
    scripts_ble.add_argument('mac', type=check_mac_address, default=None, nargs='?', help='default: tries to find GoPro')

    scripts_gc = scripts.add_parser('gc', help='GameController check script')
    scripts_gc.add_argument('--port', type=int, help='The port of the message bus')

    scripts_vid = scripts.add_parser('video', help='Video rename script')
    scripts_vid.add_argument('videos', type=str, help='Path to the video files, which should be renamed.')
    scripts_vid.add_argument('logs', type=str, help='Path to the log files, on which the video files should be renamed too.')
    scripts_vid.add_argument('--dry', action='store_true', help="Doesn't actually rename, just prints the old and new name.")

    scripts_wake = scripts.add_parser('wake', help='Wake-up GoPro script')
    scripts_wake.add_argument('mac', type=check_mac_address, nargs='?', default='f6:dd:9e:87:a1:63', help='default: D6:B9:D4:D7:B7:40')
    scripts_wake.add_argument('ip', type=str, nargs='?', default='10.5.5.9', help='default: 10.5.5.9')

    return parser.parse_args()


def check_mac_address(mac):
    if not re.match("[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", mac.lower()):
        raise argparse.ArgumentTypeError('Not a valid mac address!')

    return mac


def main(config: Configuration):
    ctx = zmq.Context.instance()
    services = [
        threading.Thread(target=MessageBus.main, args=(ctx, config)),
        threading.Thread(target=LEDController.main, args=(ctx, config)),
        threading.Thread(target=GameController.main, args=(ctx, config)),
        threading.Thread(target=GameLogger.main, args=(ctx, config)),
        threading.Thread(target=GoProController.main, args=(ctx, config)),
        threading.Thread(target=Webserver.main, args=(ctx, config))
    ]

    try:
        def stop_handler(_s, _f):
            config.logger().info('Received interrupt, stopping application ...')
            stop_event.set()

        stop_event = threading.Event()
        signal.signal(signal.SIGTERM, stop_handler)
        signal.signal(signal.SIGINT, stop_handler)

        for s in services:
            s.start()

        # monitor service threads
        while not stop_event.is_set():
            time.sleep(1)
            for s in services:
                if not s.is_alive():
                    config.logger().error("Thread %s is not running (anymore)!", str(s.__class__.__name__))

        raise SystemExit
    except (KeyboardInterrupt, SystemExit):
        ctx.term()

    for s in services:
        s.join()


if __name__ == '__main__':
    # this program is developed for the raspberry pi, so only linux is supported
    if not sys.platform.startswith('linux'):
        sys.stderr.write("Only linux based systems are currently supported!")
        exit(1)

    args = parse_args()
    config = Configuration(args.config.name)
    if args.verbose > 0:
        config.logger().setLevel(logging.ERROR - args.verbose * 10)

    if args.action == 'gopi':
        main(config)
    elif args.action == 'service':
        if args.service == 'bus':
            MessageBus.main()
        elif args.service == 'led':
            LEDController.main()
        elif args.service == 'gl':
            GameLogger.main()
        elif args.service == 'gc':
            GameController.main()
        elif args.service == 'gopro':
            GoProController.main()
        elif args.service == 'web':
            Webserver.main()
        else:
            raise argparse.ArgumentError(args.service, 'Unknown service')
    elif args.action == 'script':
        if args.script == 'ble':
            check_bluetooth.run(args.mac)
        elif args.script == 'pair':
            pair_bluetooth.run(args.mac)
        elif args.script == 'gc':
            port = args.port if args.port else config.bus.port_recv
            check_gamecontroller.run(port)
        elif args.script == 'video':
            video_rename.run(args.videos, args.logs, args.dry)
        elif args.script == 'wake':
            wake_up_gopro.run(args.mac, args.ip)
        else:
            raise argparse.ArgumentError(args.service, 'Unknown service')
    else:
        raise argparse.ArgumentError(args.action, 'Unknown action')
