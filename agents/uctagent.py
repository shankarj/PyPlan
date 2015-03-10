from abstract import absagent
import math
from copy import deepcopy
import sys

class uctnode:
    def __init__(self, node_state, action_list, is_root):
        self.state_value = node_state
        self.state_visit = 0
        self.valid_actions = action_list
        self.children_list = []
        self.reward = []
        self.is_root = is_root
        self.is_terminal = False

class UCTAgentClass(absagent.AbstractAgent):
    myname = "UCT"

    def __init__(self, simulator, rollout_policy, tree_policy, num_simulations, uct_constant=1):
        self.agentname = self.myname
        self.rollout_policy = rollout_policy
        self.simulator = deepcopy(simulator)
        self.tree_policy = tree_policy
        self.uct_constant = uct_constant
        self.simulation_count = num_simulations

    def get_agent_name(self):
        return self.agentname

    def _simulate_game(self, current_pull):
        sim_reward = [0.0] * current_pull.numplayers
        while current_pull.gameover == False:
            action_to_take = self.rollout_policy.select_action(current_pull.current_state)
            current_pull_reward = current_pull.take_action(action_to_take)
            sim_reward = [x + y for x, y in zip(sim_reward, current_pull_reward)]
            current_pull.change_turn()

        return sim_reward

    def select_action(self, current_state):
        current_turn = current_state.get_current_state()["current_player"]
        self.simulator.change_simulator_state(current_state)
        valid_actions = self.simulator.get_valid_actions()
        actions_count = len(valid_actions)

        if actions_count <= 1:
            return valid_actions[0]

        global uctnode
        root_node = uctnode(current_state, valid_actions, True)
        current_node = root_node
        visit_stack = [current_node]
        sim_count = 0

        while sim_count < self.simulation_count:
            if len(current_node.valid_actions) > 0 and len(current_node.children_list) == len(current_node.valid_actions):
                #CHOOSE A NODE USING TREE POLICY
                if self.tree_policy == "UCB":
                    max_val = 0
                    sel_node = 0
                    for node in xrange(len(current_node.children_list)):
                        value = current_node.children_list[node].reward[current_turn - 1]
                        exploration = math.sqrt(math.log(current_node.state_visit) / current_node.children_list[node].state_visit)
                        value += self.uct_constant * exploration

                        if (node == 0):
                            max_val = value
                        else:
                            if value > max_val:
                                max_val = value
                                sel_node = node

                    current_node.state_visit += 1
                    current_node = current_node.children_list[sel_node]
                    visit_stack.append(current_node)
            else:
                #SEE IF THE CURRENT NODE IS A TERMINAL NODE. IF YES, JUST RETURN ITS Q VALUE TO BE BACKTRACKED.
                current_node.state_visit += 1
                self.simulator.change_simulator_state(current_node.state_value)
                sim_count += 1

                if current_node.is_terminal:
                    q_vals = current_node.reward
                else:
                    #PULL A NEW ACTION ARM AND CREATE THE NEW STATE.
                    current_pull = deepcopy(self.simulator)
                    actual_reward = current_pull.take_action(current_node.valid_actions[len(current_node.children_list)])
                    current_pull.change_turn()
                    new_state = current_pull.get_simulator_state()

                    ##SIMULATE TILL END AND GET THE REWARD.
                    sim_reward = self._simulate_game(deepcopy(current_pull))
                    q_vals = [x+y for x,y in zip(actual_reward, sim_reward)]

                    ##CREATE NEW NODE AND APPEND TO CURRENT NODE.
                    global uctnode
                    child_node = uctnode(new_state, current_pull.get_valid_actions(), False)
                    child_node.reward = q_vals
                    child_node.state_visit += 1
                    child_node.is_terminal = current_pull.gameover
                    current_node.children_list.append(deepcopy(child_node))

                    del child_node
                    del current_pull
                    del new_state

                ##BACKTRACK REWARDS UNTIL ROOT NODE
                for node in xrange(len(visit_stack) - 1, -1, -1):
                    if visit_stack[node].is_root == False:
                        visit_stack[node].reward = [x+y for x,y in zip(visit_stack[node].reward, q_vals)]

                ##REVERT BACK TO ROOT
                current_node = root_node
                visit_stack = [current_node]

        best_arm = 0
        best_reward = root_node.children_list[0].reward[current_turn - 1]

        for arm in xrange(len(root_node.children_list)):
            if root_node.children_list[arm].reward[current_turn - 1] > best_reward:
                best_reward = root_node.children_list[arm].reward[current_turn - 1]
                best_arm = arm

        return valid_actions[best_arm]


