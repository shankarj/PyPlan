import multiprocessing
from multiprocessing import Process, Lock, Manager, Event
import time

class uctnode:
    def __init__(self, val):
        self.locked = False
        self.testval = val

    def lock_me(self):
        if self.locked == True:
            pass

def worker_code(currnode, process_name, loc):
    printed = False
    with loc:
        while currnode.root.locked:
            if printed == False:
                printed = True
                print "PROCESS", process_name, "WAITING."

    print currnode.root
    temp = currnode.root
    temp.locked = True
    currnode.root = temp

    print "STARTING PROCESS", process_name
    temp = currnode.root
    temp.testval += 1
    currnode.root = temp
    time.sleep(1)
    print "ENDING PROCESS", process_name

    temp = currnode.root
    temp.locked = False
    currnode.root = temp

if __name__ == "__main__":
    temp_mgr = Manager()
    work_space = temp_mgr.Namespace()
    temp_root = uctnode(0)
    work_space.root = temp_root

    plock = Lock()
    process_q = []
    for proc in xrange(5):
        print "PROCESS KICK"
        worker_process = Process (target=worker_code, args=(work_space, str(proc), plock))
        process_q.append(worker_process)
        worker_process.daemon = True
        worker_process.start()

    for elem in process_q:
        elem.join()

    print work_space.root.testval