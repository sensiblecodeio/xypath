import unittest
import xypath.loader
from nose.tools import assert_equal

class Test_Loader(unittest.TestCase):
    def test_foo(self):
        fn = "fixtures/4132.zip"
        tables = xypath.loader.table_set(fn)

        four, = xypath.loader.get_sheets(tables, 0)
        assert four.value == 'four', four

        one, three = xypath.loader.get_sheets(tables, [1, 2])
        assert one.value == 'one' and three.value == 'three', (one, three)

        all_sheets = xypath.loader.get_sheets(tables, 'table')
        assert len(list(all_sheets)) == 4

        all_sheets = xypath.loader.get_sheets(tables, '*')
        assert len(list(all_sheets)) == 4

        two, = xypath.loader.get_sheets(tables, lambda sheet: sheet.filter("two"))
        assert two.value == 'two'
