import multi
from nose.tools import assert_equal
fn = "fixtures/4132.zip"

tables = multi._table_set(fn)

four, = multi.get_sheets(tables, 0)
assert four.value == 'four', four

one, three = multi.get_sheets(tables, [1, 2])
assert one.value == 'one' and three.value == 'three', (one, three)

all_sheets = multi.get_sheets(tables, 'table')
assert len(list(all_sheets)) == 4

two, = multi.get_sheets(tables, lambda sheet: sheet.filter("two"))
assert two.value == 'two'
