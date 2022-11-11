from gui import Graphics
from ai import Agent
from sim import Simulator, Interface


sample_input_json = {
    "Coordinates": [
        [0, 0, 0],
        [1, 1, 1],
        [-1, -1, -1]
    ],
    "sticky_cubes": [
        [0, 1]
    ]
}


def main():
    game = Simulator(sample_input_json["Coordinates"], sample_input_json["sticky_cubes"])
    interface = Interface()
    agent = Agent()
    gui = Graphics()

    gui.display(game, show_connections=True, show_stickies=True, show_ids=True)


if __name__ == "__main__":
    main()
