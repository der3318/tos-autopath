from enum import Enum

class Move(Enum):
    UP = [-1, 0]
    DOWN = [1, 0]
    LEFT = [0, -1]
    RIGHT = [0, 1]

class StoneType(Enum):
    DARK = "dark"
    LIGHT = "light"
    WATER = "water"
    FIRE = "fire"
    EARTH = "earth"
    HEALTH = "health"

class Runestone():

    def __init__(self, _type, _status = " "):
        self.type = _type
        self.status = _status

    def __repr__(self):
        if self.type == StoneType.DARK:
            return "\x1b[0;35;40m D[{}] \x1b[0m".format(self.status)
        if self.type == StoneType.LIGHT:
            return "\x1b[0;33;40m L[{}] \x1b[0m".format(self.status)
        if self.type == StoneType.WATER:
            return "\x1b[0;34;40m W[{}] \x1b[0m".format(self.status)
        if self.type == StoneType.FIRE:
            return "\x1b[0;31;40m F[{}] \x1b[0m".format(self.status)
        if self.type == StoneType.EARTH:
            return "\x1b[0;32;40m E[{}] \x1b[0m".format(self.status)
        if self.type == StoneType.HEALTH:
            return "\x1b[0;37;40m H[{}] \x1b[0m".format(self.status)

