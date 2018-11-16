import pygame
from GameMenu import *


class

class GameOptions:
    windowWidth = GameMenu.windowWidth
    windowHeight = GameMenu.windowHeight

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.background = FunContainer.load_image("castle-options.jpg")
        self.background = pygame.transform.scale(self.background, (self.windowWidth, self.windowHeight))
        self.soundButton = Button(55, "Sound", Rect(550, 90, 100, 50))
        self.changePlayerButton = Button(55, "Player start", Rect(550, 230, 100, 50))
        self.backToMenuButton = Button(55, "Back to menu", Rect(550, 370, 100, 50))
        self.allButtons = ButtonsContainer()
        self.allButtons.add(self.soundButton, self.changePlayerButton, self.backToMenuButton)
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
