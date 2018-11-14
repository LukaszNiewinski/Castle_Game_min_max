from GameView import *


class GameController:
    def __init__(self, game: GameView):
        self.game = GameView()

    def main(self):
        spriteClicked = None
        while 1:
            self.game.clock.tick(30)
            for event in pygame.event.get():
                if event.type == QUIT:
                    return
                elif event.type == KEYDOWN and event.key == K_ESCAPE:
                    return
                elif event.type == MOUSEBUTTONDOWN:
                    self.game.gauntlet.clicked()
                    pos = pygame.mouse.get_pos()
                    if not spriteClicked:
                        spriteClicked = self.game.activePlayer.balls.clicked_sprite(pos)
                        if spriteClicked:
                            spriteClicked.clicked()
                    else:
                        pos = self.game.cartesian2board(pos)
                        if self.game.move_ball(spriteClicked, pos):
                            self.game.change_player()
                        spriteClicked.unclicked()
                        spriteClicked = None
                elif event.type == MOUSEBUTTONUP:
                    self.game.gauntlet.unclicked()
            self.game.view_update()
