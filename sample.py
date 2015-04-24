import multiprocessing
from multiprocessing import Process, Lock, Manager, Event
import time

class uctnode:
    def __init__(self, node_state, action_list, is_root, lock):
        self.state_value = node_state
        self.valid_actions = action_list
        self.is_root = is_root
        self.state_visit = 0
        self.children_list = []
        self.reward = []
        self.is_terminal = False
        self.lockobj = lock

def worker_code(root_node, current_simulator, current_turn, sim_count, tree_pol, rollout, uct_const, hor, out_q):
    printed = False

    print "PROCESS", process_name, "WAITING."
    with currnode.root.lockobj:
        print "STARTING PROCESS", process_name
        temp = currnode.root
        temp.testval += 1
        currnode.root = temp
        time.sleep(1)
        print "ENDING PROCESS", process_name

if __name__ == "__main__":
    temp_mgr = Manager()
    work_space = temp_mgr.Namespace()
    temp_root = uctnode(0, Manager().Lock())
    work_space.root = temp_root

    process_q = []
    for proc in xrange(5):
        worker_process = Process (target=worker_code, args=(work_space, str(proc)))
        process_q.append(worker_process)
        worker_process.daemon = True
        worker_process.start()


    for elem in process_q:
        elem.join()

    print work_space.root.testval