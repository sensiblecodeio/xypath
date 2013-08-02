import xypath
import messytables
import hamcrest
import collections

mt, = messytables.any.any_tableset(open('../fixtures/xyzzy.tsv'), extension='tsv').tables
xy = xypath.Table.from_messy(mt)

def f(s, d):
    return xy.filter(hamcrest.starts_with(s)).fill(d)


a = {'a1': f('a1', xypath.DOWN),
     'a2': f('a2', xypath.DOWN)}

b = {'b1': f('b1', xypath.DOWN),
     'b2': f('b2', xypath.DOWN)}

c = {'c1': f('c1', xypath.RIGHT),
     'c2': f('c2', xypath.RIGHT)}

d = {'d1': f('d1', xypath.RIGHT),
     'd2': f('d2', xypath.RIGHT)}

f = {'ucase': xy.filter("lower").fill(xypath.UP_RIGHT),
     'lcase': xy.filter("lower").fill(xypath.DOWN_RIGHT)}

od = collections.OrderedDict([['A',a],['B',b],['C',c],['D',d],['F',f]])
print list(xy.xyzzy(od))
       
