from GameModel import *


class GameController:
    def __init__(self, game: GameModel):
        self.game = GameModel()
        self.playerMoving = Player.WHITE
        self.ballsMoving = game.whiteBalls
        self.main()

    def change_player(self):
        if self.playerMoving == Player.WHITE:
            self.playerMoving = Player.BLACK
            self.ballsMoving = self.game.blackBalls
        else:
            self.playerMoving = Player.WHITE
            self.ballsMoving = self.game.whiteBalls

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
                        spriteClicked = self.ballsMoving.clicked_sprite(pos)
                    else:
                        pos = self.game.position2board(pos)
                        spriteClicked.set_position(Rect(self.game.board[pos]))
                        spriteClicked = None
                        self.change_player()
            self.game.view_update()
