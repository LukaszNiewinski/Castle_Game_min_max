#! /usr/bin/python3

import pygame
import GameView
import GameController
import GameMenu
import GameModel

if __name__ == "__main__":
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.mixer.init()
    pygame.init()
    gameModel = GameModel.GameModel()
    gameMenu = GameMenu.GameMenu()
    gameView = GameView.GameView(gameMenu.screen, gameModel)
    gameController = GameController.GameController(gameView, gameMenu)
    gameController.main_menu()
