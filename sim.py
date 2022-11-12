from math import sqrt
from os import stat
from typing import List
from utils import Rotation, Axis


class Simulator:
    def __init__(self, coordinates: List, sticky_cubes: List) -> None:
        self.coords = coordinates
        self.sticky_cubes = sticky_cubes
        self._changed_alpha = False

    def _is_horizontal(self, id1: int, id2: int, id3: int) -> bool:
        cubes = [self.coords[id1], self.coords[id2], self.coords[id3]]

        x_set = set([cube[0] for cube in cubes])
        y_set = set([cube[1] for cube in cubes])
        z_set = set([cube[2] for cube in cubes])

        if len(x_set) == 3 or len(y_set) == 3 or len(z_set) == 3:
            return True
        return False

    def _change_coordinates(self,
                            start_id: int,
                            end_id: int,
                            alpha: Rotation,
                            axis: Axis,
                            center_id: int) -> None:
        x_center, y_center, z_center = self.coords[center_id]
        for i in range(start_id, end_id + 1):
            x, y, z = self.coords[i]
            delta_x, delta_y, delta_z = x - x_center, y - y_center, z - z_center

            if alpha == Rotation.POS90:
                if axis == Axis.X:
                    self.coords[i] = [x_center + delta_x, y_center + delta_z, z_center + delta_y]
                if axis == Axis.Y:
                    self.coords[i] = [x_center + delta_z, y_center + delta_y, z_center + delta_x]
                if axis == Axis.Z:
                    self.coords[i] = [x_center + delta_y, y_center + delta_x, z_center + delta_z]

            if alpha == Rotation.NEG90:
                if axis == Axis.X:
                    self.coords[i] = [x_center + delta_x, y_center + delta_z, z_center - delta_y]
                if axis == Axis.Y:
                    self.coords[i] = [x_center - delta_z, y_center + delta_y, z_center + delta_x]
                if axis == Axis.Z:
                    self.coords[i] = [x_center + delta_y, y_center - delta_x, z_center + delta_z]

            if alpha == Rotation.D180:
                if axis == Axis.X:
                    self.coords[i] = [x_center + delta_x, y_center - delta_y, z_center - delta_z]
                if axis == Axis.Y:
                    self.coords[i] = [x_center - delta_x, y_center + delta_y, z_center - delta_z]
                if axis == Axis.Z:
                    self.coords[i] = [x_center - delta_x, y_center - delta_y, z_center + delta_z]

    def take_action(self, cube_id: int, alpha: Rotation, axis: Axis) -> None:
        start, end = 0, len(self.coords) - 1

        if cube_id == start or cube_id == end:
            return

        stuck_next, stuck_prev = False, False
        if [cube_id, cube_id + 1] in self.sticky_cubes:
            stuck_next = True
        if [cube_id - 1, cube_id] in self.sticky_cubes:
            stuck_prev = True

        if self._is_horizontal(cube_id - 1, cube_id, cube_id + 1):
            if not (stuck_next or stuck_prev):
                return

            if stuck_next and stuck_prev:
                target_cube = cube_id + 1
                while [target_cube, target_cube + 1] in self.sticky_cubes:
                    target_cube += 1

                if self._is_horizontal(target_cube - 1, target_cube, target_cube + 1):
                    return
                else:
                    return self.take_action(target_cube, alpha, axis)

            if stuck_next:
                return self.take_action(cube_id + 1, alpha, axis)

            if stuck_prev:
                if not self._changed_alpha:
                    alpha = alpha * -1
                    self._changed_alpha = True
                return self.take_action(cube_id - 1, alpha, axis)
        else:
            # ?
            if stuck_prev and stuck_next:
                return
            else:
                if end - cube_id < cube_id:
                    return self._change_coordinates(cube_id + 1, end, alpha, axis, cube_id)
                else:
                    if not self._changed_alpha:
                        alpha = alpha * -1
                        self._changed_alpha = True
                    return self._change_coordinates(start, cube_id - 1, alpha, axis, cube_id)


class Interface:
    def __init__(self):
        pass

    def evolve(self,
               state: Simulator,
               cube_id: int,
               alpha: Rotation,
               axis: Axis) -> None:
        self.check_valid_action(state, cube_id, alpha, axis)
        state.take_action(cube_id, alpha, axis)

    def copy_state(self, state: Simulator):
        _copy = Simulator(None,None)
        _copy.coords = state.coords
        _copy.sticky_cubes = state.sticky_cubes
        return _copy

    def update_coords(self, state: Simulator, new_coords: List[List[int]]) -> bool:
        if self.check_valid_state(state):
            stat.coords = new_coords
            return True
        return False

    def goal_test(self, state: Simulator):
        coords = state.coords
        sorted_cords = sorted(coords , key=lambda k: [k[0], k[1], k[2]])
        min_coord = sorted_cords[0]
        index = 0
        for delta_x in range(3):
            for delta_y in range(3):
                for delta_z in range(3):
                    if ((min_coord[0] + delta_x) != sorted_cords[index][0]
                        or (min_coord[1] + delta_y) != sorted_cords[index][1]
                        or (min_coord[2] + delta_z) != sorted_cords[index][2]
                    ):
                        return False
                    index += 1
        return True

    def check_valid_action(self, state, cube_id, alpha, axis):
        # check cube_id
        if 1 > cube_id and cube_id > len(state.coords):
            raise("cube number is not valid")
        # check alpha
        if isinstance(alpha, Rotation): raise("bad type for alpha")
        if alpha not in list(Rotation): raise("alpha is not valid")
        # check axis
        if isinstance(axis, Axis): raise("bad type for axis")
        if axis not in list(Axis): raise("axis is not valid")

    def check_valid_state(self, state: Simulator):
        # check not to be two cube in a same coordinate
        if state.coords != list(set(state.coords)):
            return False
        # check all coords next to each others
        for i in range(len(state.coords) - 1):
            this_coord = stat.coords[i]
            next_coord = stat.coords[i+1]
            distance = sqrt(pow(next_coord[0] - this_coord[0], 2)
                          + pow(next_coord[1] - this_coord[1], 2)
                          + pow(next_coord[2] - this_coord[2], 2))
            if distance != 1:
                return False
            return True