from GameView import *
from GameMenu import *
from GameModel import *
import sys


class Gauntlet(pygame.sprite.Sprite):
    resolution = (60, 60)

    def __init__(self):
        super().__init__()
        self.image = FunContainer.load_image("gauntlet.jpg", -1)
        self.clickedImage = pygame.transform.scale(self.image, (self.resolution[0]-8, self.resolution[1]-8))
        self.normalImage = pygame.transform.scale(self.image, self.resolution)
        self.image = self.normalImage
        self.rect = self.image.get_rect()
        pygame.mouse.set_visible(False)
        self.clickedSound = FunContainer.load_sound("click.wav")
        self.muted = None

    def update(self):
        self.rect.midtop = pygame.mouse.get_pos()

    def clicked(self):
        if not self.muted:
            self.clickedSound.play()
        self.image = self.clickedImage

    def unclicked(self):
        self.image = self.normalImage


class GameController:
    FPS = 30
    music = "stronghold.mp3"

    def __init__(self, gameView: GameView, gameMenu: GameMenu):
        self.muted = False

        self.gauntlet = Gauntlet()
        self.gauntlet.muted = self.muted

        self.gameView = gameView
        self.gameView.gauntlet = self.gauntlet

        self.gameModel = self.gameView.gameModel

        self.gameMenu = gameMenu
        self.gameMenu.gauntlet = self.gauntlet

        self.gameMenu.playButton.action = self.player_vs_computer
        self.gameMenu.quitButton.action = self.exit

        self.clock = pygame.time.Clock()

        pygame.mixer.music.load(os.path.join(FunContainer.data_dir, self.music))

    def main_menu(self):
        if not pygame.mixer.music.get_busy() and not self.muted:
            pygame.mixer.music.play(-1)
        pygame.time.delay(500)
        self.gameMenu.init_draw()
        while True:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.exit()
                elif event.type == MOUSEBUTTONDOWN:
                    self.gauntlet.clicked()
                    pos = pygame.mouse.get_pos()
                    spriteClicked = self.gameMenu.allButtons.focused_sprite(pos)
                    if spriteClicked:
                        self.gameMenu.view_update()
                        spriteClicked.action()
                elif event.type == MOUSEBUTTONUP:
                    self.gauntlet.unclicked()
            self.gameMenu.view_update()

    def main_game(self):
        pygame.time.delay(500)
        pygame.mixer.music.stop()
        self.gameView.init_draw()
        spriteClicked = None
        while True:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()
                # elif event.type == KEYDOWN and event.key == K_ESCAPE:
                #     self.game.new_game()
                #     self.set_player_indicator()
                #     self.main_menu()
                # elif event.type == KEYDOWN and event.key == K_s:
                #     self.game.save_game()
                # elif event.type == KEYDOWN and event.key == K_l:
                #     self.game.load_game()
                elif event.type == MOUSEBUTTONDOWN:
                    self.gauntlet.clicked()
                    if not spriteClicked:
                        pos1 = pygame.mouse.get_pos()
                        pos1 = self.gameView.cartesian2board(pos1)
                        ballsClickedColor = self.gameModel.ballsMap[pos1]
                        if ballsClickedColor == self.gameModel.activePlayer.color:
                            spriteClicked = True
                            print("bill taken correctly")
                    else:
                        pos2 = pygame.mouse.get_pos()
                        pos2 = self.gameView.cartesian2board(pos2)
                        try:
                            if self.gameModel.move_ball(pos1, pos2):
                                self.gameView.balls_update()
                                if self.gameModel.check_if_game_finish():
                                    raise EndGame
                                self.gameModel.change_player()
                                print("bill moved corectly")
                        except(SystemExit):
                            exit(0)
                            # self.game.new_game()
                            # self.set_player_indicator()
                            # self.main_menu()
                        spriteClicked = False
                elif event.type == MOUSEBUTTONUP:
                    self.gauntlet.unclicked()
            self.gameView.view_update()

    def player_vs_computer(self):
        pygame.time.delay(500)
        pygame.mixer.music.stop()
        self.gameView.init_draw()
        spriteClicked = None
        player1Turn = True
        while True:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()
                # elif event.type == KEYDOWN and event.key == K_ESCAPE:
                #     self.game.new_game()
                #     self.set_player_indicator()
                #     self.main_menu()
                # elif event.type == KEYDOWN and event.key == K_s:
                #     self.game.save_game()
                # elif event.type == KEYDOWN and event.key == K_l:
                #     self.game.load_game()
                if player1Turn:
                    if event.type == MOUSEBUTTONDOWN:
                        self.gauntlet.clicked()
                        if not spriteClicked:
                            pos1 = pygame.mouse.get_pos()
                            pos1 = self.gameView.cartesian2board(pos1)
                            ballsClickedColor = self.gameModel.ballsMap[pos1]
                            if ballsClickedColor == self.gameModel.activePlayer.color:
                                spriteClicked = True
                                print("Sprite clicked")
                        else:
                            pos2 = pygame.mouse.get_pos()
                            pos2 = self.gameView.cartesian2board(pos2)
                            try:
                                if self.gameModel.move_ball(pos1, pos2):
                                    self.gameView.balls_update()
                                    self.gameModel.change_player()
                                    player1Turn = False
                                    print("player changed")
                            except(SystemExit):
                                exit(0)
                                # self.game.new_game()
                                # self.set_player_indicator()
                                # self.main_menu()
                            print("Sprite unclicked")
                            spriteClicked = False
                    elif event.type == MOUSEBUTTONUP:
                        self.gauntlet.unclicked()
                else:
                    #funkcja inteligent move, atrybut to parametr określający głębokość drzewa przeszukiwania
                    self.gameModel.intelligent_move(5)
                    self.gameView.balls_update()
                    if self.gameModel.check_if_game_finish():
                        raise EndGame
                    self.gameModel.change_player()
                    player1Turn = True
            self.gameView.view_update()

    @classmethod
    def exit(cls):
        pygame.time.delay(500)
        pygame.quit()
        sys.exit(0)
