from utils import Rotation
from gui import Graphics
from ai import Agent
from sim import Simulator, Interface
from samples import (
    sample1,
    sample2,
    sample3,
    sample4,
    sample5
)


def main():
    game = Simulator(sample5["Coordinates"], sample5["sticky_cubes"])
    interface = Interface()
    agent = Agent()
    gui = Graphics()

    gui.display(game, show_connections=True, show_stickies=True, show_ids=True)
    print(game.coords)
    game.take_action(3, Rotation.POS90, 0)
    print(game.coords)
    gui.display(game, show_connections=True, show_stickies=True, show_ids=True)


if __name__ == "__main__":
    main()
