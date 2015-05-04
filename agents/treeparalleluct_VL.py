from abstract import absagent
import math
import sys
import timeit
import multiprocessing
from multiprocessing.managers import BaseManager
from multiprocessing import Process, Lock, Manager, Event, Queue
import os
import signal
import psutil
import time
import  subprocess

class TreeSpaceManager(BaseManager): pass

def StartManager():
    temp_mgr = TreeSpaceManager()
    temp_mgr.start()
    return temp_mgr

class uctnode:
    def __init__(self, node_num, node_state, action_list, is_root, lock_obj, is_terminal):
        self.node_number = node_num
        self.state_value = node_state
        self.valid_actions = action_list
        self.is_root = is_root
        self.state_visit = 0
        self.children_list = []
        self.reward = []
        self.is_terminal = is_terminal
        self.lockobj = lock_obj
        self.virtual_loss = []

class TreeSpace(object):
    def __init__(self):
        self.total_nodes = 0
        self.node_dictionary = {}
        self.initialized = False
        self.locks = []

    def create_new_lock(self):
        new_mgr = Manager()
        self.locks.append(new_mgr)
        return new_mgr.Lock()

    def shut_all_locks(self):
        for lock in self.locks:
            lock.shutdown()

    def initialize_space(self, node_current_state, node_valid_actions, tree_policy, rollout_pol, horizon, uct_constant):
        self.root = uctnode(self.total_nodes, node_current_state, node_valid_actions, True, self.create_new_lock(), False)
        self.node_dictionary[self.total_nodes] = self.root
        self.total_nodes += 1
        self.tree_policy = tree_policy
        self.uct_constant = uct_constant
        self.rollout_policy = rollout_pol
        self.horizon = horizon
        self.initialized = True

    def backtrack_values(self, value, visit_stack, pnum):
        for node in xrange(len(visit_stack) - 1, -1, -1):
            if self.node_dictionary[visit_stack[node]].is_root == False:
                with self.node_dictionary[visit_stack[node]].lockobj:
                    # DELETE VIRTUAL LOSS ADDED BY PROCESS.
                    # print "NODE NUM", node
                    # print "DEL IN", self.node_dictionary[visit_stack[node]].node_number, "BY", pnum, "STACK", visit_stack
                    # print "DELETED"
                    temp_diff =  [x - y for x, y in zip(value, self.node_dictionary[visit_stack[node]].reward)]
                    temp_qterm =  [float(x) / float(self.node_dictionary[visit_stack[node]].state_visit) for x in temp_diff]
                    self.node_dictionary[visit_stack[node]].reward = [x + y for x, y in zip(self.node_dictionary[visit_stack[node]].reward, temp_qterm)]

                    #print "LOSS STACK", self.node_dictionary[visit_stack[node]].virtual_loss
                    try:
                        del self.node_dictionary[visit_stack[node]].virtual_loss[-1]
                    except Exception:
                        continue

    def get_node_object(self, node_num):
        return self.node_dictionary[node_num]

    # RETURNS THE SELECTED NODE NUMBER AT THE GIVEN NODE NUMBER USING A TREE POLICY
    def node_selection(self, node_num, sim_obj, pnum, vloss):
        current_node = self.node_dictionary[node_num]
        return_value = []

        current_node.lockobj.acquire()
        if len(current_node.valid_actions) > 0 and len(current_node.children_list) == len(current_node.valid_actions):
            if self.tree_policy == "UCB":
                max_val = 0
                sel_node = 0
                for node in xrange(len(current_node.children_list)):
                    loss_total = 0.0
                    for each_loss in current_node.virtual_loss:
                        loss_total += each_loss
                    node_turn = current_node.state_value.get_current_state()["current_player"]
                    value = current_node.children_list[node].reward[node_turn - 1] - loss_total
                    exploration = math.sqrt(math.log(current_node.state_visit) / current_node.children_list[node].state_visit)
                    value += self.uct_constant * exploration

                    if (node == 0):
                        max_val = value
                    else:
                        if value > max_val:
                            max_val = value
                            sel_node = node

                self.node_dictionary[node_num].state_visit += 1
                self.node_dictionary[node_num].children_list[sel_node].virtual_loss.append(vloss)
                # print "VLOSS ADDED TO", self.node_dictionary[node_num].children_list[sel_node].node_number, "BY", pnum
                return_value = [1, self.node_dictionary[node_num].children_list[sel_node].node_number]
        else:
            # NODE EXPANSION AND SIMULATION
            simulation_rew = 0.0
            self.node_dictionary[node_num].state_visit += 1

            if current_node.is_terminal:
                simulation_rew = current_node.reward
                return_value = [0, simulation_rew]
            else:
                sim_obj.change_simulator_state(current_node.state_value)
                current_pull = sim_obj.create_copy()
                actual_reward = current_pull.take_action(current_node.valid_actions[len(current_node.children_list)])
                current_pull.change_turn()

                # NODE SIMULATION.
                temp_pull = current_pull.create_copy()
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

                # NODE CREATION.
                ## NOTE: REWARD FOR THIS NEW NODE = ACTUAL + SIM_REWARD. SO THIS NODE IS NOT INCLUDED IN
                ## THE VISIT_STACK FOR BACKTRACKING.
                temp_node = uctnode(self.total_nodes, current_pull.get_simulator_state(),
                                    current_pull.get_valid_actions(), False, self.create_new_lock(), current_pull.gameover)
                temp_node.reward = q_vals
                temp_node.state_visit += 1
                self.node_dictionary[self.total_nodes] = temp_node
                self.node_dictionary[node_num].children_list.append(temp_node)
                self.total_nodes += 1

                del current_pull

                return_value = [-1, q_vals]

        current_node.lockobj.release()

        return return_value

    def root_initialized(self):
        return self.initialized

