from utils import Rotation
from gui import Graphics
from ai import Agent
from sim import Simulator, Interface
from samples import *


def main():
    game = Simulator(sample6["Coordinates"], sample6["sticky_cubes"])
    interface = Interface()
    agent = Agent()
    gui = Graphics()

    # for samples 1 to 5
    # gui.display(game, show_connections=True, show_stickies=True, show_ids=True)
    # game.take_action(3, Rotation.POS90, 0)
    # gui.display(game, show_connections=True, show_stickies=True, show_ids=True)

    # for samples 6 to 8
    gui.display(game, show_connections=True, show_stickies=True, show_ids=True)

    action_count = 0
    while not (interface.goal_test(game)):
        action = agent.act(interface.perceive(game))
        print("attempting", action)

        game._changed_alpha = False
        interface.evolve(game, action[0], action[1], action[2])
        # gui.display(game, show_connections=True, show_stickies=True, show_ids=True)

        action_count += 1

    print(action_count)
    gui.display(game, show_connections=True, show_stickies=True, show_ids=True)


if __name__ == "__main__":
    main()
