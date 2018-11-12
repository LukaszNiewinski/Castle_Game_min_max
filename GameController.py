from GameModel import *


class GameController:
    def __init__(self, game: GameModel):
        self.game = GameModel()

    def main(self):
        spriteClicked = None
        while 1:
            self.game.clock.tick(10)
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    if not spriteClicked:
                        spriteClicked = self.game.ballsMoving.clicked_sprite(pos)
                        if spriteClicked:
                            spriteClicked.clicked()
                    else:
                        pos = self.game.cartesian2board(pos)
                        if self.game.valid_move(spriteClicked.boardPos, pos):
                            spriteClicked.set_position(Rect(self.game.board[pos]), pos)
                            spriteClicked.unclicked()
                            spriteClicked = None
                            self.game.change_player()
                        else:
                            spriteClicked.unclicked()
                            spriteClicked = None
            self.game.view_update()
