#!/usr/bin/env python
import sys
sys.path.append('xypath')
import xypath
import tcore


class TestFill(tcore.TCore):

    def test_fill_down_without_termination(self):
        world_cell = self.table.filter('WORLD').assert_one()
        filled_down = world_cell.fill(xypath.DOWN)
        assert world_cell not in filled_down
        self.assertEqual(264, len(filled_down))

    def test_fill_right_without_termination(self):
        world_cell = self.table.filter('WORLD').assert_one()
        filled_right = world_cell.fill(xypath.RIGHT)
        assert world_cell not in filled_right
        self.assertEqual(14, len(filled_right))

    def test_fill_down_with_termination(self):
        world_cell = self.table.filter('WORLD').assert_one()
        stop_cell = self.table.filter('Sub-Saharan Africa').assert_one()

        filled_down = world_cell.fill(
            xypath.DOWN,
            stop_before=lambda cell: cell == stop_cell)
        assert world_cell not in filled_down
        assert stop_cell not in filled_down  # function should be exclusive
        self.assertEqual(5, len(filled_down))

    def test_fill_right_with_termination(self):
        index_cell = self.table.filter('Index').assert_one()
        stop_cell = self.table.filter('Notes').assert_one()

        filled_down = index_cell.fill(
            xypath.RIGHT,
            stop_before=lambda cell: cell == stop_cell)
        assert index_cell not in filled_down
        assert stop_cell not in filled_down  # function should be exclusive
        self.assertEqual(2, len(filled_down))
