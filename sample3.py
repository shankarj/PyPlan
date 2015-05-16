import multiprocessing
from multiprocessing import Process, Manager
import time

def worker_code(pnum, lockie):
    #print pnum, "WAITING"
    with lockie:
        print pnum, "~INSIDE"
        time.sleep(5)
    print pnum, "DONE"

if __name__ == "__main__":
    my_lock = Manager().Lock()

    p_q = []
    for x in xrange(5):
        worker = Process(target=worker_code, args=(x, my_lock))
        worker.start()
        time.sleep(0.1)
        p_q.append(worker)

    for q in p_q:
        q.join()