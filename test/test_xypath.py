import sys
import unittest
from nose.tools import *
sys.path.append('xypath')
import xypath
import messytables
import hamcrest


class Test_XYPath(unittest.TestCase):
    @classmethod
    def setup_class(klass):
        messy = messytables.excel.XLSTableSet(open("fixtures/wpp.xls", "rb"))
        klass.table = xypath.Table.from_messy(messy.tables[0])

    def setUp(self):
        pass

    def test_has_table(self):
        self.assertEqual(xypath.Table, type(self.table))
        self.assertIsInstance(self.table, xypath.Bag)

    def test_basic_vert(self):
        r = repr(self.table.filter(lambda b: b.x == 2))
        self.assertIn("WORLD", r)
        self.assertNotIn("Country code", r)

    def test_basic_horz(self):
        r = repr(self.table.filter(lambda b: b.y == 16))
        self.assertNotIn("WORLD", r)
        self.assertIn("Country code", r)

    def test_text_match_string(self):
        self.table.filter("Country code").assert_one()

    def test_text_exact_match_lambda(self):
        self.table.filter(lambda b: b.value == 'Country code').assert_one()

    def test_text_exact_match_hamcrest(self):
        self.table.filter(hamcrest.equal_to("Country code")).assert_one()

    def test_cell_junction(self):
        a = self.table.filter("WORLD").get_one()
        b = self.table.filter("1990-1995").get_one()
        c = a.junction(b).get_one()
        self.assertEqual(1.523, c.value)

    def test_bag_junction(self):
        a = self.table.filter("WORLD")
        b = self.table.filter("1990-1995")
        j = list(a.junction(b))
        self.assertEqual(1, len(j))
        self.assertEqual(1.523, j[0][2].value)

    def test_select(self):
        a = self.table.filter("WORLD")
        b = a.select(lambda t, b: t.y == b.y + 1 and t.x == b.x).get_one()
        self.assertIn("More developed regions", b.value)

    def test_extend(self):
        a = self.table.filter("Variant")
        b = a.extend(-1, 0).get_one()
        self.assertEqual("Index", b.value)

    def test_shift(self):
        a = self.table.filter('Ethiopia')
        b = a.shift(-2, 2)  # down, left
        
        self.assertEqual(1, len(a))
        self.assertEqual(1, len(b))
        self.assertEqual(16.0, b[0].value)

    def test_from_bag(self):
        world_pops_bag = self.table.filter(lambda b: b.y >= 16 and b.y <= 22 and b.x >= 5 and b.x <= 16)
        world_pops_table = xypath.Table.from_bag(world_pops_bag) 

        # check extending the whole table gets lots of stuff all the way down
        fifties = self.table.filter("1950-1955")
        filties_col = fifties.extend(0, 1)
        self.assertEqual(265, len(filties_col))

        # check if we extend within the new world-only table, it only gets stuff from the table
        fifties = world_pops_table.filter("1950-1955")
        filties_col = fifties.extend(0, 1)
        self.assertEqual(6, len(filties_col))



