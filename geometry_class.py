import numpy
import pygame as pg
from math import cos, sin, pi
import numpy as np

# objet qui gère l'affichage et la position du joueur


class Player_Rect:
    def __init__(self, x, y, w, h, t) -> None:
        # (x, y) renvoient le centre du rectangle
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.t = t
        self.color = pg.Color("red")
        self.sight_reach = 1000.

    # renvoie le centre du rectangle
    def pos(self):
        return numpy.array([self.x, self.y])

    # renvoie les coins du rectangle
    def corners(self):

        v1 = numpy.array([cos(self.t), sin(self.t)])
        v2 = numpy.array([-v1[1], v1[0]])

        v1 *= self.w / 2
        v2 *= self.h / 2

        return [self.pos() + v1 + v2,
                self.pos() - v1 + v2,
                self.pos() - v1 - v2,
                self.pos() + v1 - v2]

    # lignes utilisées pour calculer les inputs de l'IA

    def l1(self):
        return np.array([[self.x, self.y],
                        [self.x + self.sight_reach * cos(self.t),
                        self.y + self.sight_reach * sin(self.t)]])

    def l2(self):
        return np.array([[self.x, self.y],
                        [self.x + self.sight_reach * cos(self.t + pi/4),
                        self.y + self.sight_reach * sin(self.t + pi/4)]])

    def l3(self):
        return np.array([[self.x, self.y],
                        [self.x + self.sight_reach * cos(self.t - pi/4),
                        self.y + self.sight_reach * sin(self.t - pi/4)]])

    def l4(self):
        return np.array([[self.x, self.y],
                        [self.x + self.sight_reach * cos(self.t + pi/2),
                        self.y + self.sight_reach * sin(self.t + pi/2)]])

    def l5(self):
        return np.array([[self.x, self.y],
                        [self.x + self.sight_reach * cos(self.t - pi/2),
                        self.y + self.sight_reach * sin(self.t - pi/2)]])

    def Draw(self, surface):
        pg.draw.polygon(surface, self.color, self.corners())

# objet qui gère la position et l'affichage des bords du circuit


class Line:

    def __init__(self, points) -> None:
        self.points = points
        self.segs = [[points[i], points[(i+1) % len(self.points)]]
                     for i in range(len(self.points))]

    def update(self):
        pass

    def draw(self, surface):
        for seg in self.segs:
            pg.draw.line(surface, pg.Color("white"), seg[0], seg[1])
