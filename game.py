import pygame
from pygame.locals import *
import sys, os
import numpy as np

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


class WhiteBall(pygame.sprite.Sprite):
    resolution = (35, 35)

    def __init__(self):
        super().__init__()
        self.image = FunContainer.load_image("white-ball.jpg", -1)
        self.imageOnFocus = pygame.transform.scale(self.image, (self.resolution[0]+5, self.resolution[1]+5))
        self.imageBase = pygame.transform.scale(self.image, (self.resolution[0], self.resolution[1]))
        self.image = self.imageBase
        self.rect = self.image.get_rect()

        self.clicked = False

    def set_position(self, rect: Rect):
        self.rect.center = rect.center

    def update(self):
        pass

    def click(self):
        self.clicked = True

    def unclick(self):
        self.clicked = False


class BlackBall(WhiteBall):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = FunContainer.load_image("black-ball.jpg", -1)
        self.imageOnFocus = pygame.transform.scale(self.image, (self.resolution[0]+5, self.resolution[1]+5))
        self.imageBase = pygame.transform.scale(self.image, (self.resolution[0], self.resolution[1]))
        self.image = self.imageBase
        self.rect = self.image.get_rect()
        self.rect.move_ip(200, 100)


class App(FunContainer):
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
        self.wallMap = self.wall_map_init()
        self.draw_walls()
        self.screen.blit(self.background, (0, 0))
        pygame.display.update()

        self.clock = pygame.time.Clock()

        self.blackBalls = pygame.sprite.RenderPlain()
        self.blackBalls_init()
        self.whiteBalls = pygame.sprite.RenderPlain()
        self.whiteBalls_init()

        self.app_loop()

    def board_init(self):
        board = np.array([[Rect([0]*4)]*self.numOfCells]*self.numOfCells)
        for i in range(self.numOfCells):
            for j in range(self.numOfCells):
                board[j][i] = Rect(i*self.cellWidth+self.marginWidth, j*self.cellHeight+self.marginHeight, self.cellWidth-1, self.cellHeight-1)
        return board

    def position2board(self, pos):
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
        wallMap = np.array([[False]*self.numOfCells]*19)
        for i in range(1, 8):
            wallMap[(i, 2)] = True
            wallMap[(i, 16)] = True
            wallMap[(self.numOfCells-i-1, 2)] = True
            wallMap[(self.numOfCells-i-1, 16)] = True
        for i in range(0, 6):
            wallMap[(i, 5)] = True
            wallMap[(i, 13)] = True
            wallMap[(self.numOfCells-i-1, 5)] = True
            wallMap[(self.numOfCells-i-1, 13)] = True
        for i in range(1, 6):
            wallMap[(i, 7)] = True
            wallMap[(i, 11)] = True
            wallMap[(self.numOfCells-i-1, 7)] = True
            wallMap[(self.numOfCells-i-1, 11)] = True
        for i in range(3, 9):
            wallMap[(7, i)] = True
            wallMap[(11, i)] = True
            wallMap[(7, self.numOfCells-i-1)] = True
            wallMap[(11, self.numOfCells-i-1)] = True
        for i in range(7, 12):
            wallMap[(5, i)] = True
            wallMap[(13, i)] = True
        wallMap[(1, 8)] = True
        wallMap[(1, 10)] = True
        wallMap[(17, 8)] = True
        wallMap[(17, 10)] = True
        return wallMap

    def draw_walls(self):
        resolution = (40, 40)
        wallImage = self.load_image("wall.jpg")
        wallImage = pygame.transform.scale(wallImage, resolution)
        for i in range(self.numOfCells):
            for j in range(self.numOfCells):
                if self.wallMap[i][j]:
                    self.center_blit(self.background, wallImage, Rect(self.board[(i, j)]))

    def blackBalls_init(self):
        blackBallPositions = [(11, 2), (11, 16), (18, 5), (18, 13), (13, 7), (13, 11), (17, 7), (17, 11)]
        for position in blackBallPositions:
            ball = BlackBall()
            ball.set_position(Rect(self.board[position]))
            self.blackBalls.add(ball)

    def whiteBalls_init(self):
        blackBallPositions = [(7, 2), (7, 16), (0, 5), (0, 13), (5, 7), (5, 11), (1, 7), (1, 11)]
        for position in blackBallPositions:
            ball = WhiteBall()
            ball.set_position(Rect(self.board[position]))
            self.whiteBalls.add(ball)


    def app_loop(self):
        while 1:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    onboard = self.position2board(pos)
                    print(onboard)
                    print(self.board[onboard[0]][onboard[1]])

            self.blackBalls.update()
            self.blackBalls.clear(self.screen, self.background)
            self.blackBalls.draw(self.screen)

            self.whiteBalls.update()
            self.whiteBalls.clear(self.screen, self.background)
            self.whiteBalls.draw(self.screen)
            pygame.display.update()


if __name__ == "__main__":
    App()

