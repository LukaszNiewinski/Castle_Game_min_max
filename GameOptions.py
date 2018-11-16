import pygame
from GameMenu import *


class GameOptions:
    windowWidth = GameMenu.windowWidth
    windowHeight = GameMenu.windowHeight

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.background = FunContainer.load_image("castle-options.jpg")
        self.background = pygame.transform.scale(self.background, (self.windowWidth, self.windowHeight))
        # self.playButton = Button(55, "Play", Rect(110, 90, 100, 50))
        # self.optionsButton = Button(55, "Options", Rect(110, 200, 100, 50))
        # self.quitButton = Button(55, "Quit", Rect(110, 310, 100, 50))
        self.allButtons = ButtonsContainer()
        # self.allButtons.add(self.playButton, self.quitButton, self.optionsButton)
        self.gauntlet = None

    def init_draw(self):
        self.screen.blit(self.background, (0, 0))
        self.allButtons.draw(self.screen)
        pygame.display.update()

    def view_update(self):
        self.screen.blit(self.background, self.gauntlet.rect, self.gauntlet.rect)

        self.allButtons.update()
        self.allButtons.clear(self.screen, self.background)
        self.allButtons.draw(self.screen)

        self.gauntlet.update()
        self.screen.blit(self.gauntlet.image, self.gauntlet.rect)
        pygame.display.update()
