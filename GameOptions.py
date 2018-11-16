import pygame
from GameMenu import *


class Indicator(pygame.sprite.Sprite):
    def __init__(self, size, textTrue, textFalse, position):
        super().__init__()
        self.trueImage = FunContainer.font_render(textTrue, size)
        self.falseImage = FunContainer.font_render(textFalse, size)
        self.trueRect = self.trueImage.get_rect()
        self.falseRect = self.falseImage.get_rect()
        self.trueRect.center = position.center
        self.falseRect.center = position.center
        self.image = None
        self.rect = None
        self.state = None

    def set_state(self, state):
        self.state = state
        if self.state:
            self.image = self.trueImage
            self.rect = self.trueRect
        else:
            self.image = self.falseImage
            self.rect = self.falseRect

    def change_state(self):
        if not self.state:
            self.image = self.trueImage
            self.rect = self.trueRect
        else:
            self.image = self.falseImage
            self.rect = self.falseRect
        self.state = not self.state


class GameOptions:
    windowWidth = GameMenu.windowWidth
    windowHeight = GameMenu.windowHeight

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.background = FunContainer.load_image("castle-options.jpg")
        self.background = pygame.transform.scale(self.background, (self.windowWidth, self.windowHeight))
        self.soundButton = Button(55, "Sound", Rect(550, 90, 100, 50))
        self.soundIndicator = Indicator(45, "Off", "On", Rect(550, 160, 100, 50))
        self.changePlayerButton = Button(55, "First move", Rect(550, 230, 100, 50))
        self.changePlayerIndicator = Indicator(45, "Black", "White", Rect(550, 300, 100, 50))
        self.backToMenuButton = Button(55, "Back to menu", Rect(550, 370, 100, 50))
        self.allButtons = ButtonsContainer()
        self.allIndicators = pygame.sprite.RenderPlain()
        self.allButtons.add(self.soundButton, self.changePlayerButton, self.backToMenuButton)
        self.allIndicators.add(self.soundIndicator, self.changePlayerIndicator)
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

        self.allIndicators.update()
        self.allIndicators.clear(self.screen, self.background)
        self.allIndicators.draw(self.screen)

        self.gauntlet.update()
        self.screen.blit(self.gauntlet.image, self.gauntlet.rect)
        pygame.display.update()
