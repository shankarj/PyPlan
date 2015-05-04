import multiprocessing
from multiprocessing.managers import BaseManager
from multiprocessing import Process, Lock, Manager, Event
import time
from agents import *
from simulators import *
from states import *
import math
import os
import psutil

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

class TreeSpace(object):
    def __init__(self):
        self.total_nodes = 0
        self.node_dictionary = {}
        self.initialized = False

    def initialize_space(self, node_current_state, node_valid_actions, tree_policy, rollout_pol, horizon, uct_constant):
        self.root = uctnode(self.total_nodes, node_current_state, node_valid_actions, True, Manager().Lock(), False)
        self.node_dictionary[self.total_nodes] = self.root
        self.total_nodes += 1
        self.tree_policy = tree_policy
        self.uct_constant = uct_constant
        self.rollout_policy = rollout_pol
        self.horizon = horizon
        self.initialized = True

    def backtrack_values(self, value, visit_stack, pnum):
        for node in visit_stack:
            for node in xrange(len(visit_stack) - 1, -1, -1):
                if self.node_dictionary[visit_stack[node]].is_root == False:
                    with self.node_dictionary[visit_stack[node]].lockobj:
                        temp_diff =  [x - y for x, y in zip(value, self.node_dictionary[visit_stack[node]].reward)]
                        temp_qterm =  [float(x) / float(self.node_dictionary[visit_stack[node]].state_visit) for x in temp_diff]
                        self.node_dictionary[visit_stack[node]].reward = [x + y for x, y in zip(self.node_dictionary[visit_stack[node]].reward, temp_qterm)]

    def get_node_object(self, node_num):
        return self.node_dictionary[node_num]

    # RETURNS THE SELECTED NODE NUMBER AT THE GIVEN NODE NUMBER USING A TREE POLICY
    def node_selection(self, node_num, sim_obj, pnum):
        current_node = self.node_dictionary[node_num]
        return_value = []

        current_node.lockobj.acquire()
        if len(current_node.valid_actions) > 0 and len(current_node.children_list) == len(current_node.valid_actions):
            if self.tree_policy == "UCB":
                max_val = 0
                sel_node = 0
                #print "CHILD LIST LEN", len(current_node.children_list)
                for node in xrange(len(current_node.children_list)):
                    node_turn = current_node.state_value.get_current_state()["current_player"]
                    #print "REWARD GUY", current_node.children_list[node].reward
                    value = current_node.children_list[node].reward[node_turn - 1]
                    #print "qwe", current_node.state_visit
                    exploration = math.sqrt(math.log(current_node.state_visit) / current_node.children_list[node].state_visit)
                    value += self.uct_constant * exploration

                    if (node == 0):
                        max_val = value
                    else:
                        if value > max_val:
                            max_val = value
                            sel_node = node

                self.node_dictionary[node_num].state_visit += 1
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
                print "\nACTUAL NODE ACTION", current_node.valid_actions[len(current_node.children_list)].get_action(), "PNUM", pnum
                actual_reward = current_pull.take_action(current_node.valid_actions[len(current_node.children_list)])
                print "TURN BEFORE CHANGE", current_pull.get_simulator_state().get_current_state()["current_player"]
                current_pull.change_turn()
                print "TURN AFTER CHANGE", current_pull.get_simulator_state().get_current_state()["current_player"]

                # NODE SIMULATION.
                temp_pull = current_pull.create_copy()
                print "SIM START TURN : ", temp_pull.get_simulator_state().get_current_state()["current_player"]
                simulation_rew = [0.0] * temp_pull.numplayers
                h = 0
                while temp_pull.gameover == False and h <= self.horizon:
                    action_to_take = self.rollout_policy.select_action(temp_pull.current_state)
                    print "ACTION TAKEN", action_to_take.get_action(), "PNUM", pnum
                    current_pull_reward = temp_pull.take_action(action_to_take)
                    simulation_rew = [x + y for x, y in zip(simulation_rew, current_pull_reward)]
                    temp_pull.change_turn()
                    h += 1

                print "FINAL SIM STATE", temp_pull.get_simulator_state().get_current_state(), "PNUM", pnum
                print "SIM REW", simulation_rew, "PNUM", pnum
                print "ACTUAL REW", actual_reward, "PNUM", pnum
                del temp_pull

                q_vals = [x+y for x,y in zip(actual_reward, simulation_rew)]

                # NODE CREATION.
                ## NOTE: REWARD FOR THIS NEW NODE = ACTUAL + SIM_REWARD. SO THIS NODE IS NOT INCLUDED IN
                ## THE VISIT_STACK FOR BACKTRACKING.
                print "STATE TO CREATE", current_pull.get_simulator_state().get_current_state(), "PNUM", pnum
                print "!!!  NODE REWARD CREATED", q_vals, "PNUM", pnum, "\n"
                temp_node = uctnode(self.total_nodes, current_pull.get_simulator_state(),
                                    current_pull.get_valid_actions(), False, Manager().Lock(), current_pull.gameover)
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

TreeSpaceManager.register('TreeSpace', TreeSpace)

def worker_code(pnum, mgr_obj, sim_obj):
    visit_stack = [0]

    # NODE SELECTION
    parent_node_num = 0
    current_node_work = mgr_obj.node_selection(0, sim_obj, pnum)
    while current_node_work[0] == 1:
        #print "CHOSEN NODE", current_node_work[1]
        visit_stack.append(current_node_work[1])
        parent_node_num = current_node_work[1]
        current_node_work = mgr_obj.node_selection(current_node_work[1], sim_obj, pnum)

    # BACKTRACK VALUES. STARTS FROM PARENT OF THE NODE JUST CREATED/CHOOSEN TO THE
    # CHILD OF THE ROOT NODE IN THE TRAJECTORY.
    simulation_rew = current_node_work[1]
    mgr_obj.backtrack_values(simulation_rew, visit_stack, pnum)


if __name__ == "__main__":
    # TEST VALUES
    simulator_obj = tictactoesimulator.TicTacToeSimulatorClass(num_players=2)
    stateobj = tictactoestate.TicTacToeStateClass()
    stateobj.current_state["state_val"] = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    simulator_obj.change_simulator_state(stateobj)
    agent_one = randomagent.RandomAgentClass(simulator=simulator_obj)

    # ACTUAL CODE
    mgr = StartManager()
    tree_space = mgr.TreeSpace()
    tree_space.initialize_space(simulator_obj.current_state,
                                simulator_obj.get_valid_actions(), "UCB",
                                agent_one, 10, 5)
    process_q = []
    count = 0
    for proc in xrange(20):
        worker_process = Process (target=worker_code, args=(proc, tree_space, simulator_obj))
        process_q.append(worker_process)
        worker_process.daemon = True
        worker_process.start()
        c = psutil.Process(worker_process.pid)
        #time.sleep(0.1)
        count += 1

    for elem in process_q:
        elem.join()

    # CALCULATE BEST ARM HERE
    a = tree_space.get_node_object(0)
    print "\nCHILDREN LIST", len(a.children_list)
    print "ROOT STATE COUNT", a.state_visit

    for x in range(len(a.children_list)):
        print "\nNODE STATE", a.children_list[x].state_value.get_current_state()
        temp = a.children_list[x]
        print "CHILDREN LENGTH", len(temp.children_list)
        for y in range(len(temp.children_list)):
            print "MY CHILD", temp.children_list[y].state_value.get_current_state()
            print "MY CHILD's CHILD COUNT", len(temp.children_list[y].children_list)

        print a.children_list[x].reward
        print "VISITS :", a.children_list[x].state_visit
