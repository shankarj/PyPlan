import multiprocessing
from multiprocessing import Process, Lock, Manager, Event
import time
from states import *
from actions import *

class uctnode:
    def __init__(self, myname, node_state, action_list, is_root, locked):
        self.myname = myname
        self.state_value = node_state
        self.valid_actions = action_list
        self.is_root = is_root
        self.state_visit = 0
        self.children_list = []
        self.reward = []
        self.is_terminal = False
        self.lockobj = locked
        self.val = 0
        self.checkarr = []

def worker_code(node_namespace, process_number, mgr):
    printed = False
    curr_space = node_namespace.treespace
    curr_node = curr_space[0]
    child_created = 0

    while child_created <=2:
        print "\n", process_number, "W", curr_node.myname
        with curr_node.lockobj:
            print "\n", process_number, "S", curr_node.myname
            curr_node.val += 1
            if curr_node.myname == "CH1":
                print "yo", process_number
                print curr_node.checkarr
                curr_node.checkarr.append(process_number)
            c_node = uctnode("CH"+str(child_created + 1), current_state, "ACTION_LIST", True, mgr.Lock())
            child_created += 1
            curr_node.children_list.append(c_node)
            node_namespace.treespace = curr_space
            if process_number == '0':
                time.sleep(5)
            else:
                time.sleep(0.5)
            print "\n", process_number, "E", curr_node.myname
            curr_node = curr_node.children_list[0]

if __name__ == "__main__":
    current_state = connect4state.Connect4StateClass(2)
    temp_mgr = Manager()
    node_space = Manager().Namespace()
    root_node = uctnode("RT", current_state, "ACTION_LIST", True, temp_mgr.Lock())
    node_space.treespace = [root_node]

    process_q = []
    for proc in xrange(2):
        worker_process = Process (target=worker_code, args=(node_space, str(proc), temp_mgr)) #, "CURRENT_SIM", "CURRENT_STATE",
                                                            #"TREE_POL", "ROLLOUT_POL", "UCT_CONST", "HORIZON","OUTP_Q"))
        process_q.append(worker_process)
        worker_process.daemon = True
        worker_process.start()
        time.sleep(0.1)

    for elem in process_q:
        elem.join()

    print node_space.treespace[0].children_list[0].checkarr