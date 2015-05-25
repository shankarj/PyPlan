from abstract import absagent
import math
import sys
import timeit
import multiprocessing
from multiprocessing.managers import BaseManager
from multiprocessing import Process, Lock, Manager, Event, Queue
import time

class TreeSpaceManager(BaseManager): pass

def StartManager():
    temp_mgr = TreeSpaceManager()
    temp_mgr.start()
    return temp_mgr

class uctnode:
    def __init__(self, node_state, action_list, is_root, is_terminal):
        self.node_id = 0
        self.state_value = node_state
        self.valid_actions = action_list
        self.is_root = is_root
        self.state_visit = 0
        self.children_list = []
        self.reward = []
        self.is_terminal = is_terminal

class TreeSpace(object):
    def __init__(self):
        self.total_nodes = 0
        self.node_dictionary = {}
        self.initialized = False
        self.locks = {}

    def initialize_space(self, node_current_state, node_valid_actions, tree_policy, rollout_pol, horizon, uct_constant):
        self.root = uctnode(node_current_state, node_valid_actions, True, False)
        self.create_new_lock(0)
        self.node_dictionary[0] = self.root
        self.total_nodes += 1
        self.tree_policy = tree_policy
        self.uct_constant = uct_constant
        self.rollout_policy = rollout_pol
        self.horizon = horizon
        self.initialized = True

    def create_new_lock(self, node_id):
        temp_lock = multiprocessing.Lock()
        self.locks[node_id] = temp_lock
        return temp_lock

    def shut_all_locks(self):
        for lock in self.locks:
            del lock

    def get_node_object(self, node_num):
        return self.node_dictionary[node_num]

    def backpropagate(self, visit_stack, value, pnum):
        s_t = timeit.default_timer()
        self.locks[0].acquire()
        e_t = timeit.default_timer()

        for node in visit_stack:
            for node in xrange(len(visit_stack) - 1, -1, -1):
                node_id = visit_stack[node]
                if self.node_dictionary[node_id].is_root == False:
                    temp_diff =  [x - y for x, y in zip(value, self.node_dictionary[node_id].reward)]
                    temp_qterm =  [float(x) / float(self.node_dictionary[node_id].state_visit) for x in temp_diff]
                    self.node_dictionary[node_id].reward = [x + y for x, y in zip(self.node_dictionary[node_id].reward, temp_qterm)]

        self.locks[0].release()

    def root_initialized(self):
        return self.initialized

    def lock_and_get_node(self, node_id, pnum):
        self.locks[node_id].acquire()
        return self.node_dictionary[node_id]

    def get_node(self, node_id, pnum):
        return self.node_dictionary[node_id]

    def release_lock(self, node_id, pnum):
        self.locks[node_id].release()

    def create_child_node(self, parent_id, node_state, node_valid_actions, is_root, playercount, gameover):
        temp_node = uctnode(node_state, node_valid_actions, is_root, gameover)
        temp_node.node_id = id(temp_node)
        self.create_new_lock(temp_node.node_id)
        temp_node.state_visit = 1
        temp_node.reward = [0.0] * playercount
        self.node_dictionary[temp_node.node_id] = temp_node
        self.node_dictionary[parent_id].children_list.append(temp_node)
        self.total_nodes += 1
        return temp_node.node_id

    def increase_visit_count(self, node_id):
        self.node_dictionary[node_id].state_visit += 1

TreeSpaceManager.register('TreeSpace', TreeSpace)

