import random
from time import time
from gui import Graphics
from sim import Simulator, Interface
import json


debug = False

class Agent:
    def __init__(self):
        self.predicted_actions = []

    def act(self, percept) -> str:
        """
        Takes a perception from the environment in the form of
        json string and returns an action as a string.
        """

        sensor_data = json.loads(percept)
        alg = self.a_star_algorithm

        if not self.predicted_actions:
            t0 = time()
            initial_state = Simulator(sensor_data['coordinates'], sensor_data['stick_together'])
            self.predicted_actions = alg(initial_state)
            if debug:
                print("run time:", time() - t0)

        return self.predicted_actions.pop()

    @staticmethod
    def bfs(root_game: Simulator):
        interface = Interface()
        q = [[root_game, []]]

        buffer_states = {q[0][0]}
        while q:
            node = q.pop(0)

            actions_list = interface.get_possible_actions(node[0])
            random.shuffle(actions_list)

            for action in actions_list:
                child_state = interface.copy_state(node[0])
                interface.evolve(child_state, action[0], action[1], action[2])
                if interface.check_valid_state(child_state) and child_state not in buffer_states:
                    buffer_states.add(child_state)
                    q.append([child_state, [action] + node[1]])

                    if interface.goal_test(child_state):
                        return [action] + node[1]


    def a_star_algorithm(self, root_game: Simulator):
        interface = Interface()
        gui = Graphics()

        interface.h1(root_game)
        open_list = {root_game}
        closed_list = set([])

        g = {root_game: 0}

        parents = {root_game: (root_game, None)}

        counter = 0
        while len(open_list) > 0:
            n = None

            for v in open_list:
                if n is None or (g[v] + v.h < g[n] + n.h and g[v] < 30):
                    n = v

            counter += 1
            if debug:
                print(f"counter: {counter}, g: {g[n]}, h: {n.h}")
            if counter % 100 == 0:
                if debug:
                    gui.display(n, True, True, True)

            if n is None:
                if debug:
                    print('Path does not exist!')
                return None

            if n.h == 0:
                reconst_actions = []
                if debug:
                    gui.display(n, True, True, True)

                while parents[n][0] != n:
                    n, action = parents[n]
                    reconst_actions.append(action)

                if debug:
                    print('Path found: {}'.format(reconst_actions))
                return reconst_actions

            actions_list = interface.get_possible_actions(n)
            random.shuffle(actions_list)

            for action in actions_list:
                child_state = interface.copy_state(n)
                interface.evolve(child_state, action[0], action[1], action[2])

                if interface.check_valid_state(child_state):
                    if child_state not in open_list and child_state not in closed_list:
                        open_list.add(child_state)
                        interface.h1(child_state)
                        parents[child_state] = (n, action)
                        g[child_state] = g[n] + 1
                    else:
                        if g[child_state] > g[n] + 1:
                            g[child_state] = g[n] + 1
                            parents[child_state] = (n, action)

                            if child_state in closed_list:
                                closed_list.remove(child_state)
                                open_list.add(child_state)
                                interface.h1(child_state)

            open_list.remove(n)
            closed_list.add(n)
            interface.h1(n)

        if debug:
            print('Path does not exist!')
        return None
