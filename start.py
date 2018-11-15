#! /usr/bin/python3

import pygame
import GameView
import GameController
import GameMenu

if __name__ == "__main__":
    pygame.init()
    gameMenu = GameMenu.GameMenu()
    game = GameView.GameView(gameMenu.screen)
    gameController = GameController.GameController(game, gameMenu)
    gameController.main_menu()