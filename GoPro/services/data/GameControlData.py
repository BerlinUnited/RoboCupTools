"""
    Copied structure from the GameController "data.GameControlData.java" file.
    https://github.com/RoboCup-SPL/GameController/blob/master/include/RoboCupGameControlData.h
"""

from struct import Struct


class GameControlData(Struct):
    """Representation of the SPL message format."""

    GAMECONTROLLER_TRUE_DATA_REQUEST = b'RGTr'
    GAMECONTROLLER_TRUE_DATA_HEADER = b'RGTD'
    GAMECONTROLLER_TRUE_DATA_VERSION = 0

    GAMECONTROLLER_STRUCT_HEADER = b'RGme'
    GAMECONTROLLER_STRUCT_VERSION = 18

    COMPETITION_PHASE_ROUNDROBIN  = 0
    COMPETITION_PHASE_PLAYOFF     = 1

    COMPETITION_TYPE_NORMAL                = 0
    COMPETITION_TYPE_SHARED_AUTONOMY       = 1

    GAME_PHASE_NORMAL                   = 0
    GAME_PHASE_PENALTYSHOOT             = 1
    GAME_PHASE_OVERTIME                 = 2
    GAME_PHASE_TIMEOUT                  = 3

    STATE_INITIAL                       = 0
    STATE_READY                         = 1
    STATE_SET                           = 2
    STATE_PLAYING                       = 3
    STATE_FINISHED                      = 4
    STATE_STANDBY                       = 5

    SET_PLAY_NONE                       = 0
    SET_PLAY_GOAL_KICK                  = 1
    SET_PLAY_PUSHING_FREE_KICK          = 2
    SET_PLAY_CORNER_KICK                = 3
    SET_PLAY_KICK_IN                    = 4
    SET_PLAY_PENALTY_KICK               = 5

    def __init__(self, data=None, **kwargs):
        """Constructor."""
        # initialize with the struct format characters as described here
        # https://docs.python.org/2/library/struct.html
        super(GameControlData, self).__init__('4s'  # header
                                              'B'  # version
                                              'B'  # packetNumber
                                              'B'  # playersPerTeam
                                              'B'  # competitionPhase
                                              'B'  # competitionType
                                              'B'  # gamePhase
                                              'B'  # gameState #state
                                              'B'  # setPlay
                                              'B'  # firstHalf
                                              'B'  # kickingTeam
                                              'h'  # secsRemaining
                                              'h')  # secondaryTime

        self.trueData = kwargs.pop('trueData', False)
        self.packetNumber = kwargs.pop('packetNumber', 0)
        self.playersPerTeam = kwargs.pop('playersPerTeam', 7)

        self.competitionPhase = kwargs.pop('competitionPhase', self.COMPETITION_PHASE_ROUNDROBIN)
        self.competitionType = kwargs.pop('competitionType', self.COMPETITION_TYPE_NORMAL)
        self.gamePhase = kwargs.pop('gamePhase', self.GAME_PHASE_NORMAL)
        self.gameState = kwargs.pop('gameState', self.STATE_INITIAL)
        self.setPlay = kwargs.pop('setPlay', self.SET_PLAY_NONE)

        self.firstHalf = kwargs.pop('firstHalf', 1)
        self.kickingTeam = kwargs.pop('kickingTeam', 0)

        self.secsRemaining = kwargs.pop('secsRemaining', 600)
        self.secondaryTime = kwargs.pop('secondaryTime', 0)

        self.team = [TeamInfo(), TeamInfo()]

        if data is not None:
            self.unpack(data)

    def unpack(self, data):
        # check 'data' length
        if len(data) < self.size:
            return False, "Not well formed GameControlData!"

        msg = Struct.unpack(self, data[:self.size])

        # check header
        if msg[0] == self.GAMECONTROLLER_TRUE_DATA_HEADER:
            self.trueData = True
        elif msg[0] == self.GAMECONTROLLER_STRUCT_HEADER:
            self.trueData = False
        else:
            raise Exception("Invalid message type!")

        # check spl message version
        if msg[1] != self.GAMECONTROLLER_STRUCT_VERSION:
            raise Exception("Wrong version!")

        # assign data
        it = iter(msg[2:])
        self.packetNumber     = next(it)
        self.playersPerTeam   = next(it)

        self.competitionPhase = next(it)
        self.competitionType  = next(it)
        self.gamePhase        = next(it)
        self.gameState        = next(it)
        self.setPlay          = next(it)

        self.firstHalf = next(it)
        self.kickingTeam = next(it)
        self.secsRemaining = next(it)
        self.secondaryTime = next(it)

        for i, t in enumerate(self.team):
            t.unpack(data[self.size+i*t.size:self.size+i*t.size + t.size])

        return True, None

    def pack(self):
        raw = Struct.pack(self,
                          self.GAMECONTROLLER_TRUE_DATA_HEADER if self.trueData else self.GAMECONTROLLER_STRUCT_HEADER,
                          self.GAMECONTROLLER_STRUCT_VERSION,
                          self.packetNumber,
                          self.playersPerTeam,
                          self.competitionPhase,
                          self.competitionType,
                          self.gamePhase,
                          self.gameState,
                          self.setPlay,
                          self.firstHalf,
                          self.kickingTeam,
                          self.secsRemaining,
                          self.secondaryTime)

        for t in self.team:
            raw += t.pack()

        return raw

    def __str__(self):
        out = "              Header: " + str(self.GAMECONTROLLER_TRUE_DATA_HEADER if self.trueData else self.GAMECONTROLLER_STRUCT_HEADER, 'utf-8') + "\n"
        out += "            Version: " + str(self.GAMECONTROLLER_STRUCT_VERSION) + "\n"
        out += "      Packet Number: " + str(self.packetNumber & 0xFF) + "\n"
        out += "   Players per Team: " + str(self.playersPerTeam) + "\n"

        out += "   competitionPhase: " + self.getCompetitionPhase() + "\n"
        out += "    competitionType: " + self.getCompetitionType() + "\n"
        out += "          gamePhase: " + self.getGamePhase() + "\n"
        out += "          gameState: " + self.getGameState() + "\n"
        out += "            setPlay: " + self.getSetPlay() + "\n"

        out += "          firstHalf: "
        if self.firstHalf == 1:
            out += "true"
        elif self.firstHalf == 0:
            out += "false"
        else:
            out += "undefined(" + str(self.firstHalf) + ")"

        out += "\n"
        out += "        kickingTeam: " + str(self.kickingTeam) + "\n"
        out += "      secsRemaining: " + str(self.secsRemaining) + "\n"
        out += "      secondaryTime: " + str(self.secondaryTime) + "\n"

        return out

    def isTrueData(self) -> bool:
        return self.trueData

    def getName(self, names, value):
        if value in names:
            return names[value]
        else:
            return "undefined({})".format(value)

    def getCompetitionPhase(self):
        return self.getName({
            self.COMPETITION_PHASE_ROUNDROBIN: "round robin",
            self.COMPETITION_PHASE_PLAYOFF   : "playoff",
        }, self.competitionPhase)

    def getCompetitionType(self):
        return self.getName({
            self.COMPETITION_TYPE_NORMAL: "normal",
            self.COMPETITION_TYPE_SHARED_AUTONOMY: "COMPETITION_TYPE_SHARED_AUTONOMY"
        }, self.competitionType)

    def getGamePhase(self):
        return self.getName({
            self.GAME_PHASE_NORMAL: "normal",
            self.GAME_PHASE_PENALTYSHOOT: "penalty shoot",
            self.GAME_PHASE_OVERTIME: "over time",
            self.GAME_PHASE_TIMEOUT: "timeout"
        }, self.gamePhase)

    def getGameState(self):
        return self.getName({
            self.STATE_INITIAL: "initial",
            self.STATE_READY: "ready",
            self.STATE_SET: "set",
            self.STATE_PLAYING: "playing",
            self.STATE_FINISHED: "finished",
            self.STATE_STANDBY: "standby"
        }, self.gameState)

    def getSetPlay(self):
        return self.getName({
            self.SET_PLAY_NONE: "none",
            self.SET_PLAY_GOAL_KICK: "goal kick",
            self.SET_PLAY_PUSHING_FREE_KICK: "pushing free kick",
            self.SET_PLAY_CORNER_KICK: "corner kick",
            self.SET_PLAY_KICK_IN: "kick in",
            self.SET_PLAY_PENALTY_KICK: "penalty kick"
        }, self.setPlay)


