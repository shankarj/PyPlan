from abstract import absagent
import math
import sys
import timeit

class uctnode:
    def __init__(self, node_state, action_list, is_root):
        self.state_value = node_state
        self.valid_actions = action_list
        self.is_root = is_root
        self.state_visit = 0
        self.children_list = []
        self.reward = []
        self.is_terminal = False

class UCTAgentClass(absagent.AbstractAgent):
    myname = "UCT"

    def __init__(self, simulator, rollout_policy, tree_policy, num_simulations, uct_constant=1, horizon=10):
        self.agentname = self.myname
        self.rollout_policy = rollout_policy
        self.simulator = simulator.create_copy()
        self.tree_policy = tree_policy
        self.uct_constant = uct_constant
        self.simulation_count = num_simulations
        self.horizon = horizon

    def create_copy(self):
        return UCTAgentClass(self.simulator.create_copy(), self.rollout_policy.create_copy(), self.tree_policy, self.simulation_count, self.uct_constant, self.horizon)

    def get_agent_name(self):
        return self.agentname

    def _simulate_game(self, current_pull):
        sim_reward = [0.0] * current_pull.numplayers
        h = 0
        while current_pull.gameover == False and h <= self.horizon:
            action_to_take = self.rollout_policy.select_action(current_pull.current_state)
            current_pull_reward = current_pull.take_action(action_to_take)
            sim_reward = [x + y for x, y in zip(sim_reward, current_pull_reward)]
            current_pull.change_turn()
            h += 1

        del current_pull
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
        num_nodes = 0
        start_time = timeit.default_timer()
        end_time = timeit.default_timer()

        #while end_time - start_time < 1.0:
        while sim_count < self.simulation_count:
            # CHOOSE A NODE USING TREE POLICY. NODE SELECTION.
            while len(current_node.valid_actions) > 0 and len(current_node.children_list) == len(current_node.valid_actions):
                if self.tree_policy == "UCB":
                    max_val = 0
                    sel_node = 0
                    for node in xrange(len(current_node.children_list)):
                        node_turn = current_node.state_value.get_current_state()["current_player"]
                        value = current_node.children_list[node].reward[node_turn - 1]
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

            # SEE IF THE CURRENT NODE IS A TERMINAL NODE. IF YES, JUST RETURN ITS Q VALUE TO BE BACKTRACKED.
            current_node.state_visit += 1
            sim_count += 1

            if current_node.is_terminal:
                q_vals = current_node.reward
            else:
                #PULL A NEW ACTION ARM AND CREATE THE NEW STATE.
                self.simulator.change_simulator_state(current_node.state_value)
                current_pull = self.simulator.create_copy()
                actual_reward = current_pull.take_action(current_node.valid_actions[len(current_node.children_list)])
                current_pull.change_turn()

                # SIMULATE TILL END AND GET THE REWARD.
                # NODE SIMULATION AND EXPANSION.
                sim_reward = self._simulate_game(current_pull.create_copy())
                q_vals = [x+y for x,y in zip(actual_reward, sim_reward)]

                ##CREATE NEW NODE AND APPEND TO CURRENT NODE.
                num_nodes += 1
                global uctnode
                child_node = uctnode(current_pull.get_simulator_state(), current_pull.get_valid_actions(), False)
                child_node.reward = q_vals
                child_node.state_visit += 1
                child_node.is_terminal = current_pull.gameover
                current_node.children_list.append(child_node)

                del current_pull

            # BACKTRACK REWARDS UNTIL ROOT NODE
            for node in xrange(len(visit_stack) - 1, -1, -1):
                if visit_stack[node].is_root == False:
                    temp_diff =  [x - y for x, y in zip(q_vals, visit_stack[node].reward)]
                    temp_qterm =  [float(x) / float(visit_stack[node].state_visit) for x in temp_diff]
                    visit_stack[node].reward = [x + y for x, y in zip(visit_stack[node].reward, temp_qterm)]

            ##REVERT BACK TO ROOT
            current_node = root_node
            visit_stack = [current_node]

        #end_time = timeit.default_timer()

        # print "NUM NODES : ", str(num_nodes)
        # print "NUM SIMS : ", str(sim_count)
        # exit()

        best_arm = 0
        best_reward = root_node.children_list[0].reward[current_turn - 1]

        for arm in xrange(len(root_node.children_list)):
            # print root_node.children_list[arm].reward
            if root_node.children_list[arm].reward[current_turn - 1] > best_reward:
                best_reward = root_node.children_list[arm].reward[current_turn - 1]
                best_arm = arm

        return valid_actions[best_arm]


