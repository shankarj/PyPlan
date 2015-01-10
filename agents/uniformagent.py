from abstract import absagent
from copy import deepcopy

'''
Uniformly pull each arm w number of times

Method:
------

1. From the set of valid actions in the given simulator's state, one action is chosen.
2. The chosen action is taken on the simulator and the state is updated.
3. This copy of the simulator is given to simulation using rollout policy until the game comes to an end.
4. The end reward is noted and added to the current arm in arm_rewards[arm]
5. Step 3 is repeated for the specified number of pulls
6. Step 1 is repeated for the next available action until all the available actions are chosen.
7. The final value in arm_rewards will give the value of specified number of pulls for each of the arm i.e., action
8. Return the arm with the maximum reward.

'''

class UniformRolloutAgentClass(absagent.AbstractAgent):
    myname = "UNIFORM"

    def __init__(self, simulator, rollout_policy, pull_count, heuristic=0):
        self.agentname = self.myname
        self.rollout_policy = rollout_policy
        self.heuristicvalue = heuristic
        self.pull_count = 3
        self.simulator = deepcopy(simulator)

    def get_agent_name(self):
		return self.agentname

    def set_num_pulls(self, pull_count=3):
        self.pull_count = pull_count

    def select_action(self, current_state, current_turn):
        self.simulator.change_simulator_values(current_state, current_turn)
        valid_actions = self.simulator.get_valid_actions()
        actions_count = len(valid_actions)

        arm_rewards = [0] * actions_count

        for arm in xrange(actions_count):
            for pull in xrange(self.pull_count):
                player_number = self.simulator.playerturn

                # TAKE THE ACTION i.e., CREATE THE ARM
                current_arm = deepcopy(self.simulator)
                current_arm.take_action(valid_actions[arm])
                current_arm.change_turn()

                # PLAY TILL GAME END
                while current_arm.is_terminal() == False:
                    actual_agent_id = current_arm.playerturn - 1
                    action_to_take = self.rollout_policy.select_action(current_arm.current_state, current_arm.playerturn)
                    current_arm.take_action(action_to_take)
                    current_arm.change_turn()

                winner = current_arm.winningplayer

                if winner == player_number:
                    arm_rewards[arm] += 1
                elif winner == None:
                    pass
                else:
                    arm_rewards[arm] -= 1

                del current_arm

        best_arm = 0
        best_reward = arm_rewards[0]

        for arm in xrange(len(arm_rewards)):
            if arm_rewards[arm] > best_reward:
                best_reward = arm_rewards[arm]
                best_arm = arm

        return valid_actions[best_arm]


