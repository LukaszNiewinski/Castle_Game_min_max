import numpy as np
from enum import Enum
import pygame
from pygame.locals import *


class EndGame(Exception):
    pass


class GameColor(Enum):
    WHITE = 0
    BLACK = 1

    @classmethod
    def second_color(cls, color):
        if color == cls.WHITE:
            return cls.BLACK
        elif color == cls.BLACK:
            return cls.WHITE


class Player:
    def __init__(self, color, balls, opponentThrone):
        self.color = color
        self.balls = balls
        self.opponentThrone = opponentThrone


class GameModel:
    numOfCells = 19

    initPlayer1BallPositions = [(11, 2), (11, 16), (18, 5), (18, 13), (13, 7), (13, 11), (17, 7), (17, 11)]
    initPlayer2BallPositions = [(7, 2), (7, 16), (0, 5), (0, 13), (5, 7), (5, 11), (1, 7), (1, 11)]

    player1ThronePos = (3, 9)
    player2ThronePos = (15, 9)

    player1Color = GameColor.BLACK

    wallsMap=None

    def __init__(self):
        self.player1 = Player(self.player1Color, self.initPlayer1BallPositions.copy(), self.player2ThronePos)
        self.player2 = Player(GameColor.second_color(self.player1Color), self.initPlayer2BallPositions.copy(), self.player1ThronePos)
        self.ballsMap = None
        self.model_state_init()
        self.activePlayer = self.player1


    def model_state_init(self):
        GameModel.wallsMap = np.array([[False]*self.numOfCells]*19, dtype=bool)
        self.wall_map_init()
        self.ballsMap = np.array([[None]*19]*19, dtype=GameColor)
        self.set_balls_map(self.initPlayer1BallPositions, self.initPlayer2BallPositions)

    def wall_map_init(self):
        wallsMap = GameModel.wallsMap
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

    def set_balls_map(self, player1_balls, player2_balls):
        self.ballsMap = np.array([[None]*19]*19, dtype=GameColor)
        for position in player1_balls:
            self.ballsMap[position] = self.player1.color
        for position in player2_balls:
            self.ballsMap[position] = self.player2.color

    def is_something_between(self, map: np.ndarray, startPos: tuple, endPos: tuple, direction, delta, negated=False):
        # negated parameter:
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
        isStartWall = GameModel.wallsMap[startPos]
        isEndWall = GameModel.wallsMap[endPos]
        if np.logical_xor(isStartWall, isEndWall):
            if abs(delta) > 1:
                return False
        elif not isStartWall and not isEndWall:
            if self.is_something_between(GameModel.wallsMap, startPos, endPos, direction, delta):
                return False
        else:
            if self.is_something_between(GameModel.wallsMap, startPos, endPos, direction, delta, True):
                return False
        if direction:
            if self.player1ThronePos[0] == startPos[0]:
                if min(startPos[1], endPos[1]) < self.player1ThronePos[1] < max(startPos[1], endPos[1]):
                    return False
            if self.player2ThronePos[0] == startPos[0]:
                if min(startPos[1], endPos[1]) < self.player2ThronePos[1] < max(startPos[1], endPos[1]):
                    return False
        else:
            if self.player1ThronePos[1] == startPos[1]:
                if min(startPos[0], endPos[0]) < self.player1ThronePos[0] < max(startPos[0], endPos[0]):
                    return False
            if self.player2ThronePos[1] == startPos[1]:
                if min(startPos[0], endPos[0]) < self.player2ThronePos[0] < max(startPos[0], endPos[0]):
                    return False

        return True

    def change_player(self):
        self.activePlayer = self.second_player()

    def second_player(self):
        if self.activePlayer == self.player1:
            return self.player2
        else:
            return self.player1

    def move_ball(self, startPos: tuple, endPos: tuple) -> bool:
        ballsMoving = self.activePlayer.balls
        if not self.valid_move(startPos, endPos):
            return False
        else:
            if self.ballsMap[endPos]:
                self.beat(endPos)
            self.ballsMap[startPos] = None
            self.ballsMap[endPos] = self.activePlayer.color
            ballsMoving[ballsMoving.index(startPos)] = endPos
            if self.activePlayer.opponentThrone == endPos:
                raise EndGame
            return True

    def beat(self, endPos: tuple):
        ballsFromWhichRemoving = self.second_player().balls
        ballsFromWhichRemoving.remove(endPos)

