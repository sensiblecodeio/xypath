
import xypath.xypath as xypath # no privacy

import unittest

from copy import copy

class XYCellTests(unittest.TestCase):

    def test_cell_equality(self):
        """
        test_cell_equality: required for expected set behaviour
        """
        table = xypath.Table()

        cell_a = xypath._XYCell("foo", 1, 3, table)
        also_cell_a = xypath._XYCell("foo", 1, 3, table)

        self.assertIsNot(cell_a, also_cell_a)
        self.assertEqual(cell_a, also_cell_a)

    def test_cell_identity(self):
        """
        test_cell_identity: given two cells which were instantiated separately
        but *actually* belong to the same logical cell (table, co-ordinate,
        value), ensure that their identity (as far as the 'set' type is
        concerned) is maintained.
        """

        table = xypath.Table()

        cell_a = xypath._XYCell("foo", 1, 3, table)
        also_cell_a = xypath._XYCell("foo", 1, 3, table)

        self.assertIsNot(cell_a, also_cell_a)
        self.assertEqual(hash(cell_a), hash(also_cell_a))

        self.assertEqual(1, len(set([cell_a, also_cell_a])))

    def test_cell_copy(self):
        table = xypath.Table()

        cell_a = xypath._XYCell("foo", 1, 3, table)
        not_cell_a = copy(cell_a)
        # Before mutating "not_cell_a", ensure that it is first equal
        self.assertEqual(hash(cell_a), hash(not_cell_a))


    def test_cell_identity_not_equal_different_x(self):

        table = xypath.Table()
        cell_a = xypath._XYCell("foo", 1, 3, table)
        not_cell_a = copy(cell_a)
        not_cell_a.x = 2
        self.assertNotEqual(hash(cell_a), hash(not_cell_a))
        self.assertEqual(2, len(set([cell_a, not_cell_a])))

    def test_cell_identity_not_equal_different_y(self):
        table = xypath.Table()
        cell_a = xypath._XYCell("foo", 1, 3, table)
        not_cell_a = copy(cell_a)
        not_cell_a.y = 2
        self.assertNotEqual(hash(cell_a), hash(not_cell_a))
        self.assertEqual(2, len(set([cell_a, not_cell_a])))


    def test_cell_identity_not_equal_different_tables(self):
        table = xypath.Table()
        cell_a = xypath._XYCell("foo", 1, 3, table)

        other_table = xypath.Table()
        self.assertNotEqual(hash(table), hash(other_table))

        not_cell_a = copy(cell_a)
        not_cell_a.table = other_table

        self.assertNotEqual(hash(cell_a), hash(not_cell_a))
        self.assertEqual(2, len(set([cell_a, not_cell_a])))

    def test_cell_shift_takes_tuples(self):
        table = xypath.Table()
        cell = xypath._XYCell("foo", 1, 3, table)
        table.add(cell)
        cell.shift([0,0])

