#! /usr/bin/python3

import pygame
import GameView
import GameController
import GameMenu
import GameModel
import GameOptions

if __name__ == "__main__":
    deep1 = input("Player1's deep: ")
    deep2 = input("Player2's deep: ")
    deep1 = int(deep1)
    deep2 = int(deep2)
    deep = (deep1, deep2)
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    pygame.mixer.init()
    pygame.init()
    gameModel = GameModel.GameModel()
    gameMenu = GameMenu.GameMenu()
    gameView = GameView.GameView(gameMenu.screen, gameModel)
    gameOptions = GameOptions.GameOptions(gameMenu.screen)
    gameController = GameController.GameController(gameView, gameMenu, gameOptions, deep)
    gameController.main_menu()
