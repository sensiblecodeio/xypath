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
        assert type(self.table) == xypath.Table
        assert isinstance(self.table, xypath.Bag)

    def test_basic_vert(self):
        r = repr(self.table.filter(lambda b: b.x == 2))
        assert "WORLD" in r
        assert "Country code" not in r

    def test_basic_horz(self):
        r = repr(self.table.filter(lambda b: b.y == 16))
        assert "WORLD" not in r
        assert "Country code" in r

    def test_text_search(self):
        self.table.textsearch("Country.code").assert_one()

    def test_text_exact_match_lambda(self):
        self.table.filter(lambda b: b.value == 'Country code').assert_one()

    def test_text_exact_match_hamcrest(self):
        self.table.filter(hamcrest.equal_to("Country code")).assert_one()

    def test_junction(self):
        a = self.table.textsearch("WORLD").get_one()
        b = self.table.textsearch("1990-1995").get_one()
        c = a.junction(b).get_one()
        assert c.value == 1.523

    def test_select(self):
        a = self.table.textsearch("WORLD")
        b = a.select(lambda t, b: t.y == b.y + 1 and t.x == b.x).get_one()
        assert "More developed regions" in b.value

    def test_extend(self):
        a = self.table.textsearch("Variant")
        b = a.extend(-1, 0).get_one()
        assert b.value == "Index"

    def test_shift(self):
        a = self.table.textsearch('Ethiopia')
        b = a.shift(-2, 2)  # down, left
        
        self.assertEqual(1, len(a))
        self.assertEqual(1, len(b))
        self.assertEqual(16.0, b[0].value)
