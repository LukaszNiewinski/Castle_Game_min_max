from GameView import *
from GameMenu import *
from GameOptions import *
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

    def __init__(self, game: GameView, gameMenu: GameMenu): #,gameOptions: GameOptions):
        self.muted = False

        self.gauntlet = Gauntlet()
        self.gauntlet.muted = self.muted

        self.game = game
        self.game.muted = self.muted
        self.game.gauntlet = self.gauntlet
        self.gameMenu = gameMenu
        self.gameMenu.gauntlet = self.gauntlet
        # self.gameOptions = gameOptions
        # self.gameOptions.gauntlet = self.gauntlet

        self.gameMenu.playButton.action = self.main_game
        # self.gameMenu.optionsButton.action = self.main_options
        self.gameMenu.quitButton.action = self.exit

        # self.gameOptions.backToMenuButton.action = self.main_menu
        # self.gameOptions.soundButton.action = self.on_off_sound
        # self.gameOptions.changePlayerButton.action = self.change_player
        #
        # self.gameOptions.soundIndicator.set_state(self.muted)
        # self.set_player_indicator()

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
        self.game.init_draw()
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
                    pos = pygame.mouse.get_pos()
                    if not spriteClicked:
                        spriteClicked = self.game.activePlayer.balls.clicked_sprite(pos)
                        if spriteClicked:
                            spriteClicked.clicked()
                    else:
                        pos = self.game.cartesian2board(pos)
                        try:
                            if self.game.move_ball(spriteClicked, pos):
                                self.game.change_player()
                        except(SystemExit):
                            exit(0)
                            # self.game.new_game()
                            # self.set_player_indicator()
                            # self.main_menu()
                        spriteClicked.unclicked()
                        spriteClicked = None
                elif event.type == MOUSEBUTTONUP:
                    self.gauntlet.unclicked()
            self.game.view_update()

    # def main_options(self):
    #     pygame.time.delay(500)
    #     self.gameOptions.init_draw()
    #     while True:
    #         self.clock.tick(self.FPS)
    #         for event in pygame.event.get():
    #             if event.type == QUIT:
    #                 self.exit()
    #             elif event.type == KEYDOWN and event.key == K_ESCAPE:
    #                 self.main_menu()
    #             elif event.type == MOUSEBUTTONDOWN:
    #                 self.gauntlet.clicked()
    #                 pos = pygame.mouse.get_pos()
    #                 spriteClicked = self.gameOptions.allButtons.focused_sprite(pos)
    #                 if spriteClicked:
    #                     self.gameOptions.view_update()
    #                     spriteClicked.action()
    #             elif event.type == MOUSEBUTTONUP:
    #                 self.gauntlet.unclicked()
    #         self.gameOptions.view_update()

    # def set_player_indicator(self):
    #     state = False
    #     if self.game.gameModel.activeColor == GameColor.BLACK:
    #         state = True
    #
    #     self.gameOptions.changePlayerIndicator.set_state(state)
    #
    # def change_player(self):
    #     self.gameOptions.changePlayerIndicator.change_state()
    #     self.game.change_player()
    #
    # def on_off_sound(self):
    #     self.gameOptions.soundIndicator.change_state()
    #     if self.muted:
    #         pygame.mixer.unpause()
    #         pygame.mixer.music.play()
    #         self.muted = False
    #     else:
    #         pygame.mixer.music.stop()
    #         pygame.mixer.pause()
    #         self.muted = True
    #     self.game.muted = self.muted
    #     self.gauntlet.muted = self.muted

    @classmethod
    def exit(cls):
        pygame.time.delay(500)
        pygame.quit()
        sys.exit(0)



