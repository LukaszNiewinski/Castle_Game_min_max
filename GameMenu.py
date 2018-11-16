import pygame
from pygame.locals import *
import os


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
    def font_render(cls, text, size):
        fullname = os.path.join(cls.data_dir, "Aller_Lt.ttf")
        font = pygame.font.Font(fullname, size)
        return font.render(text, 1, (0, 0, 0))

    @classmethod
    def center_blit(cls, destination: pygame.Surface, image: pygame.Surface, area: pygame.Rect):
        imageRect = image.get_rect()
        imageRect.center = area.center
        destination.blit(image, imageRect)


class Button(pygame.sprite.Sprite):
    def __init__(self, size, text, position):
        super().__init__()
        self.baseImage = FunContainer.font_render(text, size)
        self.onFocusImage = FunContainer.font_render(text, size + 5)
        self.image = self.baseImage
        self.rect = self.image.get_rect()
        self.rect.center = position.center

    def focus(self):
        self.image = self.onFocusImage

    def unfocus(self):
        self.image = self.baseImage

    def update(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.focus()
        else:
            self.unfocus()

    def action(self):
        pass


class ButtonsContainer(pygame.sprite.RenderPlain):
    def __init__(self):
        super().__init__()

    def focused_sprite(self, position):
        for sprite in self.sprites():
            if sprite.rect.collidepoint(position):
                return sprite
        return None


class GameMenu:
    windowWidth = 800
    windowHeight = 800
    windowName = "Castle game"

    def __init__(self):
        self.screen = pygame.display.set_mode((self.windowWidth, self.windowHeight))
        pygame.display.set_caption(self.windowName)
        self.icon = FunContainer.load_image("castle-icon.jpg")
        self.icon = pygame.transform.scale(self.icon, (32, 32))
        pygame.display.set_icon(self.icon)

        self.background = FunContainer.load_image("castle-menu.jpg")
        self.background = pygame.transform.scale(self.background, (self.windowWidth, self.windowHeight))
        self.playButton = Button(55, "Play", Rect(110, 90, 100, 50))
        self.optionsButton = Button(55, "Options", Rect(110, 200, 100, 50))
        self.quitButton = Button(55, "Quit", Rect(110, 310, 100, 50))
        self.allButtons = ButtonsContainer()
        self.allButtons.add(self.playButton, self.quitButton, self.optionsButton)

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