# Artificial intelligence core, finds best move and overwrites players bills positions
    def intelligent_move(self, depth):
        if self.activePlayer.color == 1:
            maximizingPlayer=True
        else:
            maximizingPlayer=False
        current_state = Node(self.player1.balls, self.player2.balls)
        best_child = self.min_max_algorythm(current_state, depth, maximizingPlayer)
        self.player1.balls=best_child.player1_balls.copy()
        self.player2.balls=best_child.player2_balls.copy()
        self.set_balls_map(self.player1.balls, self.player2.balls)

# min-max algorythm, it returns the greatest of the child nodes - depends on who is current active player
    def min_max_algorythm(self, node, depth, maximizingPlayer):
        nodes_evaluation=[]
        nodes_evaluation=nodes_evaluation+self.alphabeta_prunning_init(node, depth, -np.inf, np.inf, maximizingPlayer)
#        print("I have checked ", len(nodes_evaluation), " of possible movements to take")
        if maximizingPlayer:
            i=-np.inf
            for state_and_value in nodes_evaluation:
                if state_and_value[0]>i:
                    i=state_and_value[0]
                    best_node=state_and_value[1]
#            print("I am maximizing player and I chose one with max value which is", i)
            return best_node
        else:
            i=+np.inf
            for state_and_value in nodes_evaluation:
                if state_and_value[0]<i:
                    i=state_and_value[0]
                    best_node=state_and_value[1]
#            print("I am minimizing player and I chose one with min value which is", i)
            return best_node

# initilizing alphabetta prunning, returning nodes and evaluated value
    def alphabeta_prunning_init(self, node, depth, alfa, beta, maximizingPlayer):
        depth=depth-1
        new_nodes=node.generate_new_nodes(maximizingPlayer)
#        print("Number of generated child nodes ", len(new_nodes), "from level ", depth+1)
        nodes_and_values=[]
        if maximizingPlayer:
            for state in new_nodes:
                alfa=max(alfa, self.alphabeta_prunning(state,depth,alfa,beta, False))
                if alfa>=beta:
                    nodes_and_values.append((beta, state))
                else:
                    nodes_and_values.append((alfa, state))
        else:
            for state in new_nodes:
                beta=min(beta, self.alphabeta_prunning(state,depth,alfa,beta, True))
                if alfa>=beta:
                    nodes_and_values.append((alfa, state))
                else:
                    nodes_and_values.append((beta, state))
        return nodes_and_values

# alpha-beta prunning working in recursion, returns only value
    def alphabeta_prunning(self, node, depth, alfa, beta, maximizingPlayer):
# it takes at least 11 turns to reach terminal node,
        if depth==0 or node.terminal_node:
            return self.heuristic_function(node)
        depth=depth-1
        new_nodes=node.generate_new_nodes(maximizingPlayer)
#        print("Number of generated child nodes ", len(new_nodes), "from level ", depth+1)
        if maximizingPlayer:
            for state in new_nodes:
                alfa=max(alfa, self.alphabeta_prunning(state,depth,alfa,beta, False))
                if alfa>=beta:
                    return beta
            return alfa
        else:
            value=np.inf
            for state in new_nodes:
                beta=min(beta, self.alphabeta_prunning(state,depth,alfa,beta, True))
                if alfa>=beta:
                    return alfa
            return beta

# minimize player: WHITE, maximizing player: BLACK
    def heuristic_function(self, node):
        start_value=0
