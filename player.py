from geometry_class import Player_Rect


class Player:

    def __init__(self, x, y, w, h, t, s=10) -> None:
        self.rect = Player_Rect(x, y, w, h, t)
        self.controllers = []
        self.speed = s
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.t = t
        self.s = s
        self.i1 = 0.
        self.i2 = 0.
        self.i3 = 0.
        self.i4 = 0.
        self.i5 = 0.
        self.alive = True
        self.reward_zone = 1
        self.moved_count = 0
        self.max = 10000

    def add(self, controller):
        self.controllers.append(controller)

    def Update(self, out=None):
        self.moved_count += 1
        if(self.moved_count >= self.max and self.max != -1):
            self.die()
        if(self.s <= 80 and self.max >= 0):
            self.die()
        if(self.alive):
            for controller in self.controllers:
                controller.Update(out)
            self.rect = Player_Rect(self.x, self.y, self.w, self.h, self.t)

    def die(self):
        self.x = 170.
        self.y = 200.
        self.t = 1.
        self.s = 0.
        self.alive = False

    def Draw(self, surface):
        self.rect.Draw(surface)

    def get_reward(self):
        return 2. + self.s / 50

    def inputs(self):
        return [self.i1, self.i2, self.i3, self.i4, self.i5, self.s]
