import pygame
from pygame.locals import *

import pickle

from GameModel import *
from GameMenu import *

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")


class Ball(pygame.sprite.Sprite):
    resolution = (35, 35)
    color = None

    def __init__(self):
        super().__init__()
        self.image = None
        self.rect = None

    def on_init(self):
        self.image = pygame.transform.scale(self.image, (self.resolution[0], self.resolution[1]))
        self.rect = self.image.get_rect()


class WhiteBall(Ball):
    color = GameColor.WHITE

    def __init__(self):
        super().__init__()
        self.image = FunContainer.load_image("white-ball.jpg", -1)
        self.on_init()


class BlackBall(Ball):
    color = GameColor.BLACK

    def __init__(self):
        super().__init__()
        self.image = FunContainer.load_image("black-ball.jpg", -1)
        self.on_init()


class BallsContainer(pygame.sprite.RenderPlain):
    def __init__(self, ballsList):
        super().__init__()
        self.ballsList = ballsList


class GameView:
    windowWidth = GameMenu.windowWidth
    windowHeight = GameMenu.windowHeight
    marginWidth = 10
    marginHeight = 10

    numOfCells = GameModel.numOfCells

    cellWidth = np.floor_divide(windowWidth-2*marginWidth, numOfCells)
    marginWidth += np.floor_divide(np.remainder(windowWidth-2*marginWidth, numOfCells), 2)
    cellHeight = np.floor_divide(windowHeight-2*marginHeight, numOfCells)
    marginHeight += np.floor_divide(np.remainder(windowHeight-2*marginHeight, numOfCells), 2)
    linesColor = (25, 25, 110)

    def __init__(self, screen: pygame.Surface, gameModel: GameModel):
        super().__init__()
        self.gameModel = gameModel

        self.board = self.board_init()
        self.screen = screen

        self.background = FunContainer.load_image("background.jpg")
        self.background = pygame.transform.scale(self.background, (self.windowWidth, self.windowHeight))
        self.draw_lines()
        self.draw_thrones()
        self.draw_walls()

        self.gauntlet = None

        self.blackBalls = None
        self.whiteBalls = None

        self.balls_init()
        self.init_draw()

    def balls_init(self):
        if self.gameModel.player1.color == GameColor.BLACK:
            blackBalls = self.gameModel.player1.balls
            whiteBalls = self.gameModel.player2.balls
        else:
            blackBalls = self.gameModel.player2.balls
            whiteBalls = self.gameModel.player1.balls
        self.blackBalls = BallsContainer(blackBalls)
        self.whiteBalls = BallsContainer(whiteBalls)
        for position in self.blackBalls.ballsList:
            blackBall = BlackBall()
            blackBall.rect.center = Rect(self.board[position]).center
            self.blackBalls.add(blackBall)
        for position in self.whiteBalls.ballsList:
            whiteBall = WhiteBall()
            whiteBall.rect.center = Rect(self.board[position]).center
            self.whiteBalls.add(whiteBall)

    def balls_update(self):
        activeColor = self.gameModel.activePlayer.color
        if activeColor == GameColor.WHITE:
            numOfSprites = len(self.blackBalls)
            numOfBalls = len(self.blackBalls.ballsList)
            balls = self.whiteBalls
            opballs = self.blackBalls
        else:
            numOfSprites = len(self.whiteBalls)
            numOfBalls = len(self.whiteBalls.ballsList)
            balls = self.blackBalls
            opballs = self.whiteBalls
        if numOfBalls != numOfSprites:
            opballs.sprites()[0].kill()
        for i in range(len(balls)):
            balls.sprites()[i].rect.center = Rect(self.board[balls.ballsList[i]]).center

    def init_draw(self):
        self.screen.blit(self.background, (0, 0))
        self.blackBalls.draw(self.screen)
        self.whiteBalls.draw(self.screen)

    def board_init(self):
        board = np.array([[Rect([0]*4)]*self.numOfCells]*self.numOfCells)
        for i in range(self.numOfCells):
            for j in range(self.numOfCells):
                board[j][i] = Rect(i*self.cellWidth+self.marginWidth, j*self.cellHeight+self.marginHeight, self.cellWidth-1, self.cellHeight-1)
        return board

    def cartesian2board(self, pos):
        x = np.floor_divide(pos[1] - self.marginWidth, self.cellWidth)
        if x >= self.numOfCells:
            x = self.numOfCells - 1
        elif x <= 0:
            x = 0
        y = np.floor_divide(pos[0] - self.marginHeight, self.cellHeight)
        if y >= self.numOfCells:
            y = self.numOfCells - 1
        elif y <= 0:
            y = 0
        return x, y

    def draw_lines(self):
        for i in range(self.numOfCells):
            start = Rect(self.board[i][0]).center
            stop = Rect(self.board[i][self.numOfCells-1]).center
            pygame.draw.line(self.background, self.linesColor, start, stop, 1)
        for j in range(self.numOfCells):
            start = Rect(self.board[0][j]).center
            stop = Rect(self.board[self.numOfCells-1][j]).center
            pygame.draw.line(self.background, self.linesColor, start, stop, 1)

    def draw_thrones(self):
        resolution = (60, 60)
        blueThrone = FunContainer.load_image("blue-throne.jpg", -1)
        redThrone = FunContainer.load_image("red-throne.jpg", -1)
        blueThrone = pygame.transform.scale(blueThrone, resolution)
        redThrone = pygame.transform.scale(redThrone, resolution)
        FunContainer.center_blit(self.background, blueThrone, Rect(self.board[self.gameModel.player1ThronePos]))
        FunContainer.center_blit(self.background, redThrone, Rect(self.board[self.gameModel.player2ThronePos]))

    def draw_walls(self):
        resolution = (42, 42)
        wallImage = FunContainer.load_image("wall.jpg")
        wallImage = pygame.transform.scale(wallImage, resolution)
        for i in range(self.numOfCells):
            for j in range(self.numOfCells):
                if self.gameModel.wallsMap[i][j]:
                    FunContainer.center_blit(self.background, wallImage, Rect(self.board[(i, j)]))

    def view_update(self):
        self.screen.blit(self.background, self.gauntlet.rect, self.gauntlet.rect)

        self.blackBalls.clear(self.screen, self.background)
        self.blackBalls.draw(self.screen)

        self.whiteBalls.clear(self.screen, self.background)
        self.whiteBalls.draw(self.screen)

        self.gauntlet.update()
        self.screen.blit(self.gauntlet.image, self.gauntlet.rect)

        pygame.display.update()

