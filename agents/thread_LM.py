from abstract import absagent
import math
import sys
import timeit
import threading
import time

class uctnode:
    def __init__(self, node_state, action_list, is_root, is_terminal, lock_obj):
        self.node_id = 0
        self.state_value = node_state
        self.valid_actions = action_list
        self.is_root = is_root
        self.state_visit = 0
        self.children_list = []
        self.reward = []
        self.is_terminal = is_terminal
        self.lock_obj = lock_obj

root_node = None
total_sims = 0
start_time = None

# PARALLEL CODE. THIS IS THE CODE THAT RUNS ON INDIVIDUAL PROCESS'S SPACE.
def worker_code(pnum, sim_obj, tree_policy, rollout_policy, uct_constant, sim_count, horizon, time_limit, start_time):
    sim_c = 0

    while sim_c < sim_count:
        sim_c += 1
        if time_limit != -1.0:
            end_time = timeit.default_timer()
            if end_time - start_time > time_limit:
                break

        global root_node
        current_node = root_node
        current_node.lock_obj.acquire()
        current_node.state_visit += 1
        visit_stack = [current_node]

        #print "SELECTING"
        try:
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
                next_node = current_node.children_list[sel_node]
                current_node.lock_obj.release()
                current_node = next_node
                current_node.state_visit += 1
                current_node.lock_obj.acquire()
                visit_stack.append(current_node)


            simulation_rew = [0.0] * sim_obj.numplayers
            actual_reward = [0.0] * sim_obj.numplayers

            #print "CHECKING IF TERMINAL"
            if current_node.is_terminal:
                current_node.lock_obj.release()
                simulation_rew = current_node.reward
            else:
                #print "CREATING"
                sim_obj.change_simulator_state(current_node.state_value)
                current_pull = sim_obj.create_copy()
                actual_reward = current_pull.take_action(current_node.valid_actions[len(current_node.children_list)])
                current_pull.change_turn()

                # NODE EXPANSION. ADD NEW NODE TO VISIT STACK.
                global uctnode
                temp_node = uctnode(current_pull.get_simulator_state(), current_pull.get_valid_actions(),
                                    False, current_pull.gameover, threading.Lock())
                temp_node.state_visit = 1
                temp_node.reward = [0.0] * sim_obj.numplayers
                current_node.children_list.append(temp_node)
                current_node.lock_obj.release()
                visit_stack.append(temp_node)

                # START SIMULATION. LOCK IS RELEASED IN PREVIOUS STEP.
                # SO THIS SIMULATION RUNS IN PARALLEL TO OTHER STEPS.
                temp_pull = current_pull.create_copy()
                simulation_rew = [0.0] * temp_pull.numplayers
                h = 0

                #print "SIMULATING"
                while temp_pull.gameover == False and h <= horizon:
                    try:
                        action_to_take = rollout_policy.select_action(temp_pull.current_state)
                        current_pull_reward = temp_pull.take_action(action_to_take)
                        simulation_rew = [x + y for x, y in zip(simulation_rew, current_pull_reward)]
                        temp_pull.change_turn()
                        h += 1
                    except Exception:
                        break

                del temp_pull

            q_vals = [x+y for x,y in zip(actual_reward, simulation_rew)]

            # LOCK AND BACKPROPAGATE.
            root_node.lock_obj.acquire()

            for node in xrange(len(visit_stack) - 1, -1, -1):
                if visit_stack[node].is_root == False:
                    temp_diff =  [x - y for x, y in zip(q_vals, visit_stack[node].reward)]
                    temp_qterm =  [float(x) / float(visit_stack[node].state_visit) for x in temp_diff]
                    visit_stack[node].reward = [x + y for x, y in zip(visit_stack[node].reward, temp_qterm)]

            root_node.lock_obj.release()
        except Exception:
            print "GOT"

            try:
                current_node.lock_obj.release()
            except Exception:
                pass

            continue

    global  total_sims
    total_sims += sim_c

class ThreadTPLMClass(absagent.AbstractAgent):
    myname = "UCT-TP-LM-THREAD"

    def __init__(self, simulator, rollout_policy, tree_policy, num_simulations, threadcount, uct_constant, horizon, time_limit=-1):
        self.agentname = self.myname
        self.rollout_policy = rollout_policy
        self.simulator = simulator.create_copy()
        self.tree_policy = tree_policy
        self.uct_constant = uct_constant
        self.horizon = horizon
        self.thread_count = threadcount
        self.time_limit = time_limit
        self.simulation_count = num_simulations

    def create_copy(self):
        return ThreadTPLMClass(self.simulator.create_copy(), self.rollout_policy.create_copy(),
                                       self.tree_policy, self.simulation_count, self.thread_count,
                                       self.uct_constant, self.horizon, self.time_limit)

    def get_agent_name(self):
        return self.agentname

    def select_action(self, current_state):
        current_turn = current_state.get_current_state()["current_player"]
        self.simulator.change_simulator_state(current_state)
        valid_actions = self.simulator.get_valid_actions()
        actions_count = len(valid_actions)

        if actions_count <= 1:
            return valid_actions[0]

        process_q = []
        count = 0

        if self.time_limit != -1:
            self.simulation_count = 30000000000000

        global root_node
        root_node = uctnode(current_state, valid_actions,
                            True, self.simulator.gameover, threading.Lock())
        global  total_sims
        total_sims = 0

        global start_time
        start_time = timeit.default_timer()

        for proc in xrange(self.thread_count):
            worker_process = threading.Thread(target=worker_code, args=(proc, self.simulator, self.tree_policy,
                                                                self.rollout_policy, self.uct_constant,
                                                                self.simulation_count, self.horizon, self.time_limit,
                                                                start_time))
            process_q.append(worker_process)
            #worker_process.daemon = True
            worker_process.start()
            count += 1

        for elem in process_q:
            elem.join()

        best_arm = 0
        best_reward = root_node.children_list[0].reward[current_turn - 1]

        global  total_sims
        print "LM", total_sims
        #print "------------TREE VISIT", tree_space.get_node_object(0).state_visit

        for arm in xrange(len(root_node.children_list)):
            #print "CHILD VISIT", tree_space.get_node_object(0).children_list[arm].state_visit
            if root_node.children_list[arm].reward[current_turn - 1] > best_reward:
                best_reward = root_node.children_list[arm].reward[current_turn - 1]
                best_arm = arm

        return valid_actions[best_arm]


