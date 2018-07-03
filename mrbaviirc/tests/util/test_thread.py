""" Tests for mrbaviirc.util.thread """

from __future__ import absolute_import

__author__      = "Brian AllenVanderburg II"
__copyright__   = "Copyright 2018"
__license__     = "Apache License 2.0"

import threading
import random

from ...util import thread


# threadattr

# Basically, we create a list of numbers in each thread and append the result
# to the thread-local list, then store a copy of each list in the main
# accumulator.  Then for the test, we make sure each list was stored correctly
# to cofirm each thread was accessing it's own copy of the list

class ThreadAttrAccumulator(object):
    def __init__(self):
        self.lock = threading.RLock()
        self.results = {}

    

class ThreadAttrCalculator(threading.Thread):

    data = thread.threadattr(None)

    def __init__(self, accum):
        threading.Thread.__init__(self)
        self.accum = accum

    def run(self):
        count = random.randint(3000, 10000)
        self.data = [count]
        for i in range(count):
            self.data.append(i + count)

        with self.accum.lock:
            self.accum.results[threading.current_thread()] = list(self.data)


def test_thread_attr():
    accum = ThreadAttrAccumulator()
    threads = [ThreadAttrCalculator(accum) for i in range(20)]
    for i in threads:
        i.start()
    for i in threads:
        i.join()

    assert(len(accum.results) == 20)
    for i in threads:
        count = accum.results[i][0]
        for j in range(count):
            assert(accum.results[i][j + 1] == j + count)


            
        