class TeamInfo(Struct):
    """ Representation of the TeamInfo. """

    MAX_NUM_PLAYERS = 20

    TEAM_BLUE                           = 0  # blue, cyan
    TEAM_RED                            = 1  # red, magenta, pink
    TEAM_YELLOW                         = 2  # yellow
    TEAM_BLACK                          = 3  # black, dark gray
    TEAM_WHITE                          = 4  # white
    TEAM_GREEN                          = 5  # green
    TEAM_ORANGE                         = 6  # orange
    TEAM_PURPLE                         = 7  # purple, violet
    TEAM_BROWN                          = 8  # brown
    TEAM_GRAY                           = 9  # lighter grey

    def __init__(self, data=None, **kwargs):
        super().__init__('B'  # teamNumber
                         'B'  # fieldPlayerColor
                         'B'  # goalkeeperColor
                         'B'  # goalkeeper
                         'B'  # score
                         'B'  # penaltyShot
                         'H'  # singleShots
                         'H')  # messageBudget

        self.teamNumber = kwargs.pop('teamNumber', 0)
        self.fieldPlayerColor = kwargs.pop('fieldPlayerColor', self.TEAM_BLUE)
        self.goalkeeperColor = kwargs.pop('goalkeeperColor', self.TEAM_BLUE)
        self.goalkeeper = kwargs.pop('goalkeeper', 0)
        self.score = kwargs.pop('score', 0)
        self.penaltyShot = kwargs.pop('penaltyShot', 0)
        self.singleShots = kwargs.pop('singleShots', 0)
        self.messageBudget = kwargs.pop('messageBudget', 0)
        self.player = [PlayerInfo() for _ in range(self.MAX_NUM_PLAYERS)]

        if data is not None:
            self.unpack(data)

    @property
    def size(self):
        return super().size + sum([p.size for p in self.player])

    def unpack(self, data):
        # check 'data' length
        if len(data) < self.size:
            print(len(data), self.size)
            return False, "Not well formed TeamInfo!"

        msg = Struct.unpack(self, data[:super().size])

        # assign data
        it = iter(msg)
        self.teamNumber = next(it)
        self.fieldPlayerColor = next(it)
        self.goalkeeperColor = next(it)
        self.goalkeeper = next(it)
        self.score = next(it)
        self.penaltyShot = next(it)
        self.singleShots = next(it)
        self.messageBudget = next(it)

        for i, p in enumerate(self.player):
            p.unpack(data[super().size+i*p.size:super().size+i*p.size + p.size])

        return True, None

    def pack(self):
        raw = Struct.pack(self,
                          self.teamNumber,
                          self.fieldPlayerColor,
                          self.goalkeeperColor,
                          self.goalkeeper,
                          self.score,
                          self.penaltyShot,
                          self.singleShots,
                          self.messageBudget)

        for p in self.player:
            raw += p.pack()

        return raw

    def getName(self, names, value):
        if value in names:
            return names[value]
        else:
            return "undefined({})".format(value)

    def getColor(self, color: int):
        return self.getName({
            self.TEAM_BLUE:   "blue",
            self.TEAM_RED:    "red",
            self.TEAM_YELLOW: "yellow",
            self.TEAM_BLACK:  "black",
            self.TEAM_WHITE:  "white",
            self.TEAM_GREEN:  "green",
            self.TEAM_ORANGE: "orange",
            self.TEAM_PURPLE: "purple",
            self.TEAM_BROWN:  "brown",
            self.TEAM_GRAY:   "grey",
        }, color)

    def __str__(self):
        out = "--------------------------------------\n"

        out += "         teamNumber: " + str(self.teamNumber) + "\n"
        out += "   fieldPlayerColor: " + self.getColor(self.fieldPlayerColor) + "\n"
        out += "    goalkeeperColor: " + self.getColor(self.goalkeeperColor) + "\n"
        out += "         goalkeeper: " + str(self.goalkeeper) + "\n"
        out += "              score: " + str(self.score) + "\n"
        out += "        penaltyShot: " + str(self.penaltyShot) + "\n"
        out += "        singleShots: " + str(self.singleShots) + "\n"
        out += "      messageBudget: " + str(self.messageBudget) + "\n"
        for i, p in enumerate(self.player):
            out += "          Player #" + str(i + 1) + ": " + str(p) + "\n"

        return out


