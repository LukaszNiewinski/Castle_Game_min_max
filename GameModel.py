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
    #    if self.is_something_between(self.ballsMap, startPos, endPos, direction, delta):
    #        return False
    #    if self.balls_Map[endPos]:
    #        if self.balls_Map[endPos] == self.activePlayer.color:
    #            return False
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

#funkcja odpowiadajaca za znalezienie najlepszego stanu potomnego
    def intelligent_move(self, depth):
        print("Nareszcie moja tura! Jestem obiektem klasy artificial intelligence a moje imie to TwojaPorazkaIsComing! ")
        current_state = Node(self.player1.balls, self.player2.balls)
        best_child = self.min_max_algorythm(current_state, depth, False) #zamiast false: self.activePlayer.color
        self.player1.balls=best_child.player1_balls
        self.player2.balls=best_child.player2_balls
        print("pozycje bill gracza czarnego w nowym stanie:", best_child.player1_balls)
        print("pozycje bill gracza bialego w nowym stanie:", best_child.player2_balls)
        self.set_balls_map(self.player1.balls, self.player2.balls)

#algorytm min_max wybierający - w zależności od aktywnego gracza stan max albo stan min
    def min_max_algorythm(self, node, depth, activePlayer):
        nodes_evaluation=[]
        print("Na swoj uzytek wywoluje algorytm min max!")
        nodes_evaluation=nodes_evaluation+self.alphabeta_prunning_init(node, depth, -np.inf, np.inf, activePlayer)
        print("Sprawdzilem ", len(nodes_evaluation), " mozliwych nastepnych ruchow")
        if activePlayer:
            i=-np.inf
            for state_and_value in nodes_evaluation:
                if state_and_value[0]>i:
                    i=state_and_value[0]
                    best_node=state_and_value[1]
            print("..i wybralem najlepszy z nich!")
            return best_node
        else:
            i=+np.inf
            for state_and_value in nodes_evaluation:
                if state_and_value[0]<i:
                    i=state_and_value[0]
                    best_node=state_and_value[1]
            print("..i wybralem najlepszy z nich!")
            return best_node

#początkowa funkcja wywołująca obcinanie alfa-beta, zwraca node wraz z oceną
    def alphabeta_prunning_init(self, node, depth, alfa, beta, maximizingPlayer):
        depth=depth-1
        print("By szybciej Cie zniszczyc wywoluje rowniez funkcje alfa_beta!")
        new_nodes=node.generate_new_nodes(maximizingPlayer)
        print("liczba wygenerowanych child nodes: ", len(new_nodes), "na poziomie -", depth)
        nodes_and_values=[]
        if maximizingPlayer:
            for state in new_nodes:
                new_nodes.remove(state)
                alfa=max(alfa, self.alphabeta_prunning(state,depth,alfa,beta, False))
                if alfa>=beta:
                    nodes_and_values.append((beta, state))
                else:
                    nodes_and_values.append((alfa, state))
        else:
            for state in new_nodes:
                new_nodes.remove(state)
                beta=min(beta, self.alphabeta_prunning(state,depth,alfa,beta, True))
                if alfa>=beta:
                    nodes_and_values.append((alfa, state))
                else:
                    nodes_and_values.append((beta, state))
        return nodes_and_values

#obcinanie alfa-beta działajace rekurencyjnie, zwraca jedynie wartosc
    def alphabeta_prunning(self, node, depth, alfa, beta, maximizingPlayer):
        if depth==0: # or terminal_node: potrzeba minimum 11 tur aby osiągnąć stan terminalny
             return self.heuristic_function(node)
        depth=depth-1
        new_nodes=node.generate_new_nodes(maximizingPlayer)
        print("liczba wygenerowanych child nodes: ", len(new_nodes), "na poziomie -", depth)
        if maximizingPlayer:
            for state in new_nodes:
                new_nodes.remove(state)
                alfa=max(alfa, self.alphabeta_prunning(state,depth,alfa,beta, False))
                if alfa>=beta:
                    return beta
                else:
                    return alfa
        else:
            value=np.inf
            for state in new_nodes:
                new_nodes.remove(state)
                beta=min(beta, self.alphabeta_prunning(state,depth,alfa,beta, True))
                if alfa>=beta:
                    return alfa
                else:
                    return beta

#czarny gracz minimalizuje, bialy gracz maksymalizuje
    def heuristic_function(self, node):
        start_value=10000
    #sprawdzenie i punktowanie obecności kul w różnych obszarach
        for ball in node.player1_balls:
            if ball[0] in range(0,18) and ball[1] in range(8,11):
                start_value-=500
            if ball[0] in range(2,17) and ball[1] in range(0,8):
                start_value-=1000
            if ball[0] in range(5,14) and ball[1] in range(0,6):
                start_value-=1000
            if ball[0] in range(7,12) and ball[1] in range(0,6):
                start_value-=1000
            if ball==self.player2ThronePos:
                start_value-=100000
        for ball in node.player2_balls:
            if ball[0] in range(0,18) and ball[1] in range(8,11):
                start_value+=1000
            if ball[0] in range(2,17) and ball[1] in range(11,19):
                start_value+=2000
            if ball[0] in range(5,14) and ball[1] in range(13,19):
                start_value+=2000
            if ball[0] in range(7,12) and ball[1] in range(13,19):
                start_value+=2000
            if ball==self.player2ThronePos:
                start_value+=100000
        #premiowanie gracza z większą ilością bil
            start_value=start_value+(len(node.player2_balls)-len(node.player1_balls))*20000
        return start_value


class Node(GameModel):
    def __init__(self, balls_1: list, balls_2: list):
        self.player1_balls=balls_1
        self.player2_balls=balls_2

#funkcja znajdujaca stany potomne, generuje w postaci list obiektow klasy Node
    def generate_new_nodes(self, activePlayer) -> list:
        child_nodes=[]
        if activePlayer:
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
                    if endpos == GameModel.player2ThronePos:
                        print("Szach..!")
                    child_nodes.append(Node(player1_balls_copy, player2_balls_copy))
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
                    if endpos == GameModel.player1ThronePos:
                        print("Szach..!")
                    child_nodes.append(Node(player1_balls_copy, player2_balls_copy))
        return child_nodes

#funkcja znajdujaca mozliwe ruchy(endPos'itions) bili podanej na wejsciu
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
