import pygame
from pygame.locals import *
import os
import numpy as np
from enum import Enum

if not pygame.font:
    print("Warning, fonts disabled")
if not pygame.mixer:
    print("Warning, sound disabled")


class FunContainer:
    main_dir = os.path.split(os.path.abspath(__file__))[0]
    data_dir = os.path.join(main_dir, "resources")

    def __init__(self):
        pass

    @classmethod
    def load_image(cls, name, colorkey=None):
        fullname = os.path.join(cls.data_dir, name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error:
            print("Cannot load image {}".format(name))
            raise SystemExit
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image

    @classmethod
    def load_sound(cls, name):
        class NoneSound:
            def play(self): pass

        if not pygame.mixer:
            return NoneSound()
        fullname = os.path.join(cls.data_dir, name)
        try:
            sound = pygame.mixer.Sound(fullname)
        except pygame.error:
            print("Cannot load sound: {}".format(name))
            raise SystemExit
        return sound

    @classmethod
    def center_blit(cls, destination: pygame.Surface, image: pygame.Surface, area: pygame.Rect):
        imageRect = image.get_rect()
        imageRect.center = area.center
        destination.blit(image, imageRect)


class Ball(pygame.sprite.Sprite):
    resolution = (35, 35)

    def __init__(self):
        super().__init__()
        self.image = None
        self.imageBase = None
        self.imageOnFocus = None
        self.rect = None
        self.rectBase = None
        self.rectOnFocus = None
        self.boardPos = None
        self.color = None

    def on_init(self):
        self.imageOnFocus = pygame.transform.scale(self.image, (self.resolution[0] + 5, self.resolution[1] + 5))
        self.imageBase = pygame.transform.scale(self.image, (self.resolution[0], self.resolution[1]))
        self.image = self.imageBase
        self.rectOnFocus = self.imageOnFocus.get_rect()
        self.rectBase = self.imageBase.get_rect()
        self.rect = self.rectBase

    def set_position(self, rect: Rect, position):
        self.rect.center = rect.center
        self.boardPos = position

    def clicked(self):
        self.image = self.imageOnFocus
        center = self.rect.center
        self.rect = self.rectOnFocus
        self.rect.center = center

    def unclicked(self):
        self.image = self.imageBase
        center = self.rect.center
        self.rect = self.rectBase
        self.rect.center = center

    def update(self):
        pass


class WhiteBall(Ball):
    def __init__(self):
        super().__init__()
        self.image = FunContainer.load_image("white-ball.jpg", -1)
        self.color = GameColor.WHITE
        self.on_init()


class BlackBall(Ball):
    def __init__(self):
        super().__init__()
        self.image = FunContainer.load_image("black-ball.jpg", -1)
        self.color = GameColor.BLACK
        self.on_init()


class BallsContainer(pygame.sprite.RenderPlain):
    def __init__(self):
        super().__init__()
    
    def clicked_sprite(self, position):
        for sprite in self.sprites():
            if sprite.rect.collidepoint(position):
                return sprite
        return None


class GameColor(Enum):
    WHITE = 0
    BLACK = 1


class GameModel(FunContainer):
    windowWidth = 800
    windowHeight = 800
    marginWidth = 10
    marginHeight = 10
    numOfCells = 19
    cellWidth = np.floor_divide(windowWidth-2*marginWidth, numOfCells)
    marginWidth += np.floor_divide(np.remainder(windowWidth-2*marginWidth, numOfCells), 2)
    cellHeight = np.floor_divide(windowHeight-2*marginHeight, numOfCells)
    marginHeight += np.floor_divide(np.remainder(windowHeight-2*marginHeight, numOfCells), 2)
    linesColor = Color(25, 25, 110)
    windowName = "Castle game"

    def __init__(self):
        super().__init__()
        pygame.init()
        self.board = self.board_init()
        self.screen = pygame.display.set_mode((self.windowWidth, self.windowHeight))
        pygame.display.set_caption(self.windowName)
        self.background = FunContainer.load_image("background.jpg")
        self.background = pygame.transform.scale(self.background, (self.windowWidth, self.windowHeight))
        self.draw_lines()
        self.draw_thrones()
        self.wallsMap = self.wall_map_init()
        self.draw_walls()
        self.screen.blit(self.background, (0, 0))

        self.clock = pygame.time.Clock()

        self.ballsMap = np.array([[None]*19]*19, dtype=GameColor)
        self.blackBalls = BallsContainer()
        self.whiteBalls = BallsContainer()
        self.balls_init()

        self.blackBalls.draw(self.screen)
        self.whiteBalls.draw(self.screen)
        pygame.display.update()

        self.playerMoving = GameColor.WHITE
        self.ballsMoving = self.whiteBalls

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
        blueThrone = self.load_image("blue-throne.jpg", -1)
        redThrone = self.load_image("red-throne.jpg", -1)
        blueThrone = pygame.transform.scale(blueThrone, resolution)
        redThrone = pygame.transform.scale(redThrone, resolution)
        self.center_blit(self.background, blueThrone, Rect(self.board[3][9]))
        self.center_blit(self.background, redThrone, Rect(self.board[15][9]))

    def wall_map_init(self):
        wallsMap = np.array([[False]*self.numOfCells]*19, dtype=bool)
        for i in range(1, 8):
            wallsMap[(i, 2)] = True
            wallsMap[(i, 16)] = True
            wallsMap[(self.numOfCells-i-1, 2)] = True
            wallsMap[(self.numOfCells-i-1, 16)] = True
        for i in range(0, 6):
            wallsMap[(i, 5)] = True
            wallsMap[(i, 13)] = True
            wallsMap[(self.numOfCells-i-1, 5)] = True
            wallsMap[(self.numOfCells-i-1, 13)] = True
        for i in range(1, 6):
            wallsMap[(i, 7)] = True
            wallsMap[(i, 11)] = True
            wallsMap[(self.numOfCells-i-1, 7)] = True
            wallsMap[(self.numOfCells-i-1, 11)] = True
        for i in range(3, 9):
            wallsMap[(7, i)] = True
            wallsMap[(11, i)] = True
            wallsMap[(7, self.numOfCells-i-1)] = True
            wallsMap[(11, self.numOfCells-i-1)] = True
        for i in range(7, 12):
            wallsMap[(5, i)] = True
            wallsMap[(13, i)] = True
        wallsMap[(1, 8)] = True
        wallsMap[(1, 10)] = True
        wallsMap[(17, 8)] = True
        wallsMap[(17, 10)] = True
        return wallsMap


    def draw_walls(self):
        resolution = (40, 40)
        wallImage = self.load_image("wall.jpg")
        wallImage = pygame.transform.scale(wallImage, resolution)
        for i in range(self.numOfCells):
            for j in range(self.numOfCells):
                if self.wallsMap[i][j]:
                    self.center_blit(self.background, wallImage, Rect(self.board[(i, j)]))

    def balls_init(self):
        blackBallPositions = [(11, 2), (11, 16), (18, 5), (18, 13), (13, 7), (13, 11), (17, 7), (17, 11)]
        whiteBallPositions = [(7, 2), (7, 16), (0, 5), (0, 13), (5, 7), (5, 11), (1, 7), (1, 11)]

        for position in blackBallPositions:
            ball = BlackBall()
            self.place_ball(ball, position)
            self.blackBalls.add(ball)

        for position in whiteBallPositions:
            ball = WhiteBall()
            self.place_ball(ball, position)
            self.whiteBalls.add(ball)

    def change_player(self):
        if self.playerMoving == GameColor.WHITE:
            self.playerMoving = GameColor.BLACK
            self.ballsMoving = self.blackBalls
        else:
            self.playerMoving = GameColor.WHITE
            self.ballsMoving = self.whiteBalls
    
    def place_ball(self, ball: Ball, boardPos: tuple):
        self.ballsMap[boardPos] = ball.color
        ball.set_position(Rect(self.board[boardPos]), boardPos)

    def valid_move(self, ballColor: GameColor, startPos: tuple, endPos: tuple):
        dy = endPos[0] - startPos[0]
        dx = endPos[1] - startPos[1]
        delta = dy
        direction = 0
        if (dx or not dy) and (not dx or dy):
            return False
        if not dy:
            delta = dx
            direction = 1
        isStartWall = self.wallsMap[startPos]
        isEndWall = self.wallsMap[endPos]
        if (isStartWall and not isEndWall) or (not isStartWall and isEndWall):
            if abs(delta) > 1:
                return False
        return True


    def move_ball(self, ball: Ball, endPos: tuple) -> bool:
        startPos = ball.boardPos
        if not self.valid_move(ball.color, startPos, endPos):
            return False
        else:
            self.ballsMap[startPos] = None
            self.place_ball(ball, endPos)
            return True

    def view_update(self):
        self.blackBalls.update()
        self.blackBalls.clear(self.screen, self.background)
        self.blackBalls.draw(self.screen)

        self.whiteBalls.update()
        self.whiteBalls.clear(self.screen, self.background)
        self.whiteBalls.draw(self.screen)
        pygame.display.update()

