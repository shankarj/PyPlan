from abstract import absagent
import random


class RandomAgentClass(absagent.AbstractAgent):
    myname = "RANDOM"

    def __init__(self, simulator, rollout_policy = None):
        self.agentname = self.myname
        self.simulator = simulator.create_copy()
        self.rollout_policy = rollout_policy

    def create_copy(self):
        return RandomAgentClass(self.simulator.create_copy())

    def get_agent_name(self):
        return self.agentname

    def create_copy(self):
        pass

    def select_action(self, current_state):
        current_turn = current_state.get_current_state()["current_player"]
        self.simulator.change_simulator_state(current_state)
        valid_actions = self.simulator.get_valid_actions()
        actions_count = len(valid_actions)

        if actions_count == 0:
            raise ValueError("Action count cannot be zero.")

        if actions_count == 1:
            choice = 0
        else:
            choice = random.randrange(actions_count)

        return valid_actions[choice]



