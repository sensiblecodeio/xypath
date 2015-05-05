from __future__ import absolute_import
import xypath
import xypath.xyzzy
from collections import OrderedDict

table = [[' ', 'Q', 'A', 'A', 'B', 'B'],
         ['K', 'W', 'a', 'b', 'a', 'b'],
         ['X', 'x', '5', '6', '7', '8'],
         ['X', 'y', '2', '9', '0', '1']]

output = [['A', 'a', 'x', '5'],
          ['A', 'a', 'y', '2'],
          ['A', 'b', 'x', '6'],
          ['A', 'b', 'y', '9'],
          ['B', 'a', 'x', '7'],
          ['B', 'a', 'y', '0'],
          ['B', 'b', 'x', '8'],
          ['B', 'b', 'y', '1']]


xy = xypath.Table.from_iterable(table)
dimensions_horizontal = [0, 1]
dimensions_vertical = [1]


def get_value_bags_for_dimension(table, header_index_and_direction, **kwargs):
    index, is_row = header_index_and_direction
    if is_row:
        function, direction = (lambda cell: cell.y == index, xypath.DOWN)
    else:
        function, direction = (lambda cell: cell.x == index, xypath.RIGHT)

    header = xypath.xyzzy.group(table.filter(function), **kwargs)
    return {k: header[k].fill(direction) for k in header}


def xtract_by_numbers(table, rows, columns):
    rows_and_columns = [(row_index, True) for row_index in rows] +\
                       [(column_index, False) for column_index in columns]
    bags_by_dimension = [get_value_bags_for_dimension(table, x) for x in rows_and_columns]

    def name_dim(index, dimension):
        return ('dimension_%s' % (index + 1), dimension)
    bags_for_xyzzy = OrderedDict(name_dim(i, x) for i, x in enumerate(bags_by_dimension))
    return xypath.xyzzy.xyzzy(table, bags_for_xyzzy, 'value')


def test_xyzzy_kinda_works():
    things = xtract_by_numbers(xy, dimensions_horizontal, dimensions_vertical)
    sorted_things = [list(thing.values()) for thing in sorted(things)]
    assert sorted_things == output
