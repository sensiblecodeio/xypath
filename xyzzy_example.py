import xypath
import xypath.xyzzy
table = [[' ',' ','A','A','B','B'],
         [' ',' ','a','b','a','b'],
         ['X','x','5','6','7','8'],
         ['X','y','2','9','0','1']]

xy = xypath.Table.from_iterable(table)

description={'caps': {'A': xy.filter('A').fill(xypath.DOWN),
                      'B': xy.filter('B').fill(xypath.DOWN),
                     },
             'lower': {'a': xy.filter('a').fill(xypath.DOWN),
                       'b': xy.filter('b').fill(xypath.DOWN),
                      },
             'late': {'x': xy.filter('x').fill(xypath.RIGHT),
                      'y': xy.filter('y').fill(xypath.RIGHT),
                     },
            }

for x in xypath.xyzzy.xyzzy(xy, description):
    print x
