from abstract import absagent
from copy import deepcopy

'''
At n, pull arm n mod k. k - Total actions available.

Method:
------

1. From the set of valid actions in the given simulator's state, one action is chosen.
   1. a. Action is chosed based on n mod k. k - Total actions available.. n - current pull.
2. The chosen action is taken on the simulator and the state is updated.
3. This copy of the simulator is given to simulation using rollout policy until the game comes to an end.
4. The rollout reward vectors are added to the current_arms rewards in arm_rewards
    4. a. The pull count for the chosen arm is incremented in arm_pull_count[chosen_arm]
5. Step 3 is repeated for the specified number of pulls
6. Step 1 is repeated for the next available action until all the pulls are exhausted.
7. The final value in arm_rewards will give the value of specified arm for the number of pulls.
8. Return the arm with the maximum average reward.

'''

class IncUniformRolloutAgentClass(absagent.AbstractAgent):
    myname = "INCREMENTAL UNIFORM"

    def __init__(self, simulator, rollout_policy, pull_count=5, horizon=5, heuristic=0):
        self.agentname = self.myname
        self.rollout_policy = rollout_policy
        self.heuristicvalue = heuristic
        self.pull_count = pull_count
        self.simulator = deepcopy(simulator)
        self.horizon = horizon

    def get_agent_name(self):
		return self.agentname

    def set_num_pulls(self, pull_count=3):
        self.pull_count = pull_count

    def select_action(self, current_state):
        current_turn = current_state.get_current_state()["current_player"]
        self.simulator.change_simulator_state(current_state)
        valid_actions = self.simulator.get_valid_actions()
        actions_count = len(valid_actions)

        if actions_count <= 1:
            return valid_actions[0]

        arm_rewards = [[0.0] * self.simulator.numplayers] * actions_count  # REWARD VECTOR(EACH PLAYER) PER ACTION
        arm_pull_count = [0] * actions_count

        for current_pull in xrange(self.pull_count):
            chosen_arm = current_pull % actions_count

            # TAKE THE ACTION i.e., CREATE THE CHOSEN ARM TO DO ROLL OUT
            current_pull = deepcopy(self.simulator)
            actual_reward = current_pull.take_action(valid_actions[chosen_arm])
            current_pull.change_turn()

            # PLAY TILL GAME END
            playout_rewards = []
            h = 0
            while current_pull.gameover == False and h <= self.horizon:
                action_to_take = self.rollout_policy.select_action(current_pull.current_state)
                reward = current_pull.take_action(action_to_take)
                playout_rewards.append(reward)
                current_pull.change_turn()
                h += 1

            # ADD ACTUAL REWARD + BACKTRACK REWARDS TO THE CURRENT PULL'S REWARD AND ADD TO CURRENT ARM'S REWARD VECTOR
            # INCREMENT THE CHOSEN ARM'S PULL COUNT
            current_pull_reward = [0] * self.simulator.numplayers
            current_pull_reward = [x + y for x, y in zip(actual_reward, current_pull_reward)]
            for value in xrange(len(playout_rewards)):
                current_pull_reward = [x + y for x, y in zip(playout_rewards[value], current_pull_reward)]

            arm_pull_count[chosen_arm] += 1
            arm_rewards[chosen_arm] = [x + y for x, y in zip(arm_rewards[chosen_arm], current_pull_reward)]
            del current_pull

        # CALCULATE ARM WITH BEST AVERAGE AND RETURN IT
        best_arm = 0
        best_avg = arm_rewards[0][current_turn - 1] / arm_pull_count[0]
        for arm in xrange(len(arm_rewards)):
            if arm_pull_count[arm] == 0:
                curr_avg = 0
            else:
                curr_avg = arm_rewards[arm][current_turn - 1] / arm_pull_count[arm]

            if curr_avg > best_avg:
                best_arm = arm
                best_avg = curr_avg

        return valid_actions[best_arm]


