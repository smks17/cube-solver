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
    pass
