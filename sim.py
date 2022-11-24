import json
from copy import deepcopy
from math import sqrt
from typing import List

import numpy as np
from sklearn.decomposition import PCA

from utils import (
    Rotation,
    Axis,
    is_horizontal,
    joint_axis,
    stuck_to,
    TRANSFORM_MATRIX_X,
    TRANSFORM_MATRIX_Y,
    TRANSFORM_MATRIX_Z,
)


class Simulator:
    def __init__(self, coordinates: List, sticky_cubes: List) -> None:
        self.coords = np.array(coordinates)
        if sticky_cubes is None:
            sticky_cubes = None
        else:
            self.sticky_cubes = [[i[0]-1,i[1]-1] for i in sticky_cubes]
        self._changed_alpha = False
        self.h = None

    def _change_coordinates(self,
                            start_id: int,
                            end_id: int,
                            alpha: Rotation,
                            axis: Axis,
                            center_id: int) -> None:
        delta_coords = self.coords[start_id: end_id + 1, ] - self.coords[center_id]
        if axis == Axis.X:
            transform_matrix = TRANSFORM_MATRIX_X[alpha.name]
        elif axis == Axis.Y:
            transform_matrix = TRANSFORM_MATRIX_Y[alpha.name]
        elif axis == Axis.Z:
            transform_matrix = TRANSFORM_MATRIX_Z[alpha.name]
        self.coords[start_id: end_id + 1, ] = \
            self.coords[center_id] + (transform_matrix @ delta_coords.T).T


    def take_action(self, cube_id: int, axis: Axis, alpha: Rotation) -> None:
        start, end = 0, len(self.coords) - 1

        if cube_id == start or cube_id == end:
            return

        stuck_next, stuck_prev = stuck_to(self.sticky_cubes, cube_id)

        if is_horizontal(self.coords, cube_id - 1, cube_id, cube_id + 1):
            if not (stuck_next or stuck_prev):
                return

            if stuck_next and stuck_prev:
                if not self._changed_alpha:
                    target_cube = cube_id + 1
                    while [target_cube, target_cube + 1] in self.sticky_cubes:
                        target_cube += 1
                else:
                    target_cube = cube_id - 1
                    while [target_cube - 1, target_cube] in self.sticky_cubes:
                        target_cube -= 1

                if is_horizontal(self.coords, target_cube - 1, target_cube, target_cube + 1):
                    return
                else:
                    return self.take_action(target_cube, axis, alpha)

            if stuck_next:
                target_cube = cube_id + 1
                if (
                        is_horizontal(self.coords, target_cube - 1, target_cube, target_cube + 1) and
                        ([target_cube, target_cube + 1] not in self.sticky_cubes)
                ):
                    return
                return self.take_action(target_cube, axis, alpha)

            if stuck_prev:
                target_cube = cube_id - 1
                if (
                        is_horizontal(self.coords, target_cube - 1, target_cube, target_cube + 1) and
                        ([target_cube - 1, target_cube] not in self.sticky_cubes)
                ):
                    return
                if not self._changed_alpha:
                    self._changed_alpha = True
                return self.take_action(target_cube, axis, alpha)
        else:
            if stuck_prev and stuck_next:
                return
            else:
                if self.coords[cube_id][axis] != self.coords[cube_id + 1][axis]:
                    return self._change_coordinates(start, cube_id - 1, alpha, axis, cube_id)
                if self.coords[cube_id - 1][axis] != self.coords[cube_id][axis]:
                    return self._change_coordinates(cube_id + 1, end, alpha, axis, cube_id)
                raise "given axis is not compatible with given rotation"

    def __eq__(self, __o: object) -> bool:
        mat1 = self.coords - self.coords[0]
        mat2 = __o.coords - __o.coords[0]
        return (PCA().fit_transform(mat1) == PCA().fit_transform(mat2)).all()

    def __hash__(self) -> int:
        return hash(self.coords.tobytes())


