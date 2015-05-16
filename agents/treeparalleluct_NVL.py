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
    def __init__(self, node_state, action_list, is_root, lock_obj, is_terminal):
        self.node_id = 0
        self.state_value = node_state
        self.valid_actions = action_list
        self.is_root = is_root
        self.state_visit = 0
        self.children_list = []
        self.reward = []
        self.is_terminal = is_terminal
        self.lockobj = lock_obj

class TreeSpace(object):
    def __init__(self):
        self.total_nodes = 0
        self.node_dictionary = {}
        self.initialized = False
        self.locks = []

    def initialize_space(self, node_current_state, node_valid_actions, tree_policy, rollout_pol, horizon, uct_constant):
        self.root = uctnode(node_current_state, node_valid_actions, True, self.create_new_lock(), False)
        self.node_dictionary[0] = self.root
        self.total_nodes += 1
        self.tree_policy = tree_policy
        self.uct_constant = uct_constant
        self.rollout_policy = rollout_pol
        self.horizon = horizon
        self.initialized = True
        self.node_counter_lock = self.create_new_lock()

    def create_new_lock(self):
        new_mgr = Manager()
        self.locks.append(new_mgr)
        return new_mgr.Lock()

    def shut_all_locks(self):
        for lock in self.locks:
            lock.shutdown()

    def get_node_object(self, node_num):
        return self.node_dictionary[node_num]

    def backtrack(self, visit_stack, value, pnum):
        s_t = timeit.default_timer()
        self.node_dictionary[0].lockobj.acquire()
        e_t = timeit.default_timer()
        for node in visit_stack:
            for node in xrange(len(visit_stack) - 1, -1, -1):
                node_id = visit_stack[node]
                if self.node_dictionary[node_id].is_root == False:


                    print "PROCESS WAITED FOR ", str(e_t - s_t) ," IN BACKTRACK ONLY LOCK ON NODE"
                    temp_diff =  [x - y for x, y in zip(value, self.node_dictionary[node_id].reward)]
                    temp_qterm =  [float(x) / float(self.node_dictionary[node_id].state_visit) for x in temp_diff]
                    self.node_dictionary[node_id].reward = [x + y for x, y in zip(self.node_dictionary[node_id].reward, temp_qterm)]
        self.node_dictionary[0].lockobj.release()

    def simulate_and_backtrack(self, visit_stack, sim_obj, pnum):
        # NODE EXPANSION AND SIMULATION
        simulation_rew = 0.0

        current_node = self.node_dictionary[visit_stack[-1]]
        actual_reward = current_node.reward[:]

        # REVERT (TO 0.0) THE ACTUAL REWARD TEMPORARILY ADDED IN THE NEW NODE.
        self.node_dictionary[visit_stack[-1]].reward = [0.0] * sim_obj.numplayers

        # NODE SIMULATION.
        sim_obj.change_simulator_state(current_node.state_value)
        temp_pull = sim_obj.create_copy()
        del sim_obj
        simulation_rew = [0.0] * temp_pull.numplayers
        h = 0

        while temp_pull.gameover == False and h <= self.horizon:
            action_to_take = self.rollout_policy.select_action(temp_pull.current_state)
            current_pull_reward = temp_pull.take_action(action_to_take)
            simulation_rew = [x + y for x, y in zip(simulation_rew, current_pull_reward)]
            temp_pull.change_turn()
            h += 1

        del temp_pull

        q_vals = [x+y for x,y in zip(actual_reward, simulation_rew)]

        # BACKTRACK
        self.backtrack(visit_stack, q_vals, pnum)

    # THIS FUNCTION RETURNS THE VISIT STACK FROM ROOT NODE
    def node_selection(self, sim_obj, pnum):
        root_node = self.node_dictionary[0]
        visit_stack = [0]
        current_node = root_node

        s_t = timeit.default_timer()
        current_node.lockobj.acquire()
        e_t = timeit.default_timer()
        print "PROCESS WAITED FOR ", str(e_t - s_t) ," IN ROOT LOCK."
        node_num = current_node.node_id
        return_value = []

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

                self.node_dictionary[node_num].state_visit += 1
                visit_stack.append(node_num)
                current_node.lockobj.release()

                # CHANGE CURRENT NODE TO NEXT SELECTED NODE
                current_node = self.node_dictionary[node_num].children_list[sel_node]
                s_t = timeit.default_timer()
                current_node.lockobj.acquire()
                e_t = timeit.default_timer()
                print "PROCESS WAITED FOR ", str(e_t - s_t) ," IN A NODE LOCK."
                node_num = current_node.node_id


        self.node_dictionary[node_num].state_visit += 1

        if current_node.is_terminal:
            simulation_rew = current_node.reward
            return_value = [0, visit_stack, simulation_rew]
            current_node.lockobj.release()
        else:
            sim_obj.change_simulator_state(current_node.state_value)
            current_pull = sim_obj.create_copy()
            actual_reward = current_pull.take_action(current_node.valid_actions[len(current_node.children_list)])

            current_pull.change_turn()
            temp_node = uctnode(current_pull.get_simulator_state(),
                                current_pull.get_valid_actions(), False, self.create_new_lock(), current_pull.gameover)
            temp_node.node_id = id(temp_node)
            temp_node.reward = actual_reward
            temp_node.state_visit += 1
            self.node_dictionary[temp_node.node_id] = temp_node
            self.node_dictionary[current_node.node_id].children_list.append(temp_node)
            self.total_nodes += 1
            current_node.lockobj.release()


            visit_stack.append(temp_node.node_id)
            return_value = [1, visit_stack, current_pull]

        return return_value

    def root_initialized(self):
        return self.initialized

