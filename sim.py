from typing import List
from utils import Piece, Rotation


class Simulator:
    def __init__(self, coordinates: List, sticky_cubes: List) -> None:
        self.coords = coordinates
        self.sticky_cubes = sticky_cubes

    def take_action(self, piece1: Piece, piece2: Piece, alpha: Rotation) -> None:
        pass


class Interface:
    pass