# checking balls positions, awarding those being in chosen areas of an enemy castle
        for ball in node.player2_balls:
            if ball[0] in range(0,18) and ball[1] in range(8,11):
                start_value-=5
            if ball[0] in range(2,17) and ball[1] in range(0,8):
                start_value-=10
            if ball[0] in range(5,14) and ball[1] in range(0,6):
                start_value-=10
            if ball[0] in range(7,12) and ball[1] in range(0,6):
                start_value-=10
            if ball==self.player1ThronePos:
                start_value-=1000000
        for ball in node.player1_balls:
            if ball[0] in range(0,18) and ball[1] in range(8,11):
                start_value+=5
            if ball[0] in range(2,17) and ball[1] in range(11,19):
                start_value+=10
            if ball[0] in range(5,14) and ball[1] in range(13,19):
                start_value+=10
            if ball[0] in range(7,12) and ball[1] in range(13,19):
                start_value+=10
            if ball==self.player2ThronePos:
                start_value+=1000000
# heuristic which awards player with bigger quantity of bills left
            start_value=start_value+(len(node.player1_balls)-len(node.player2_balls))*15
        return start_value

    def check_if_game_finish(self):
        for position in self.player1.balls:
            if position == self.player1ThronePos:
                print("Player black won!")
                return True
        for position in self.player2.balls:
            if position == self.player2ThronePos:
                print("Player white won!")
                return True
        return False

class Node(GameModel):
    def __init__(self, balls_1: list, balls_2: list, terminal_node=False):
        self.player1_balls=balls_1
        self.player2_balls=balls_2
        self.terminal_node=terminal_node

# function that finds child nodes, returns list of class Node objects
    def generate_new_nodes(self, maximizingPlayer) -> list:
        child_nodes=[]
        if maximizingPlayer:
            for ball in self.player1_balls:
                list_possible_endpos=self.find_possible_endpos(ball)
                while list_possible_endpos:
                    player1_balls_copy=self.player1_balls.copy()
                    player2_balls_copy=self.player2_balls.copy()
                    player1_balls_copy.remove(ball)
                    endpos=list_possible_endpos.pop(0)
                    player1_balls_copy.append(endpos)
                    if endpos in self.player2_balls:
                        player2_balls_copy.remove(endpos)
                    if endpos == self.player2ThronePos:
                        terminal_node=True
                        print("Terminal node found! Check..!")
                    else: terminal_node=False
                    child_nodes.append(Node(player1_balls_copy, player2_balls_copy, terminal_node))
        else:
            for ball in self.player2_balls:
                list_possible_endpos=self.find_possible_endpos(ball)
                while list_possible_endpos:
                    player1_balls_copy=self.player1_balls.copy()
                    player2_balls_copy=self.player2_balls.copy()
                    player2_balls_copy.remove(ball)
                    endpos=list_possible_endpos.pop(0)
                    player2_balls_copy.append(endpos)
                    if endpos in self.player1_balls:
                        player1_balls_copy.remove(endpos)
                    if endpos == self.player1ThronePos:
                        terminal_node=True
                        print("Terminal node found! Check..!")
                    else: terminal_node=False
                    child_nodes.append(Node(player1_balls_copy, player2_balls_copy, terminal_node))
        return child_nodes

# function that finds possible endpositions for ball position on input
    def find_possible_endpos(self, ball: tuple) -> list:
            list_endpos=[]
            i=ball[0]
            j=ball[1]
            for coordinate in range(j+1, 19):
                endPos=(i, coordinate)
                if self.valid_move(ball, endPos):
                    list_endpos.append(endPos)
                else: break
            for coordinate in range(i+1, 19):
                endPos=(coordinate, j)
                if self.valid_move(ball, endPos):
                    list_endpos.append(endPos)
                else: break
            for coordinate in range(0, i):
                endPos=(coordinate, j)
                if self.valid_move(ball, endPos):
                    list_endpos.append(endPos)
                else: break
            for coordinate in range(0, j):
                endPos=(i, coordinate)
                if self.valid_move(ball, endPos):
                    list_endpos.append(endPos)
                else: break
            return list_endpos