TreeSpaceManager.register('TreeSpace', TreeSpace)

# PARALLEL CODE. THIS IS THE CODE THAT RUNS ON INDIVIDUAL PROCESS SPACE.
def worker_code(pnum, mgr_obj, sim_obj, sim_count):
    sim_c = 0

    while sim_c < sim_count:
        s_t = timeit.default_timer()
        ## NEW CODE BEGINS
        current_node = mgr_obj.lock_and_get_node(0)
        current_node_id = current_node.node_id
        visit_stack = []
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

                visit_stack.append(current_node_id)
                mgr_obj.release_lock(current_node_id)

                # CHANGE CURRENT NODE TO NEXT SELECTED NODE
                next_node_id = mgr_obj.get_node_id(parent_node_id=current_node.node_id, )
                current_node = mgr_obj.lock_and_get_node(next_node_id)

        simulation_rew = []
        if current_node.is_terminal:
            simulation_rew = current_node.reward
        else:
            sim_obj.change_simulator_state(current_node.state_value)
            current_pull = sim_obj.create_copy()

            actual_reward = current_pull.take_action(current_node.valid_actions[len(current_node.children_list)])

            current_pull.change_turn()
            temp_node = uctnode(current_pull.get_simulator_state(),
                                current_pull.get_valid_actions(), False, self.create_new_lock(), current_pull.gameover)
            temp_node.node_id = id(temp_node)
            temp_node.reward = actual_reward
            temp_node.state_visit += 1
            self.node_dictionary[temp_node.node_id] = temp_node
            self.node_dictionary[current_node.node_id].children_list.append(temp_node)
            self.total_nodes += 1
            mgr_obj.release_lock(current_node_id)


        ## NEW CODE ENDS

        # NODE SELECTION
        parent_node_num = 0
        ret_val = mgr_obj.node_selection(sim_obj, pnum)

        if ret_val[0] == 0:
            # BACKTRACK ONLY FOR TERMINAL NODES.
            mgr_obj.backtrack(ret_val[1], ret_val[2], pnum)
        elif ret_val[0] == 1:
            # SIMULATE AND BACKTRACK VALUES.
            mgr_obj.simulate_and_backtrack(ret_val[1], ret_val[2], pnum)

        sim_c += 1
        e_t = timeit.default_timer()
        print "ONE SIMULATION TIME IN ONE PROCESS", e_t - s_t

class TreeParallelUCTNVLClass(absagent.AbstractAgent):
    myname = "UCT-TP-NVL"

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
        return TreeParallelUCTNVLClass(self.simulator.create_copy(), self.rollout_policy.create_copy(),
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
        for proc in xrange(self.thread_count):
            worker_process = Process (target=worker_code, args=(proc, tree_space, self.simulator, self.simulation_count))
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


