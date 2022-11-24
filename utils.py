from enum import IntEnum
from typing import List, Tuple
from math import pi, cos, sin

import numpy as np


class Rotation(IntEnum):
    POS90 = 1
    D180 = 2
    NEG90 = 3

    @property
    def degree(self) -> float:
        if self == Rotation.POS90: return pi/2
        elif self == Rotation.NEG90: return - pi/2
        elif self == Rotation.D180: return pi

TRANSFORM_MATRIX_X = dict()
TRANSFORM_MATRIX_Y = dict()
TRANSFORM_MATRIX_Z = dict()

for alpha in Rotation:
    TRANSFORM_MATRIX_X[alpha.name] = np.array(
        [[1, 0, 0],
         [0, cos(alpha.degree), sin(alpha.degree)],
         [0, - sin(alpha.degree), cos(alpha.degree)]],
        dtype=np.int64)
    TRANSFORM_MATRIX_Y[alpha.name] = np.array(
        [[cos(alpha.degree), 0, - sin(alpha.degree)],
         [0, 1, 0],
         [sin(alpha.degree), 0, cos(alpha.degree)]],
        dtype=np.int64)
    TRANSFORM_MATRIX_Z[alpha.name] = np.array(
        [[cos(alpha.degree), sin(alpha.degree), 0],
         [- sin(alpha.degree), cos(alpha.degree), 0],
         [0, 0, 1]],
        dtype=np.int64)


class Axis(IntEnum):
    X = 0
    Y = 1
    Z = 2


def is_horizontal(coords: List, id1: int, id2: int, id3: int) -> bool:
    cubes = [coords[id1], coords[id2], coords[id3]]

    x_set = set([cube[0] for cube in cubes])
    y_set = set([cube[1] for cube in cubes])
    z_set = set([cube[2] for cube in cubes])

    if len(x_set) == 3 or len(y_set) == 3 or len(z_set) == 3:
        return True
    return False


def joint_axis(coords: List, id1: int, id2: int) -> Axis:
    if coords[id1][0] != coords[id2][0]:
        return Axis.X
    if coords[id1][1] != coords[id2][1]:
        return Axis.Y
    if coords[id1][2] != coords[id2][2]:
        return Axis.Z
    raise "given cubes have the same coordinates."


def stuck_to(sticky_cubes: List, cube_id) -> Tuple[bool, bool]:
    stuck_next, stuck_prev = False, False
    if [cube_id, cube_id + 1] in sticky_cubes:
        stuck_next = True
    if [cube_id - 1, cube_id] in sticky_cubes:
        stuck_prev = True
    return stuck_next, stuck_prev
