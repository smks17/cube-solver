import json
from copy import deepcopy
from typing import List
from utils import Rotation, Axis, is_horizontal, joint_axis, stuck_to


class Simulator:
    def __init__(self, coordinates: List, sticky_cubes: List) -> None:
        self.coords = coordinates
        self.sticky_cubes = sticky_cubes
        self._changed_alpha = False

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

        stuck_next, stuck_prev = stuck_to(self.sticky_cubes, cube_id)

        if is_horizontal(self.coords, cube_id - 1, cube_id, cube_id + 1):
            if not (stuck_next or stuck_prev):
                return

            if stuck_next and stuck_prev:
                target_cube = cube_id + 1
                while [target_cube, target_cube + 1] in self.sticky_cubes:
                    target_cube += 1

                if is_horizontal(self.coords, target_cube - 1, target_cube, target_cube + 1):
                    return
                else:
                    return self.take_action(target_cube, alpha, axis)

            if stuck_next:
                target_cube = cube_id + 1
                if (
                    is_horizontal(self.coords, target_cube - 1, target_cube, target_cube + 1) and
                    ([target_cube, target_cube + 1] not in self.sticky_cubes)
                ):
                    return
                return self.take_action(cube_id + 1, alpha, axis)

            # if stuck_prev:
            #     target_cube = cube_id + 1
            #     if (
            #             is_horizontal(self.coords, target_cube - 1, target_cube, target_cube + 1) and
            #             ([target_cube, target_cube + 1] not in self.sticky_cubes)
            #     ):
            #     if alpha == Rotation.POS90 or alpha == Rotation.NEG90:
            #         if not self._changed_alpha:
            #             alpha = alpha * -1
            #             self._changed_alpha = True
            #     return self.take_action(cube_id - 1, alpha, axis)
        else:
            if stuck_prev and stuck_next:
                return
            else:
                if end - cube_id < cube_id:
                    return self._change_coordinates(cube_id + 1, end, alpha, axis, cube_id)
                else:
                    if alpha == Rotation.POS90 or alpha == Rotation.NEG90:
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
            "Coordinates": state.coords,
            "sticky_cubes": state.sticky_cubes
        })

    @staticmethod
    def goal_test(state: Simulator) -> bool:
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
        set_coords = set(tuple(x) for x in state.coords)
        if len(set_coords) != len(state.coords):
            return False
        return True

    @staticmethod
    def get_possible_actions(state: Simulator) -> List:
        action_list = []
        for cube_id in range(1, len(state.coords) - 2):
            for rotation in list(Rotation):
                if is_horizontal(state.coords, cube_id - 1, cube_id, cube_id + 1):
                    stuck_next, stuck_prev = stuck_to(state.sticky_cubes, cube_id)
                    if (stuck_prev or stuck_next) and not (stuck_next and stuck_prev):
                        axis = joint_axis(state.coords, cube_id - 1, cube_id)
                        res = [cube_id, rotation, axis]
                        if res not in action_list:
                            action_list.append(res)
                    continue
                else:
                    prev_axis = joint_axis(state.coords, cube_id - 1, cube_id)
                    next_axis = joint_axis(state.coords, cube_id, cube_id + 1)
                    for axis in list({prev_axis, next_axis}):
                        res = [cube_id, rotation, axis]
                        if res not in action_list:
                            action_list.append(res)
        return action_list
