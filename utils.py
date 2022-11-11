from dataclasses import dataclass
from enum import IntEnum, auto, Enum
from typing import Tuple


class Rotation(IntEnum):
    POS90 = 90
    NEG90 = -90
    D180 = 180


class ConnectionType(Enum):
    STICKY = auto()
    NORMAL = auto()


@dataclass()
class Piece:
    id: int
    coordinates: Tuple


@dataclass
class Connection:
    prev: int
    to: int
    connection_type: ConnectionType
