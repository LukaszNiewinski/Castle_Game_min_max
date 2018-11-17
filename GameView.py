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
        self.imageBase = None
        self.imageOnFocus = None
        self.rect = None
        self.rectBase = None
        self.rectOnFocus = None
        self.boardPos = None

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
    def __init__(self):
        super().__init__()
    
    def clicked_sprite(self, position):
        for sprite in self.sprites():
            if sprite.rect.collidepoint(position):
                return sprite
        return None


class Fire(pygame.sprite.Sprite):
    resolution = (50, 50)

    def __init__(self):
        super().__init__()
        self.image = FunContainer.load_image("fire.jpg", -1)
        self.image = pygame.transform.scale(self.image, self.resolution)
        self.rect = self.image.get_rect()
        self.muted = None

    def set_rect(self, rect):
        self.rect.center = rect.center


class Player:
    def __init__(self, color, balls, winningThrone, name):
        self.color = color
        self.balls = balls
        self.winningThrone = winningThrone
        self.name = name


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

    fileToSave = os.path.join(FunContainer.data_dir, "saved.game")

    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.gameModel = GameModel()

        self.board = self.board_init()
        self.screen = screen

        self.background = FunContainer.load_image("background.jpg")
        self.background = pygame.transform.scale(self.background, (self.windowWidth, self.windowHeight))
        self.draw_lines()
        self.draw_thrones()
        self.draw_walls()

        self.gauntlet = None
        self.fire = Fire()
        self.fireSound = FunContainer.load_sound("snow-ball.wav")

        self.blackBalls = None
        self.whiteBalls = None
        self.activePlayer = None

        self.whitePlayer = None
        self.blackPlayer = None

        self.muted = None

        self.reset_view_state()

    def new_game(self):
        self.gameModel.model_state_init()
        self.reset_view_state()

    def reset_view_state(self):
        self.blackBalls = BallsContainer()
        self.whiteBalls = BallsContainer()
        self.balls_init()
        self.activePlayer = self.player_init()

    def who_start_draw(self):
        text = "{} begins".format(self.activePlayer.name)
        textImage = FunContainer.font_render(text, 55)
        rect = Rect(0, 0, self.windowWidth, self.windowHeight - 55)
        FunContainer.center_blit(self.screen, textImage, rect)
        pygame.display.update()
        pygame.time.delay(1500)
        self.screen.blit(self.background, (0, 0))

    def init_draw(self):
        self.screen.blit(self.background, (0, 0))
        self.blackBalls.draw(self.screen)
        self.whiteBalls.draw(self.screen)
        self.who_start_draw()

    def player_init(self):
        self.whitePlayer = Player(GameColor.WHITE, self.whiteBalls, self.gameModel.whiteThronePos, "White player")
        self.blackPlayer = Player(GameColor.BLACK, self.blackBalls, self.gameModel.blackThronePos, 'Black player')
        if self.gameModel.activeColor == GameColor.WHITE:
            return self.whitePlayer
        else:
            return self.blackPlayer

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
        FunContainer.center_blit(self.background, blueThrone, Rect(self.board[self.gameModel.blackThronePos]))
        FunContainer.center_blit(self.background, redThrone, Rect(self.board[self.gameModel.whiteThronePos]))

    def draw_walls(self):
        resolution = (42, 42)
        wallImage = FunContainer.load_image("wall.jpg")
        wallImage = pygame.transform.scale(wallImage, resolution)
        for i in range(self.numOfCells):
            for j in range(self.numOfCells):
                if self.gameModel.wallsMap[i][j]:
                    FunContainer.center_blit(self.background, wallImage, Rect(self.board[(i, j)]))

    def balls_init(self):
        for i in range(self.numOfCells):
            for j in range(self.numOfCells):
                if self.gameModel.ballsMap[(i, j)]:
                    if self.gameModel.ballsMap[(i, j)] == GameColor.WHITE:
                        ball = WhiteBall()
                        self.place_ball(ball, (i, j))
                        self.whiteBalls.add(ball)
                    else:
                        ball = BlackBall()
                        self.place_ball(ball, (i, j))
                        self.blackBalls.add(ball)

    def view_update(self):
        self.screen.blit(self.background, self.gauntlet.rect, self.gauntlet.rect)

        self.blackBalls.update()
        self.blackBalls.clear(self.screen, self.background)
        self.blackBalls.draw(self.screen)

        self.whiteBalls.update()
        self.whiteBalls.clear(self.screen, self.background)
        self.whiteBalls.draw(self.screen)

        self.gauntlet.update()
        self.screen.blit(self.gauntlet.image, self.gauntlet.rect)

        pygame.display.update()

    def change_player(self):
        if self.activePlayer == self.blackPlayer:
            self.activePlayer = self.whitePlayer
            self.gameModel.activeColor = GameColor.WHITE
        else:
            self.activePlayer = self.blackPlayer
            self.gameModel.activeColor = GameColor.BLACK
    
    def place_ball(self, ball: Ball, boardPos: tuple):
        self.gameModel.ballsMap[boardPos] = ball.color
        ball.set_position(Rect(self.board[boardPos]), boardPos)

    def beat(self, boardPos: tuple, ballColor: GameColor):
        ballsContainer = None
        if ballColor == GameColor.WHITE:
            ballsContainer = self.whiteBalls
        else:
            ballsContainer = self.blackBalls
        rect = Rect(self.board[boardPos])
        sprite = ballsContainer.clicked_sprite(rect.center)
        if not self.muted:
            self.fireSound.play()
        sprite.kill()
        self.fire.set_rect(rect)
        FunContainer.center_blit(self.screen, self.fire.image, self.fire.rect)
        pygame.display.update()
        pygame.time.delay(500)
        self.screen.blit(self.background, self.fire.rect, self.fire.rect)

    def move_ball(self, ball: Ball, endPos: tuple) -> bool:
        startPos = ball.boardPos
        if not self.gameModel.valid_move(startPos, endPos):
            return False
        else:
            if self.gameModel.ballsMap[endPos]:
                self.beat(endPos, GameColor.second_color(ball.color))
            self.gameModel.ballsMap[startPos] = None
            self.place_ball(ball, endPos)
            if self.activePlayer.winningThrone == endPos:
                self.end_game()
            return True

    def end_game(self):
        self.view_update()
        pygame.time.delay(500)
        text = "{} won that round".format(self.activePlayer.name)
        text2 = "Congratulations !"
        textImage = FunContainer.font_render(text, 55)
        textImage2 = FunContainer.font_render(text2, 55)
        rect = Rect(0, 0, self.windowWidth, self.windowHeight - 125)

        FunContainer.center_blit(self.screen, textImage, rect)
        FunContainer.center_blit(self.screen, textImage2, self.screen.get_rect())
        self.fire.set_rect(Rect(self.board[self.activePlayer.winningThrone]))
        self.screen.blit(self.fire.image, self.fire.rect)
        pygame.display.update()
        pygame.time.delay(3000)
        raise SystemExit

    def save_game(self):
        text = str()
        try:
            with open(self.fileToSave, 'wb') as file:
                pickle.dump(self.gameModel, file)
                text = "Game saved"
        except:
            text = "Cannot write to file"
        finally:
            textImage = FunContainer.font_render(text, 55)
            rect = Rect(0, 0, self.windowWidth, self.windowHeight - 55)
            FunContainer.center_blit(self.screen, textImage, rect)
            pygame.display.update()
            pygame.time.delay(2000)
            self.screen.blit(self.background, (0, 0))

    def load_game(self):
        text = str()
        try:
            with open(self.fileToSave, 'rb') as file:
                self.gameModel = pickle.load(file)
                text = "Game loaded"
                self.reset_view_state()
        except:
            text = "Cannot open file"
        finally:
            textImage = FunContainer.font_render(text, 55)
            rect = Rect(0, 0, self.windowWidth, self.windowHeight - 55)
            FunContainer.center_blit(self.screen, textImage, rect)
            pygame.display.update()
            pygame.time.delay(1500)
            self.screen.blit(self.background, (0, 0))
            self.who_start_draw()
