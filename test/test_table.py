#!/usr/bin/env python
import sys
sys.path.append('xypath')
import xypath
import tcore
from nose.tools import assert_raises

# Inheriting from tcore.TCore means that self.table contains an
# example table automatically, without us having to open a file
class TestTable(tcore.TCore):

    def test_get_at_gets_the_correct_cell(self):
        cells = self.table.get_at(4, 17)

        assert isinstance(cells, xypath.xypath.Bag)
        cells.assert_one() # will raise exception if more than one cell in bag
        assert cells.value == 900

    def test_get_at_returns_empty_bag_for_invalid_coordinates(self):
        index_size_before = len(self.table.xy_index)
        cells = self.table.get_at(9999,9999)
        index_size_after = len(self.table.xy_index)

        assert isinstance(cells, xypath.xypath.Bag)
        assert len(cells) == 0
        assert index_size_before == index_size_after

    def test_get_at_complains_nicely(self):
        assert_raises(AssertionError, self.table.get_at, 'kitten')
