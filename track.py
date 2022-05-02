import math_extra as me
from geometry_class import Line
import numpy as np


dt = 1/60


class Track:

    def __init__(self) -> None:
        self.line1 = Line([[100., 100.], [150., 300.], [400., 500.],
                          [800., 650.], [1100., 700.], [1000., 450.],
                          [1100., 450.], [1100., 100.]])
        self.line2 = Line([[200., 200.], [300., 300.], [500., 450.],
                          [950., 600.], [900., 350.], [1000., 350.],
                          [1000., 200.]])
        self.segs = np.array(self.line1.segs + self.line2.segs)

    def update(self, player):
        if player.alive:
            a = player.rect.corners()
            player_borders = np.array([[[a[i][0], a[i][1]], [a[(i+1)][0],
                                        a[(i+1)][1]]] for i in range(3)])
            player.i1 = 0.
            player.i2 = 0.
            player.i3 = 0.
            player.i4 = 0.
            player.i5 = 0.
            for seg in self.segs:
                if(me.intersects(player.rect.l1(), seg)):
                    player.i1 = max(player.i1, me.line_intersection(
                        player.rect.l1(), seg))
                if(me.intersects(player.rect.l2(), seg)):
                    player.i2 = max(player.i2, me.line_intersection(
                        player.rect.l2(), seg))
                if(me.intersects(player.rect.l3(), seg)):
                    player.i3 = max(player.i3, me.line_intersection(
                        player.rect.l3(), seg))
                if(me.intersects(player.rect.l4(), seg)):
                    player.i4 = max(player.i4, me.line_intersection(
                        player.rect.l4(), seg))
                if(me.intersects(player.rect.l5(), seg)):
                    player.i5 = max(player.i5, me.line_intersection(
                        player.rect.l5(), seg))

                for s in player_borders:
                    if me.intersects(s, seg):
                        player.die()

    def draw(self, surface):
        self.line1.draw(surface)
        self.line2.draw(surface)
