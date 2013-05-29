import sys
from nose.tools import *
sys.path.append('xypath')
import xypath
import messytables
import re
import xy


class Test_XYPath(object):
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
        r = repr(self.table.match(lambda b: b.x == 2))
        assert "WORLD" in r
        assert "Country code" not in r

    def test_basic_horz(self):
        r = repr(self.table.match(lambda b: b.y == 16))
        assert "WORLD" not in r
        assert "Country code" in r

    def test_text_search(self):
        def textsearch(s):
            return lambda b: re.search(s, unicode(b))
        self.table.match(textsearch("Country.code")).assertone()

    def test_junction(self):
        a = self.table.match(xy.textsearch("WORLD")).getit()
        b = self.table.match(xy.textsearch("1990-1995")).getit()
        c = a.junction(b).getit()
        assert c.value == 1.523

    def test_select(self):
        a = self.table.match(xy.textsearch("WORLD"))
        b = a.select(lambda t, b: t.y == b.y + 1 and t.x == b.x).getit()
        assert "More developed regions" in b.value
