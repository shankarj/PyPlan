import multiprocessing
from multiprocessing import Process, Lock, Value, Manager
import time
from multiprocessing.managers import BaseManager

class something:
    def __init__(self, val):
        self.a = val

def f(mlist, i, pl):
    a = [1,2,3]
    with pl:
        A = something(i)
        mlist.append(A)
        if i == 3:
            temp = mlist[2]
            temp.a = i + 7
            mlist[2] = temp

if __name__ == '__main__':
    lock = Lock()
    p_q = []
    mgr = Manager()
    mgrsome = mgr.list()

    for num in range(10):
        p = Process(target=f, args=(mgrsome,num, lock))
        p_q.append(p)
        p.start()

    for proc in p_q:
        proc.join()

    for elem in xrange(len(mgrsome)):
        print mgrsome[elem].a