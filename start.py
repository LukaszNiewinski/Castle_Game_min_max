#! /usr/bin/python3

import pygame
import GameView
import GameController
import GameMenu
import GameOptions

if __name__ == "__main__":
    pygame.init()
    gameMenu = GameMenu.GameMenu()
    game = GameView.GameView(gameMenu.screen)
    gameOptions = GameOptions.GameOptions(gameMenu.screen)
    gameController = GameController.GameController(game, gameMenu, gameOptions)
    gameController.main_menu()