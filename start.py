#! /usr/bin/python3

import pygame
import GameView
import GameController

if __name__ == "__main__":
    game = GameView.GameView()
    gameController = GameController.GameController(game)
    gameController.main()
    pygame.quit()
