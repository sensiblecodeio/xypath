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
wb = xypath.Table.from_filename('fixtures/pakdate.xls', table_index=0)


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
    sorted_things = [thing.values() for thing in sorted(things)]
    assert sorted_things == output


def test_ravel_kinda_works():
    Q = xy.filter("Q").fill(xypath.RIGHT)
    all_c = [lambda bag: bag.table.filter("K").fill(xypath.DOWN),
             lambda bag: bag.shift(xypath.RIGHT),
             None,
             lambda bag: bag.fill(xypath.RIGHT),
             lambda bag: Q,
             lambda bag: bag.shift(xypath.DOWN),
             None,
             lambda bag: bag.fill(xypath.DOWN),
             ]
    things = xypath.ravel(xy, all_c)
    print list(things)

    sorted_things = [thing.values() for thing in sorted(things)]
    for i, o in zip(sorted_things, output):
        assert (i[0][1], i[0][2], i[0][3], i[1]) == o, (i, o)


def test_ravel_worldbank():
    code = wb.filter("Indicator Code").assert_one()
    codedown = code.fill(xypath.DOWN).filter(lambda cell: cell.y < 100)
    coderight = code.fill(xypath.RIGHT).filter(lambda cell: cell.x < 20)
    # turns out the above doesn't massively increase speed
    # TODO check faster than replacing code with that string.
    all_c = [lambda bag: codedown,
             None,
             lambda bag: bag.fill(xypath.RIGHT),
             lambda bag: coderight,
             None,
             lambda bag: bag.fill(xypath.DOWN)
             ]
    things = list(xypath.ravel(wb, all_c))
    assert ([u'AG.LND.CREL.HA', u'1968'], 9536763.0) in things