# PARALLELIZED CODE.
def worker_code(pnum, mgr_obj, sim_obj, vloss):
    visit_stack = [0]

    # NODE SELECTION
    parent_node_num = 0
    current_node_work = mgr_obj.node_selection(0, sim_obj, pnum, vloss)
    while current_node_work[0] == 1:
        visit_stack.append(current_node_work[1])
        parent_node_num = current_node_work[1]
        current_node_work = mgr_obj.node_selection(current_node_work[1], sim_obj, pnum, vloss)

    # BACKTRACK VALUES. STARTS FROM PARENT OF THE NODE JUST CREATED/CHOOSEN TO THE
    # CHILD OF THE ROOT NODE IN THE TRAJECTORY.
    simulation_rew = current_node_work[1]
    mgr_obj.backtrack_values(simulation_rew, visit_stack, pnum)

class TreeParallelUCTVLClass(absagent.AbstractAgent):
    myname = "UCT-TP-VL"

    def __init__(self, simulator, rollout_policy, tree_policy, num_simulations, num_threads = 5, uct_constant=1, horizon=10, virtual_loss=1.0):
        self.agentname = self.myname
        self.rollout_policy = rollout_policy
        self.simulator = simulator.create_copy()
        self.tree_policy = tree_policy
        self.uct_constant = uct_constant
        self.simulation_count = num_simulations
        self.horizon = horizon
        self.threadcount = num_threads
        self.virtual_loss = virtual_loss

    def create_copy(self):
        return TreeParallelUCTVLClass(self.simulator.create_copy(), self.rollout_policy.create_copy(), self.tree_policy, self.simulation_count, self.uct_constant, self.horizon)

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

        for proc in xrange(self.simulation_count):
            done_event = multiprocessing.Event()
            worker_process = Process (name="worker_process", target=worker_code, args=(proc, tree_space,
                                                                                       self.simulator,
                                                                                       self.virtual_loss))
            process_q.append(worker_process)
            worker_process.start()
            time.sleep(0.01)

        for each_proc in process_q:
            each_proc.join()

        best_arm = 0
        best_reward = tree_space.get_node_object(0).children_list[0].reward[current_turn - 1]

        print "------------TREE VISIT", tree_space.get_node_object(0).state_visit

        for arm in xrange(len(tree_space.get_node_object(0).children_list)):
            print "CHILD VISIT", tree_space.get_node_object(0).children_list[arm].state_visit
            if tree_space.get_node_object(0).children_list[arm].reward[current_turn - 1] > best_reward:
                best_reward = tree_space.get_node_object(0).children_list[arm].reward[current_turn - 1]
                best_arm = arm

        tree_space.shut_all_locks()
        mgr.shutdown()

        return valid_actions[best_arm]


