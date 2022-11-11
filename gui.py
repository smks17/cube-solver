from typing import List
from sim import Simulator
import numpy as np
import matplotlib.pyplot as plt


class Graphics:
    def __int__(self) -> None:
        pass

    @staticmethod
    def _shift_coords(coords: List,
                      shifter: int,
                      min_x: int,
                      min_y: int,
                      min_z: int):
        if min_x < 0:
            for coord in coords:
                coord[0] += (min_x * -1)

        if min_y < 0:
            for coord in coords:
                coord[1] += (min_y * -1)

        if min_z < 0:
            for coord in coords:
                coord[2] += (min_z * -1)

        for coord in coords:
            coord[0] += shifter
            coord[1] += shifter
            coord[2] += shifter

    @staticmethod
    def _draw_lines(ax: plt.axes, coord1: List, coord2: List, color: str) -> None:
        x_start, x_end = coord1[0] + 0.5, coord2[0] + 0.5
        y_start, y_end = coord1[1] + 0.5, coord2[1] + 0.5
        z_start, z_end = coord1[2] + 0.5, coord2[2] + 0.5

        ax.plot([x_start, x_end],
                [y_start, y_end],
                [z_start, z_end],
                color=color)

    def display(self,
                env: Simulator,
                show_connections: bool = False,
                show_stickies: bool = False,
                show_ids: bool = False) -> None:
        coords = np.array([[x, y, z] for x, y, z in env.coords])
        stickies = np.array([[p1, p2] for p1, p2 in env.sticky_cubes])
        shifter = 1
        alpha = 0.1

        min_cord, max_cord = coords.min(0), coords.max(0)
        min_x, min_y, min_z = min_cord
        max_x, max_y, max_z = max_cord

        len_x, len_y, len_z = (max_x - min_x) + (2 * shifter) + 1, \
                              (max_y - min_y) + (2 * shifter) + 1, \
                              (max_z - min_z) + (2 * shifter) + 1
        axes = [len_x, len_y, len_z]

        self._shift_coords(coords, shifter, min_x, min_y, min_z)

        data = np.zeros(axes, dtype=np.bool)
        for x, y, z in coords:
            data[x, y, z] = 1

        colors = np.empty(axes + [4], dtype=np.float32)
        colors[:] = [0, 0, 1, alpha]

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')

        ax.voxels(data, facecolors=colors)

        if show_connections:
            for i in range(len(coords) - 1):
                self._draw_lines(ax, coords[i], coords[i + 1], color="black")

        if show_stickies:
            for p1, p2 in stickies:
                coord1, coord2 = coords[p1], coords[p2]
                self._draw_lines(ax, coord1, coord2, color="red")

        if show_ids:
            for index, coord in enumerate(coords):
                ax.text(coord[0] + 0.5,
                        coord[1] + 0.5,
                        coord[2] + 0.5,
                        str(index + 1),
                        color="green")

        plt.show()
