'''
    Copied structure from the GameController "data.GameControlData.java" file.
    https://github.com/RoboCup-SPL/GameController/blob/master/include/RoboCupGameControlData.h
'''

from struct import Struct


class GameControlData(Struct):
    """Representation of the SPL message format."""

    GAMECONTROLLER_STRUCT_HEADER          = b'RGme'
    GAMECONTROLLER_STRUCT_VERSION         = 13

    COMPETITION_PHASE_ROUNDROBIN          = 0
    COMPETITION_PHASE_PLAYOFF             = 1
    
    COMPETITION_TYPE_NORMAL               = 0
    COMPETITION_TYPE_GENERAL_PENALTY_KICK = 1
    
    GAME_PHASE_NORMAL                     = 0
    GAME_PHASE_PENALTYSHOOT               = 1
    GAME_PHASE_OVERTIME                   = 2
    GAME_PHASE_TIMEOUT                    = 3
    
    STATE_INITIAL                         = 0
    STATE_READY                           = 1
    STATE_SET                             = 2
    STATE_PLAYING                         = 3
    STATE_FINISHED                        = 4

    SET_PLAY_NONE                         = 0
    SET_PLAY_GOAL_FREE_KICK               = 1
    SET_PLAY_PUSHING_FREE_KICK            = 2
    SET_PLAY_CORNER_KICK                  = 3
    SET_PLAY_KICK_IN                      = 4
    SET_PLAY_PENALTY_KICK                 = 5
    
    def __init__(self, data=None):
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
                                               'h'  # secondaryTime
                                              )

        self.setDefaults()

        if data is not None:
            self.unpack(data)

    def setDefaults(self):
        self.packetNumber = 0
        self.playersPerTeam = 6
        
        self.competitionPhase = self.COMPETITION_PHASE_ROUNDROBIN
        self.competitionType  = self.COMPETITION_TYPE_NORMAL
        self.gamePhase        = self.GAME_PHASE_NORMAL
        self.gameState        = self.STATE_INITIAL
        self.setPlay          = self.SET_PLAY_NONE
        
        self.firstHalf = 1
        self.kickingTeam = 0

        self.secsRemaining = 600
        self.secondaryTime = 0

        self.team = [ TeamInfo(), TeamInfo() ]

    def unpack(self, data):
        # check 'data' length
        if len(data) < self.size:
            return (False, "Not well formed GameControlData!")

        msg = Struct.unpack(self, data[:self.size])

        # check header
        if msg[0] != self.GAMECONTROLLER_STRUCT_HEADER:
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

        return (True, None)

    def pack(self):
        return Struct.pack(self,
                           self.SPL_STANDARD_MESSAGE_STRUCT_HEADER,
                           self.SPL_STANDARD_MESSAGE_STRUCT_VERSION,
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
                           self.secondaryTime
                           )

    def __str__(self):
        out = "              Header: " + str(self.GAMECONTROLLER_STRUCT_HEADER, 'utf-8') + "\n"
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

    def getName(self, names, value):
      if value in names:
        return names[value]
      else:
        return "undefined({})".format(value)

    def getCompetitionPhase(self):
      return self.getName({
        self.COMPETITION_PHASE_ROUNDROBIN: "round robin",
        self.COMPETITION_PHASE_PLAYOFF   : "playoff"
      }, self.competitionPhase)
    
    def getCompetitionType(self):
      return self.getName({
        self.COMPETITION_TYPE_NORMAL: "normal",
        self.COMPETITION_TYPE_MIXEDTEAM: "mixed team"
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
        self.STATE_FINISHED: "finished"
      }, self.gameState)
    
    def getSetPlay(self):
      return self.getName({
        self.SET_PLAY_NONE: "none",
        self.SET_PLAY_GOAL_FREE_KICK: "goal free kick",
        self.SET_PLAY_PUSHING_FREE_KICK: "pushing free kick",
        self.SET_PLAY_CORNER_KICK: "corner kick",
        self.SET_PLAY_KICK_IN: "kick in"
      }, self.setPlay)


