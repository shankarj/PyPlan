from abstract import absagent
import math
import sys
import multiprocessing
from multiprocessing import Process, Queue
import timeit
import threading

total_count = 0
start_time = None

class uctnode:
    def __init__(self, node_state, action_list, is_root):
        self.state_value = node_state
        self.valid_actions = action_list
        self.is_root = is_root
        self.state_visit = 0
        self.children_list = []
        self.reward = []
        self.is_terminal = False
        self.verbose = False

def _simulate_game(rollout_policy, current_pull, horizon, s_q):
    sim_reward = [0.0] * current_pull.numplayers
    h = 0
    while current_pull.gameover == False and h <= horizon:
        action_to_take = rollout_policy.select_action(current_pull.current_state)
        current_pull_reward = current_pull.take_action(action_to_take)
        sim_reward = [x + y for x, y in zip(sim_reward, current_pull_reward)]
        current_pull.change_turn()
        h += 1

    del current_pull
    s_q.put(sim_reward)
'''
1. THIS METHOD GENERATES ONE UCT TREE AND RETURNS THE REWARDS OF ALL THE ACTIONS
AND THE VISIT COUNT. COULD BE INVOKED IN PARALLEL OR SEQ.
2. I HAVE KEPT IT OUTSIDE THE CLASS BECAUSE OF PICKLING PROBLEMS WHILE MULTIPROC
INITIALIZING.
'''
def generate_tree(pnum, current_simulator, current_state, sim_count, tree_pol, rollout, uct_const, hor, threadcount,
                  time_limit, out_q):
    current_turn = current_state.get_current_state()["current_player"]
    current_simulator.change_simulator_state(current_state)
    valid_actions = current_simulator.get_valid_actions()
    actions_count = len(valid_actions)

    if actions_count <= 1:
        return valid_actions[0]

    global uctnode
    root_node = uctnode(current_state, valid_actions, True)
    current_node = root_node
    visit_stack = [current_node]
    curr_sim_count = 0
    num_nodes = 0

    while curr_sim_count < sim_count:
        if time_limit != -1.0:
            global  start_time
            end_time = timeit.default_timer()
            if end_time - start_time > time_limit:
                break
        # CHOOSE A NODE USING TREE POLICY. NODE SELECTION.
        while len(current_node.valid_actions) > 0 and len(current_node.children_list) == len(current_node.valid_actions):
            if tree_pol == "UCB":
                max_val = 0
                sel_node = 0
                for node in xrange(len(current_node.children_list)):
                    node_turn = current_node.state_value.get_current_state()["current_player"]
                    value = current_node.children_list[node].reward[node_turn - 1]
                    exploration = math.sqrt(math.log(current_node.state_visit) / current_node.children_list[node].state_visit)
                    value += uct_const * exploration

                    if (node == 0):
                        max_val = value
                    else:
                        if value > max_val:
                            max_val = value
                            sel_node = node

                current_node.state_visit += 1
                current_node = current_node.children_list[sel_node]
                visit_stack.append(current_node)

        #SEE IF THE CURRENT NODE IS A TERMINAL NODE. IF YES, JUST RETURN ITS Q VALUE TO BE BACKTRACKED.
        current_node.state_visit += 1
        curr_sim_count += 1

        if current_node.is_terminal:
            q_vals = current_node.reward
        else:
            #PULL A NEW ACTION ARM AND CREATE THE NEW STATE.
            current_simulator.change_simulator_state(current_node.state_value)
            current_pull = current_simulator.create_copy()
            actual_reward = current_pull.take_action(current_node.valid_actions[len(current_node.children_list)])
            current_pull.change_turn()

            ## SIMULATE TILL END AND GET THE REWARD.
            ## HERE SIMULATION TAKES PLACE PARALLELY.
            process_list = []
            output_que = Queue(threadcount)
            for proc in xrange(threadcount):
                worker_proc = Process(target=_simulate_game, args=(rollout.create_copy(),
                                                                   current_pull.create_copy(), hor,
                                                                   output_que,))
                #worker_proc.daemon = True
                process_list.append(worker_proc)
                worker_proc.start()

            for worker in process_list:
                worker.join()

            # AVERAGE THE REWARDS FROM PARALLEL SIMULATIONS
            sim_reward = [0.0] * current_pull.numplayers
            for thread in xrange(threadcount):
                temp_reward = output_que.get()
                sim_reward = [x+y for x,y in zip(temp_reward, sim_reward)]

            sim_reward = [float(x / threadcount) for x in sim_reward]

            q_vals = [x + y for x, y in zip(actual_reward, sim_reward)]


            ##CREATE NEW NODE AND APPEND TO CURRENT NODE. THIS NODE HAS THE NEW TURN IN ITS STATE (THE NEXT PLAYER).
            num_nodes += 1
            global uctnode
            child_node = uctnode(current_pull.get_simulator_state(), current_pull.get_valid_actions(), False)
            child_node.reward = q_vals
            child_node.state_visit += 1
            child_node.is_terminal = current_pull.gameover
            current_node.children_list.append(child_node)

            del current_pull

        ##BACKTRACK REWARDS UNTIL ROOT NODE
        for node in xrange(len(visit_stack) - 1, -1, -1):
            if visit_stack[node].is_root == False:
                temp_diff = [x - y for x, y in zip(q_vals, visit_stack[node].reward)]
                temp_qterm = [float(x) / float(visit_stack[node].state_visit) for x in temp_diff]
                visit_stack[node].reward = [x + y for x, y in zip(visit_stack[node].reward, temp_qterm)]

        ##REVERT BACK TO ROOT
        current_node = root_node
        visit_stack = [current_node]

        end_time = timeit.default_timer()

    print "BLK", curr_sim_count
    global  total_count
    total_count += curr_sim_count

    rewards = []
    visits = []

    for kid in root_node.children_list:
        rewards.append(kid.reward[current_turn - 1])
        visits.append(kid.state_visit)

    out_q.put([rewards, visits])


