import xypath
import time

timing_instructions = [lambda bag: bag.table.get_at(0, 0).fill(xypath.DOWN),
                       None,
                       lambda bag: bag.fill(xypath.DOWN),
                       lambda bag: bag.table.get_at(0, 0).fill(xypath.RIGHT),
                       None,
                       lambda bag: bag.fill(xypath.RIGHT),
                       ]


def long_table(n):
    import random
    big_table = []
    big_table.append(list(chr(n) for n in range(65, 85)))
    for i in xrange(0, n):
        big_table.append(list((random.random(),) * 20))
    return xypath.Table.from_iterable(big_table)


def ravel_time(n):
    bigtable = long_table(n)
    t = time.clock()
    print len(list(xypath.ravel(bigtable, timing_instructions)))
    elapsed = time.clock()-t
    print n, elapsed, elapsed/n


for i in range(6, 11):
    ravel_time(2**i)
