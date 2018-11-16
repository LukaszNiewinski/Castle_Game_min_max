import numpy as np
from enum import Enum


class GameColor(Enum):
    WHITE = 0
    BLACK = 1

    @classmethod
    def second_color(cls, color):
        if color == cls.WHITE:
            return cls.BLACK
        elif color == cls.BLACK:
            return cls.WHITE


class GameModel:
    numOfCells = 19

    initBlackBallPositions = [(11, 2), (11, 16), (18, 5), (18, 13), (13, 7), (13, 11), (17, 7), (17, 11)]
    initWhiteBallPositions = [(7, 2), (7, 16), (0, 5), (0, 13), (5, 7), (5, 11), (1, 7), (1, 11)]

    blackThronePos = (3, 9)
    whiteThronePos = (15, 9)

    def __init__(self):
        self.activeColor = GameColor.BLACK
        self.wallsMap = None
        self.ballsMap = None
        self.model_state_init()

    def model_state_init(self):
        self.wallsMap = np.array([[False]*self.numOfCells]*19, dtype=bool)
        self.wall_map_init()
        self.ballsMap = np.array([[None]*19]*19, dtype=GameColor)
        self.balls_map_init()

    def wall_map_init(self):
        wallsMap = self.wallsMap
        for i in range(1, 8):
            wallsMap[(i, 2)] = True
            wallsMap[(i, 16)] = True
            wallsMap[(self.numOfCells - i - 1, 2)] = True
            wallsMap[(self.numOfCells - i - 1, 16)] = True
        for i in range(0, 6):
            wallsMap[(i, 5)] = True
            wallsMap[(i, 13)] = True
            wallsMap[(self.numOfCells - i - 1, 5)] = True
            wallsMap[(self.numOfCells - i - 1, 13)] = True
        for i in range(1, 6):
            wallsMap[(i, 7)] = True
            wallsMap[(i, 11)] = True
            wallsMap[(self.numOfCells - i - 1, 7)] = True
            wallsMap[(self.numOfCells - i - 1, 11)] = True
        for i in range(3, 9):
            wallsMap[(7, i)] = True
            wallsMap[(11, i)] = True
            wallsMap[(7, self.numOfCells - i - 1)] = True
            wallsMap[(11, self.numOfCells - i - 1)] = True
        for i in range(7, 12):
            wallsMap[(5, i)] = True
            wallsMap[(13, i)] = True
        wallsMap[(1, 8)] = True
        wallsMap[(1, 10)] = True
        wallsMap[(17, 8)] = True
        wallsMap[(17, 10)] = True

    def balls_map_init(self):
        for position in self.initBlackBallPositions:
            self.ballsMap[position] = GameColor.BLACK

        for position in self.initWhiteBallPositions:
            self.ballsMap[position] = GameColor.WHITE

    def is_something_between(self, map: np.ndarray, startPos: tuple, endPos: tuple, direction, delta, negated=False):
        # negated paramter:
        # if false check if there is any wall between clear cells
        # if true check if there is any clear cell between walls
        if delta < 0:
            startPos, endPos = endPos, startPos
        if direction == 0:
            for cell in map[startPos[0]+1:endPos[0], startPos[1]]:
                if np.logical_xor(bool(cell), negated):
                    return True
        elif direction == 1:
            for cell in map[startPos[0], startPos[1]+1:endPos[1]]:
                if np.logical_xor(bool(cell), negated):
                    return True
        return False

    def valid_move(self, startPos: tuple, endPos: tuple):
        dy = endPos[0] - startPos[0]
        dx = endPos[1] - startPos[1]
        delta = dy
        direction = 0
        if not np.logical_xor(dx, dy):
            return False
        if not dy:
            delta = dx
            direction = 1
        isStartWall = self.wallsMap[startPos]
        isEndWall = self.wallsMap[endPos]
        if np.logical_xor(isStartWall, isEndWall):
            if abs(delta) > 1:
                return False
        elif not isStartWall and not isEndWall:
            if self.is_something_between(self.wallsMap, startPos, endPos, direction, delta):
                return False
        else:
            if self.is_something_between(self.wallsMap, startPos, endPos, direction, delta, True):
                return False
        if self.is_something_between(self.ballsMap, startPos, endPos, direction, delta):
            return False
        if self.ballsMap[endPos]:
            if self.ballsMap[endPos] == self.activeColor:
                return False
        return True
