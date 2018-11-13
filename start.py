#! /usr/bin/python3

import GameModel
import GameController

if __name__ == "__main__":
    game = GameModel.GameModel()
    gameController = GameController.GameController(game)
    gameController.main()
