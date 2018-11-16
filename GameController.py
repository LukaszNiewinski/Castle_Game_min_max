from GameView import *
from GameMenu import *
from GameOptions import *
import sys


class Gauntlet(pygame.sprite.Sprite):
    resolution = (60, 60)

    def __init__(self):
        super().__init__()
        self.image = FunContainer.load_image("gauntlet2.jpg", -1)
        self.clickedImage = pygame.transform.scale(self.image, (self.resolution[0]-8, self.resolution[1]-8))
        self.normalImage = pygame.transform.scale(self.image, self.resolution)
        self.image = self.normalImage
        self.rect = self.image.get_rect()
        pygame.mouse.set_visible(False)

    def update(self):
        self.rect.midtop = pygame.mouse.get_pos()

    def clicked(self):
        self.image = self.clickedImage

    def unclicked(self):
        self.image = self.normalImage


class GameController:
    FPS = 30

    def __init__(self, game: GameView, gameMenu: GameMenu, gameOptions: GameOptions):
        self.gauntlet = Gauntlet()
        self.game = game
        self.game.gauntlet = self.gauntlet
        self.gameMenu = gameMenu
        self.gameMenu.gauntlet = self.gauntlet
        self.gameOptions = gameOptions
        self.gameOptions.gauntlet = self.gauntlet

        self.gameMenu.playButton.action = self.main_game
        self.gameMenu.optionsButton.action = self.main_options
        self.gameMenu.quitButton.action = self.exit

        self.gameOptions.backToMenuButton.action = self.main_menu
        self.clock = pygame.time.Clock()

    def main_menu(self):
        pygame.time.delay(500)
        self.gameMenu.init_draw()
        while 1:
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
        self.game.init_draw()
        spriteClicked = None
        while 1:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.game.new_game()
                    self.main_menu()
                elif event.type == KEYDOWN and event.key == K_s:
                    self.game.save_game()
                elif event.type == KEYDOWN and event.key == K_l:
                    self.game.load_game()
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
                            self.game.new_game()
                            self.main_menu()
                        spriteClicked.unclicked()
                        spriteClicked = None
                elif event.type == MOUSEBUTTONUP:
                    self.gauntlet.unclicked()
            self.game.view_update()

    def main_options(self):
        pygame.time.delay(500)
        self.gameOptions.init_draw()
        while 1:
            self.clock.tick(self.FPS)
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.exit()
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    self.main_menu()
                elif event.type == MOUSEBUTTONDOWN:
                    self.gauntlet.clicked()
                    pos = pygame.mouse.get_pos()
                    spriteClicked = self.gameOptions.allButtons.focused_sprite(pos)
                    if spriteClicked:
                        self.gameOptions.view_update()
                        spriteClicked.action()
                elif event.type == MOUSEBUTTONUP:
                    self.gauntlet.unclicked()
            self.gameOptions.view_update()

    @classmethod
    def exit(cls):
        pygame.time.delay(500)
        pygame.quit()
        sys.exit(0)



