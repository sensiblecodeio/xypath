#!/usr/bin/env python
import sys
sys.path.append('xypath')
import xypath
try:
    import hamcrest
except:
    pass

import tcore
import collections


class Test_Xyzzy(tcore.TXyzzy):
    def test_xyzzy(self):
        "That it works and table is preserved"

        def fun(s, d):
            return self.table.filter(hamcrest.starts_with(s)).fill(d)

        a = {'a1': fun('a1', xypath.DOWN),
             'a2': fun('a2', xypath.DOWN)}

        b = {'b1': fun('b1', xypath.DOWN),
             'b2': fun('b2', xypath.DOWN)}

        c = {'c1': fun('c1', xypath.RIGHT),
             'c2': fun('c2', xypath.RIGHT)}

        d = {'d1': fun('d1', xypath.RIGHT),
             'd2': fun('d2', xypath.RIGHT)}

        f = {'ucase': self.table.filter("lower").fill(xypath.UP_RIGHT),
             'lcase': self.table.filter("lower").fill(xypath.DOWN_RIGHT)}

        od = collections.OrderedDict([['A', a], ['B', b],
                                      ['C', c], ['D', d], ['F', f]])
        l = list(self.table.xyzzy(od))

        lookfor = collections.OrderedDict([('A', 'a1'), ('B', 'b1'),
                                           ('C', 'c1'), ('D', 'd2'),
                                           ('F', 'lcase'), ('_value', u'e')])
        assert lookfor in l
