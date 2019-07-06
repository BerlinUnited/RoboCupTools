import json

from . import Logger
from .Blackboard import blackboard
from .Network import Network
from .GameController import GameController
from .GameControlData import GameControlData
from .GoPro import GoPro
from .daemonize import Daemonize
from .GameLoggerSql import GameLoggerSql
from .GameLoggerLog import GameLoggerLog
from .LEDStatusMonitor import LedStatusMonitor
from .CheckGameController import CheckGameController
from .Bluetooth import Bluetooth
from .CheckBluetooth import CheckBluetooth


def rename(videos_dir, logs_dir, dry:bool=False):
    """ Renames all files from the 'videos_dir' based on the log entry in the 'logs_dir'. """
    import os, re

    if not os.path.isdir(videos_dir):
        Logger.error("Video folder doesn't exists or isn't a directory! ({})".format(videos_dir))
    elif not os.path.isdir(logs_dir):
        Logger.error("Log folder doesn't exists or isn't a directory! ({})".format(logs_dir))
    else:
        Logger.info("Renaming video files")

        vids = {}
        logs = {}

        # read video file names
        for filename in os.listdir(videos_dir):
            name = os.path.splitext(filename)[0]
            if name not in vids:
                vids[name] = []
            vids[name].append(os.path.join(videos_dir, filename))

        # read logs and their content (video files)
        for filename in os.listdir(logs_dir):
            if filename.endswith(".log"):
                try:
                    data = json.load(open(os.path.join(logs_dir, filename)))
                    if data and 'video' in data:
                        for v in data['video']:
                            m = re.match('.+/(.+).MP4', v)
                            if m:
                                name = m.group(1)
                                if name not in logs:
                                    logs[name] = []
                                logs[name].append(os.path.splitext(filename)[0])
                except Exception as e:
                    print('ERROR[',filename, '] Invalid JSON, skipping file;', e)

        cnt = 0

        def do_renaming(v, o):
            c = 0
            for f in vids[o]:
                if os.path.isfile(f):
                    n = re.sub('(.+/)(.+)(\..{3})', '\g<1>'+v+'_'+o+'\g<3>', f)
                    Logger.debug("Renaming '{}' to '{}'".format(o,n))
                    if not dry:
                        os.replace(f, n)
                        #shutil.move(o, n)
                    c += 1
            return c

        # rename video file based on the log entry
        for l in logs:
            if len(logs[l]) == 1 and l in vids:
                # rename the registered file
                cnt += do_renaming(logs[l][0], l)

                # check if other files of the same video exists
                if l.startswith('GOPR'):
                    j = 1
                    while 'GP{:02d}{}'.format(j, l[4:]) in vids:
                        cnt += do_renaming(logs[l][0], 'GP{:02d}{}'.format(j, l[4:]))
                        j += 1

                # check if other files of the same video exists
                if l.startswith('GP'):
                    if 'GOPR{}'.format(l[4:]) in vids:
                        cnt += do_renaming(logs[l][0], 'GOPR{}'.format(l[4:]))
                    j = 1
                    while 'GP{:02d}{}'.format(j, l[4:]) in vids:
                        cnt += do_renaming(logs[l][0], 'GP{:02d}{}'.format(j, l[4:]))
                        j+=1

            elif len(logs[l]) > 1:
                print("ERROR: multiple games for the same video file!?")
        Logger.info("Renamed {} files".format(cnt))
