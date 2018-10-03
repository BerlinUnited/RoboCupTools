import datetime
import os
import re

from .Config import config
from .Game import Game


class Event:
    def __init__(self, dir):
        self.directory = dir

        self.date = None
        self.name = None
        self.games = []

        self.parse_info()
        self.scan_games()

    def parse_info(self):
        m = re.match(config['event']['regex'], os.path.basename(self.directory))
        self.date = datetime.datetime.strptime(m.group(1), '%Y-%m-%d')

        self.name = m.group(2)

    def scan_games(self):
        # scan for games at the event
        for game in os.listdir(self.directory):
            # make sure, the game directory has the correct naming scheme
            game_dir = os.path.join(self.directory, game)
            if os.path.isdir(game_dir) and re.match(config['game']['regex'], game):

                g = Game(self, game_dir)
                self.games.append(g)

    def __repr__(self):
        return "{} @ {} ({})".format(self.name, self.date.strftime('%d.%m.%Y'), len(self.games))
