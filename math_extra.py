import math
from numba import njit
import numpy as np


@njit('boolean(float64[:],float64[:],float64[:])')
def on_segment(p, q, r):
    if(r[0] <= max(p[0], q[0]) and r[0] >= min(p[0], q[0]) and
            r[1] <= max(p[1], q[1]) and r[1] >= min(p[1], q[1])):
        return True
    return False


@njit('int32(float64[:],float64[:],float64[:])')
def orientation(p, q, r):

    val = ((q[1] - p[1]) * (r[0] - q[0])) - ((q[0] - p[0]) * (r[1] - q[1]))
    if val == 0:
        return 0
    return 1 if val > 0 else -1


@njit('boolean(float64[:,:],float64[:,:])')
def intersects(seg1, seg2):

    p1, q1 = seg1
    p2, q2 = seg2

    o1 = orientation(p1, q1, p2)

    o2 = orientation(p1, q1, q2)
    o3 = orientation(p2, q2, p1)
    o4 = orientation(p2, q2, q1)

    if o1 != o2 and o3 != o4:

        return True

    if o1 == 0 and on_segment(p1, q1, p2):
        return True

    if o2 == 0 and on_segment(p1, q1, q2):
        return True
    if o3 == 0 and on_segment(p2, q2, p1):
        return True
    if o4 == 0 and on_segment(p2, q2, q1):
        return True
    return False


@njit('float64(float64, float64)')
def norm(x, y):
    return math.sqrt(x**2 + y**2)


@njit('float64(float64[:], float64[:])')
def det(a, b):
    return a[0] * b[1] - a[1] * b[0]


def line_intersection(line1, line2):
    xdiff = np.array([line1[0][0] - line1[1][0], line2[0][0] - line2[1][0]])
    ydiff = np.array([line1[0][1] - line1[1][1], line2[0][1] - line2[1][1]])

    div = det(xdiff, ydiff)
    if div == 0:
        return 500
    d = np.array([det(np.array(line1[0]), np.array(line1[1])),
                 det(np.array(line2[0]), np.array(line2[1]))])
    x = det(d, xdiff) / div
    y = det(d, ydiff) / div
    return (1 - norm(x - line1[0][0], y - line1[0][1]) /
            norm(line1[1][0] - line1[0][0], line1[1][1] - line1[0][1])) * 500