class TeamInfo(Struct):
    """ Representation of the TeamInfo. """

    MAX_NUM_PLAYERS = 6

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

    def __init__(self, data=None):
        super().__init__('B'  # teamNumber
                         'B'  # teamColor
                         'B'  # score
                         'B'  # penaltyShot
                         'H'  # singleShots
                         )

        self.setDefaults()

        if data is not None:
            self.unpack(data)

    def setDefaults(self):
        self.teamNumber = 0
        self.teamColor = 0
        self.score = 0
        self.penaltyShot = 0
        self.singleShots = 0

        self.player = [ PlayerInfo() for _ in range(self.MAX_NUM_PLAYERS) ]

    @property
    def size(self):
        return super().size + sum([ p.size for p in self.player ])

    def unpack(self, data):
        # check 'data' length
        if len(data) != self.size:
            return (False, "Not well formed TeamInfo!")

        msg = Struct.unpack(self, data[:super().size])

        # assign data
        it = iter(msg)
        self.teamNumber = next(it)
        self.teamColor = next(it)
        self.score = next(it)
        self.penaltyShot = next(it)
        self.singleShots = next(it)

        for i,p in enumerate(self.player):
            p.unpack(data[super().size+i*p.size:super().size+i*p.size + p.size])

        return (True, None)

    def getName(self, names, value):
      if value in names:
        return names[value]
      else:
        return "undefined({})".format(value)

    def getColor(self):
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
      }, self.teamColor)

    def __str__(self):
        out = "--------------------------------------\n"

        out += "         teamNumber: " + str(self.teamNumber) + "\n"
        out += "          teamColor: " + str(self.teamColor) + "\n"
        out += "              score: " + str(self.score) + "\n"
        out += "        penaltyShot: " + str(self.penaltyShot) + "\n"
        out += "        singleShots: " + str(self.singleShots) + "\n"
        for i, p in enumerate(self.player):
            out += "          Player #" + str(i + 1) + ": " + str(p) + "\n"

        return out


class PlayerInfo(Struct):
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
    
    PENALTY_SUBSTITUTE                  = 14
    PENALTY_MANUAL                      = 15

    """ Representation of the PlayerInfo. """

    def __init__(self, data=None):
        super().__init__('B'  # penalty
                         'B'  # secsTillUnpenalised
                         )

        self.setDefaults()

        if data is not None:
            self.unpack(data)

    def setDefaults(self):
        self.penalty = 0
        self.secsTillUnpenalised = 0

    def unpack(self, data):
        # check 'data' length
        if len(data) != self.size:
            return (False, "Not well formed PlayerInfo!")

        msg = Struct.unpack(self, data)

        # assign data
        it = iter(msg)
        self.penalty = next(it)
        self.secsTillUnpenalised = next(it)

        return (True, None)

    def getName(self, names, value):
      if value in names:
        return names[value]
      else:
        return "undefined({})".format(value)

    def getPenalty(self):
      return self.getName({
          self.PENALTY_NONE:                      "none",
          self.PENALTY_SPL_ILLEGAL_BALL_CONTACT:  "playing with hands",
          self.PENALTY_SPL_PLAYER_PUSHING:        "pushing",
          self.PENALTY_SPL_ILLEGAL_MOTION_IN_SET: "motion in set",
          self.PENALTY_SPL_INACTIVE_PLAYER:       "inactive",
          self.PENALTY_SPL_ILLEGAL_POSITION:      "illegal position",
          self.PENALTY_SPL_LEAVING_THE_FIELD:     "leaving the field",
          self.PENALTY_SPL_REQUEST_FOR_PICKUP:    "pickup",
          self.PENALTY_SPL_LOCAL_GAME_STUCK:      "local game stuck",
          PENALTY_SPL_ILLEGAL_POSITION_IN_SET:    "illegal position in SET",
          
          self.PENALTY_SUBSTITUTE:                "substitute",
          self.PENALTY_MANUAL:                    "manual",
      }, self.penalty)

    def __str__(self):
        out = "penalty: " + str(self.penalty)
        out += ", secsTillUnpenalised: " + str(self.secsTillUnpenalised)
        return out
