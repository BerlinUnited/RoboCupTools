import datetime
import os
import re
import logging

from .Config import config
from .Game import Game


class Event:
    """Represents an event, its addtional informations, its games and their contained logs."""

    def __init__(self, dir):
        """Constructor. Initializes class variables and reads some basic information of the event. Also all available
        games are searched."""
        self.directory = dir

        self.date = None
        self.name = None
        self.games = []

        self.parse_info()
        self.scan_games()

    def parse_info(self):
        """Extracts date and name of this game, based on the configuration regular expression."""
        m = re.match(config['event']['regex'], os.path.basename(self.directory))
        if m:
            self.date = datetime.datetime.strptime(m.group(1), '%Y-%m-%d')
            self.name = m.group(2)
        else:
            logging.getLogger('Event').debug("Couldn't parse event info from %s", os.path.basename(self.directory))

    def scan_games(self):
        """Scans the directory for matching games and add them to the game list."""
        # scan for games at the event
        for game in os.listdir(self.directory):
            # make sure, the game directory has the correct naming scheme
            game_dir = os.path.join(self.directory, game)
            if os.path.isdir(game_dir) and re.match(config['game']['regex'], game):
                g = Game(self, game_dir)
                self.games.append(g)
            else:
                logging.getLogger('Event').debug("Ignoring invalid game directory: %s", game)

    def __repr__(self):
        """Returns the string representation of this event."""
        return "{} @ {} ({})".format(self.name, self.date.strftime('%d.%m.%Y'), len(self.games))