class PlayerInfo(Struct):
    """ Representation of the PlayerInfo. """

    PENALTY_NONE                        = 0
    PENALTY_SPL_ILLEGAL_BALL_CONTACT    = 1
    PENALTY_SPL_PLAYER_PUSHING          = 2
    PENALTY_SPL_ILLEGAL_MOTION_IN_SET   = 3
    PENALTY_SPL_INACTIVE_PLAYER         = 4
    PENALTY_SPL_ILLEGAL_POSITION        = 5
    PENALTY_SPL_LEAVING_THE_FIELD       = 6
    PENALTY_SPL_REQUEST_FOR_PICKUP      = 7
    PENALTY_SPL_LOCAL_GAME_STUCK        = 8
    PENALTY_SPL_ILLEGAL_POSITION_IN_SET = 9
    PENALTY_SPL_PLAYER_STANCE           = 10
    PENALTY_SPL_ILLEGAL_MOTION_IN_STANDBY=11

    PENALTY_SUBSTITUTE                  = 14
    PENALTY_MANUAL                      = 15

    def __init__(self, data: bytes = None, **kwargs):
        super().__init__('B'   # penalty
                         'B')  # secsTillUnpenalised

        self.penalty = kwargs.pop('penalty', 0)
        self.secsTillUnpenalised = kwargs.pop('secsTillUnpenalised', 0)

        if data is not None:
            self.unpack(data)

    def unpack(self, data):
        # check 'data' length
        if len(data) != self.size:
            return False, "Not well formed PlayerInfo!"

        msg = Struct.unpack(self, data)

        # assign data
        it = iter(msg)
        self.penalty = next(it)
        self.secsTillUnpenalised = next(it)

        return True, None

    def pack(self):
        return Struct.pack(self, self.penalty, self.secsTillUnpenalised)

    def getName(self, names, value):
        if value in names:
            return names[value]
        else:
            return "undefined({})".format(value)

    def getPenalty(self):
        return self.getName({
              self.PENALTY_NONE:                        "none",
              self.PENALTY_SPL_ILLEGAL_BALL_CONTACT:    "playing with hands",
              self.PENALTY_SPL_PLAYER_PUSHING:          "pushing",
              self.PENALTY_SPL_ILLEGAL_MOTION_IN_SET:   "motion in set",
              self.PENALTY_SPL_INACTIVE_PLAYER:         "inactive",
              self.PENALTY_SPL_ILLEGAL_POSITION:        "illegal position",
              self.PENALTY_SPL_LEAVING_THE_FIELD:       "leaving the field",
              self.PENALTY_SPL_REQUEST_FOR_PICKUP:      "pickup",
              self.PENALTY_SPL_LOCAL_GAME_STUCK:        "local game stuck",
              self.PENALTY_SPL_ILLEGAL_POSITION_IN_SET: "illegal position in SET",
              self.PENALTY_SPL_PLAYER_STANCE:           "player stance",
              self.PENALTY_SPL_ILLEGAL_MOTION_IN_STANDBY: "illegal motion in STANDBY",

              self.PENALTY_SUBSTITUTE:                  "substitute",
              self.PENALTY_MANUAL:                      "manual",
        }, self.penalty)

    def __str__(self):
        out = "penalty: " + str(self.penalty)
        out += ", secsTillUnpenalised: " + str(self.secsTillUnpenalised)
        return out
