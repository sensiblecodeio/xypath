import xypath
import xypath.xyzzy
from collections import OrderedDict

table = [[' ','Q','A','A','B','B'],
         ['K','W','a','b','a','b'],
         ['X','x','5','6','7','8'],
         ['X','y','2','9','0','1']]

xy = xypath.Table.from_iterable(table)
dimensions_horizontal = [0,1]
dimensions_vertical = [1]


def header(table, dimension, **kwargs):
    index, is_row = dimension
    if is_row:
        function, direction = (lambda cell: cell.y == index, xypath.DOWN)
    else:
        function, direction = (lambda cell: cell.x == index, xypath.RIGHT)

    header = xypath.xyzzy.group(table.filter(function), **kwargs)
    return {k: header[k].fill(direction) for k in header}


def magic(table, rows, columns):
    lookup = [(row_index, True) for row_index in rows] +\
             [(column_index, False) for column_index in columns]

    description = [headers(table, x) for x in lookup]
    description_dict = {'%s' % i: x for i, x in enumerate(description)}
    return xypath.xyzzy.xyzzy(table, description)

for thing in magic(xy, dimensions_horizontal, dimensions_vertical):
    print thing



# lookup = {'caps': (lambda cell: cell.y == 0, xypath.DOWN),
#           'lower': (lambda cell: cell.y == 1, xypath.DOWN),
#           'late': (lambda cell: cell.x == 1, xypath.RIGHT)}
#
# description = {x: xypath.xyzzy.headers(xy, lookup[x][0], lookup[x][1]) for x in lookup}
#
#
# for x in xypath.xyzzy.xyzzy(xy, description):
#     print x