class Interface:
    def __init__(self):
        pass

    def evolve(self,
               state: Simulator,
               cube_id: int,
               axis: Axis,
               alpha: Rotation) -> None:
        self.check_valid_action(state, cube_id, alpha, axis)
        state.take_action(cube_id, axis, alpha)

    @staticmethod
    def copy_state(state: Simulator) -> Simulator:
        _copy = Simulator(None, None)
        _copy.coords = deepcopy(state.coords)
        _copy.sticky_cubes = state.sticky_cubes
        return _copy

    @staticmethod
    def perceive(state: Simulator):
        """Returns what agent will see in a given state as a json."""

        return json.dumps({
            "coordinates": state.coords.tolist(),
            "stick_together": state.sticky_cubes
        })

    def h1(self, state: Simulator):
        sorted_coords = sorted(state.coords, key=lambda k: [k[0], k[1], k[2]])
        min_coord = sorted_coords[0]
        index = 0
        res = 0
        for delta_x in range(3):
            for delta_y in range(3):
                for delta_z in range(3):
                    x1, y1, z1 = (
                        min_coord[0] + delta_x,
                        min_coord[1] + delta_y,
                        min_coord[2] + delta_z
                    )
                    x2, y2, z2 = sorted_coords[index]
                    res += sqrt(pow(x2 - x1, 2) +
                                pow(y2 - y1, 2) +
                                pow(z2 - z1, 2) * 1.0)
                    index += 1
        state.h = res
        # return res

    def h2(self, state: Simulator):
        #! This method is not used
        x_set = len(set([cube[0] for cube in state.coords]))
        y_set = len(set([cube[1] for cube in state.coords]))
        z_set = len(set([cube[2] for cube in state.coords]))

        res = abs(x_set + y_set + z_set - 9)
        state.h = res * 100 * self.h1(state)

    @staticmethod
    def goal_test(state: Simulator) -> bool:
        #! This method is not used
        sorted_coords = sorted(state.coords, key=lambda k: [k[0], k[1], k[2]])
        min_coord = sorted_coords[0]
        index = 0
        for delta_x in range(3):
            for delta_y in range(3):
                for delta_z in range(3):
                    if (
                            (min_coord[0] + delta_x) != sorted_coords[index][0] or
                            (min_coord[1] + delta_y) != sorted_coords[index][1] or
                            (min_coord[2] + delta_z) != sorted_coords[index][2]
                    ):
                        return False
                    index += 1
        return True

    @staticmethod
    def check_valid_action(state, cube_id, alpha, axis):
        # check cube_id
        if cube_id < 0 or cube_id > len(state.coords) - 1:
            raise "cube number is not valid"

        # check alpha
        if not isinstance(alpha, Rotation):
            raise "incorrect type for alpha"
        if alpha not in list(Rotation):
            raise "alpha is not valid"

        # check axis
        if not isinstance(axis, Axis):
            raise "incorrect type for axis"
        if axis not in list(Axis):
            raise "axis is not valid"

    @staticmethod
    def check_valid_state(state: Simulator) -> bool:
        # check not to be two cube in a same coordinate
        axs = state.coords
        return len(np.unique(axs, axis=0)) == len(axs)

    @staticmethod
    def get_possible_actions(state: Simulator) -> List:
        action_list = []
        for cube_id in range(1, len(state.coords) - 2):
            for rotation in list(Rotation):
                if is_horizontal(state.coords, cube_id - 1, cube_id, cube_id + 1):
                    # stuck_next, stuck_prev = stuck_to(state.sticky_cubes, cube_id)
                    # if (stuck_prev or stuck_next) and not (stuck_next and stuck_prev):
                    #     axis = joint_axis(state.coords, cube_id - 1, cube_id)
                    #     res = [cube_id, rotation, axis]
                    #     if res not in action_list:
                    #         action_list.append(res)
                    continue
                else:
                    stuck_next, stuck_prev = stuck_to(state.sticky_cubes, cube_id)
                    if stuck_prev and stuck_next:
                        continue

                    prev_axis = joint_axis(state.coords, cube_id - 1, cube_id)
                    next_axis = joint_axis(state.coords, cube_id, cube_id + 1)

                    if stuck_next:
                        res = [cube_id, next_axis, rotation]
                        if res not in action_list:
                            action_list.append(res)
                    elif stuck_prev:
                        res = [cube_id, prev_axis, rotation]
                        if res not in action_list:
                            action_list.append(res)
                    else:
                        for axis in list({prev_axis, next_axis}):
                            res = [cube_id, axis, rotation]
                            if res not in action_list:
                                action_list.append(res)
        return action_list
