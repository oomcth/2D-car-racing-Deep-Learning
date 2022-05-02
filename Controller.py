import pygame as pg
from math import cos, sin

dt = 1/60


class Controller:

    def __init__(self, player) -> None:
        self.player = player
        self.angularspeed = 3
        self.acceration = 50

    def Update(self, inputs=None):
        self.player.x += dt * self.player.s * cos(self.player.t)
        self.player.y += dt * self.player.s * sin(self.player.t)

    def R_turn(self):
        self.player.t += dt * self.angularspeed

    def L_turn(self):
        self.player.t -= dt * self.angularspeed

    def accelerate(self):
        self.player.s += dt * self.acceration

    def decelerate(self):
        self.player.s = max(0, self.player.s - dt * 5 * self.acceration)


class Player_Controller(Controller):

    def __init__(self, player) -> None:
        super().__init__(player)

    def Update(self, inputs=None):
        key = pg.key.get_pressed()

        if(key[pg.K_z]):
            super().accelerate()
        if(key[pg.K_s]):
            super().decelerate()
        if(key[pg.K_d]):
            super().R_turn()
        if(key[pg.K_q]):
            super().L_turn()
        super().Update()


class IA_Controller(Controller):

    def __init__(self, player) -> None:
        super().__init__(player)

    def Update(self, inputs=None):
        if(inputs[0] >= 0.8):
            self.accelerate()
        if(inputs[0] <= 0.2):
            pass
        if(inputs[1] >= 0.8):
            self.L_turn()
        if(inputs[1] <= 0.2):
            self.R_turn()
        super().Update()