class BlockParallelUCTClass(absagent.AbstractAgent):
    myname = "UCT-BP"

    def __init__(self, simulator, rollout_policy, tree_policy, num_simulations, uct_constant=1, threadcount = 5, ensembles=2, horizon=10,
                 parallel=False, time_limit=-1):
        self.agentname = self.myname
        self.rollout_policy = rollout_policy
        self.simulator = simulator.create_copy()
        self.tree_policy = tree_policy
        self.uct_constant = uct_constant
        self.simulation_count = num_simulations
        self.ensemble_count = ensembles
        self.horizon = horizon
        self.thread_count = threadcount
        self.time_limit = time_limit

    def create_copy(self):
        return BlockParallelUCTClass(self.simulator.create_copy(), self.rollout_policy.create_copy(),
                                     self.tree_policy, self.simulation_count, self.uct_constant, self.threadcount,
                                     self.ensemble_count, self.horizon)

    def get_agent_name(self):
        return self.agentname

    def select_action(self, current_state):
        current_turn = current_state.get_current_state()["current_player"]
        self.simulator.change_simulator_state(current_state)
        valid_actions = self.simulator.get_valid_actions()
        actions_count = len(valid_actions)

        if actions_count == 1:
            return valid_actions[0]

        reward_values = []
        visit_counts = []
        output_que = Queue(self.ensemble_count)

        if self.time_limit != -1.0:
            self.simulation_count = 30000000000000000000000000

        global  overall_results
        global  total_count
        overall_results = []
        total_count = 0

        global  start_time
        start_time = timeit.default_timer()

        process_list = []
        for proc in xrange(self.ensemble_count):
            worker_proc = Process(target=generate_tree, args=(proc,
                                                              self.simulator.create_copy(),
                                                              current_state.create_copy(),
                                                              self.simulation_count,
                                                              self.tree_policy,
                                                              self.rollout_policy.create_copy(),
                                                              self.uct_constant,
                                                              self.horizon,
                                                              self.thread_count,
                                                              self.time_limit,
                                                              output_que,))
            process_list.append(worker_proc)
            worker_proc.start()

        for worker in process_list:
            worker.join()

        for val in xrange(self.ensemble_count):
            q_output = output_que.get()
            reward_values.append(q_output[0])
            visit_counts.append(q_output[1])

        global total_count
        #print "BLK", total_count

        # NEED NOT WORRY ABOUT SPECIFYING CURRENT PLAYER'S TURN HERE. WE PASS THE TURN
        # WHILE CREATING UCT AGENT AND WE RETRIEVE ONLY THE PLAYER OF INTEREST'S
        # REWARD.
        best_avg = 0.0
        best_arm = 0
        # COMPARE FOR BEST AVG
        for arm in xrange(0, len(reward_values[0])):
            curr_avg = 0.0
            numer = 0.0
            denom = 0.0
            for ensemble in xrange(len(reward_values)):
                try:
                    numer += reward_values[ensemble][arm] * visit_counts[ensemble][arm]
                    denom += visit_counts[ensemble][arm]
                except IndexError:
                    pass

            curr_avg = numer / denom

            if arm == 0:
                best_avg = curr_avg
            else:
                if curr_avg > best_avg:
                    best_avg = curr_avg
                    best_arm = arm

        return valid_actions[best_arm]