# PARALLEL CODE. THIS IS THE CODE THAT RUNS ON INDIVIDUAL PROCESS'S SPACE.
def worker_code(pnum, mgr_obj, sim_obj, tree_policy, rollout_policy, uct_constant, sim_count, horizon, time_limit, start_time):
    sim_c = 0

    end_time = timeit.default_timer()

    while sim_c < sim_count:
        if time_limit != -1.0:
            if end_time - start_time > time_limit:
                break

        current_node = mgr_obj.lock_and_get_node(node_id=0, pnum=pnum)
        current_node_id = current_node.node_id
        visit_stack = [0]
        mgr_obj.increase_visit_count(current_node_id)

        #print "SELECTING"
        while len(current_node.valid_actions) > 0 and len(current_node.children_list) == len(current_node.valid_actions):
            if tree_policy == "UCB":
                max_val = 0
                sel_node = 0
                for node in xrange(len(current_node.children_list)):
                    node_turn = current_node.state_value.get_current_state()["current_player"]
                    value = current_node.children_list[node].reward[node_turn - 1]
                    exploration = math.sqrt(math.log(current_node.state_visit) / current_node.children_list[node].state_visit)

                    value += uct_constant * exploration

                    if (node == 0):
                        max_val = value
                    else:
                        if value > max_val:
                            max_val = value
                            sel_node = node

                # GET NEXT SELECTED NODE'S ID. RELEASE THE CURRENT NODE.
                # CHANGE CURRENT NODE TO THE NEXT NODE OBJECT.
                next_node_id = current_node.children_list[sel_node].node_id
                current_node = mgr_obj.get_node(next_node_id, pnum)
                current_node_id = next_node_id
                visit_stack.append(next_node_id)
                mgr_obj.increase_visit_count(current_node_id)

        simulation_rew = [0.0] * sim_obj.numplayers
        actual_reward = [0.0] * sim_obj.numplayers

        #print "CHECKING IF TERMINAL"
        if current_node.is_terminal:
            simulation_rew = current_node.reward
            mgr_obj.release_lock(node_id=0, pnum=pnum)
        else:
            #print "CREATING"
            sim_obj.change_simulator_state(current_node.state_value)
            current_pull = sim_obj.create_copy()
            actual_reward = current_pull.take_action(current_node.valid_actions[len(current_node.children_list)])
            current_pull.change_turn()

            # NODE EXPANSION. ADD NEW NODE TO VISIT STACK.
            new_node_id = mgr_obj.create_child_node(current_node_id, current_pull.get_simulator_state(),
                                current_pull.get_valid_actions(), False, sim_obj.numplayers, current_pull.gameover)
            visit_stack.append(new_node_id)
            mgr_obj.release_lock(node_id=0, pnum=pnum)

            # START SIMULATION. LOCK IS RELEASED IN PREVIOUS STEP.
            # SO THIS SIMULATION RUNS IN PARALLEL TO OTHER STEPS.
            temp_pull = sim_obj.create_copy()
            simulation_rew = [0.0] * temp_pull.numplayers
            h = 0

            while temp_pull.gameover == False and h <= horizon:
                action_to_take = rollout_policy.select_action(temp_pull.current_state)
                current_pull_reward = temp_pull.take_action(action_to_take)
                simulation_rew = [x + y for x, y in zip(simulation_rew, current_pull_reward)]
                temp_pull.change_turn()
                h += 1

            del temp_pull

        q_vals = [x+y for x,y in zip(actual_reward, simulation_rew)]

        # LOCK AND BACKPROPAGATE.
        mgr_obj.backpropagate(visit_stack, q_vals, pnum)
        sim_c += 1

        end_time = timeit.default_timer()

    print "GM SIM COUNT", sim_c
    sim_count_file = open("Results/TPGM-" + str(pnum) + ".csv", "w")
    sim_count_file.write(str(sim_c) + "\n")
    sim_count_file.close()


class TreeParallelUCTGMClass(absagent.AbstractAgent):
    myname = "UCT-TP-GM"

    def __init__(self, simulator, rollout_policy, tree_policy, num_simulations, threadcount, uct_constant, horizon, time_limit=-1):
        self.agentname = self.myname
        self.rollout_policy = rollout_policy
        self.simulator = simulator.create_copy()
        self.tree_policy = tree_policy
        self.uct_constant = uct_constant
        self.simulation_count = num_simulations
        self.horizon = horizon
        self.thread_count = threadcount
        self.time_limit = time_limit

    def create_copy(self):
        return TreeParallelUCTGMClass(self.simulator.create_copy(), self.rollout_policy.create_copy(),
                                       self.tree_policy, self.simulation_count, self.thread_count,
                                       self.uct_constant, self.horizon, self.time_limit)

    def get_agent_name(self):
        return self.agentname

    def select_action(self, current_state):
        TreeSpaceManager.register('TreeSpace', TreeSpace)
        current_turn = current_state.get_current_state()["current_player"]
        self.simulator.change_simulator_state(current_state)
        valid_actions = self.simulator.get_valid_actions()
        actions_count = len(valid_actions)

        if actions_count <= 1:
            return valid_actions[0]

        mgr = StartManager()
        tree_space = mgr.TreeSpace()
        tree_space.initialize_space(current_state,
                                    valid_actions, self.tree_policy,
                                    self.rollout_policy, self.horizon, self.uct_constant)

        process_q = []
        count = 0

        if self.time_limit != -1:
            self.simulation_count = 30000000000000000000000000

        for proc in xrange(self.thread_count):
            start_time = timeit.default_timer()
            worker_process = Process (target=worker_code, args=(proc, tree_space, self.simulator, self.tree_policy,
                                                                self.rollout_policy, self.uct_constant,
                                                                self.simulation_count, self.horizon, self.time_limit,
                                                                start_time))
            process_q.append(worker_process)
            worker_process.daemon = True
            worker_process.start()
            count += 1

        for elem in process_q:
            elem.join()

        best_arm = 0
        best_reward = tree_space.get_node_object(0).children_list[0].reward[current_turn - 1]

        #print "------------TREE VISIT", tree_space.get_node_object(0).state_visit

        for arm in xrange(len(tree_space.get_node_object(0).children_list)):
            #print "CHILD VISIT", tree_space.get_node_object(0).children_list[arm].state_visit
            if tree_space.get_node_object(0).children_list[arm].reward[current_turn - 1] > best_reward:
                best_reward = tree_space.get_node_object(0).children_list[arm].reward[current_turn - 1]
                best_arm = arm

        tree_space.shut_all_locks()
        mgr.shutdown()

        return valid_actions[best_arm]


