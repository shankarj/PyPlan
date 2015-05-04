import multiprocessing
from multiprocessing import Process, Manager
import time

def worker_code(something, mgr):
    time.sleep(20)

if __name__ == "__main__":
    pq = []
    mgr = Manager()
    for x in xrange(10):
        worker = Process(target=worker_code, args=(x, mgr))
        pq.append(worker)
        worker.start()
        print worker.pid

    mgr.shutdown()
    for proc in pq:
        proc.join()

    while 1:
        continue