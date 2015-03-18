import multiprocessing as mp
from multiprocessing import Lock
import timeit


def subtract(num, ids, full_arr, lk):
    for x in xrange(num):
        continue

    lk.acquire()
    full_arr.append(ids)
    print "HERE " + str(ids)
    lk.release()

    return x

overall = []
cpu_cores = mp.cpu_count()
pool = mp.Pool(processes = cpu_cores)

start_time = timeit.default_timer()
result = []
manager = mp.Manager()
my_lock = manager.Lock()

for a in xrange(10):
    print "PUSHING " + str(a)
    result.append(pool.apply_async(subtract,(10, a, overall, my_lock,)))

pool.close()
pool.join()

end_time = timeit.default_timer()

print "TOTAL TIME : " + str(end_time - start_time)

print overall