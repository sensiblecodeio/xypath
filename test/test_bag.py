#!/usr/bin/env python
import sys
import unittest
sys.path.append('xypath')
import xypath
import messytables
try:
    import hamcrest
except:
    pass
import re
import tcore


class Test_Bag(tcore.TCore):
    #bag
    def test_bag_from_list(self):
        "That it works and table is preserved"
        true_bag = self.table.filter(lambda b: b.value > "F")
        fake_bag = list(true_bag.table)
        self.assertEqual(type(fake_bag), list)
        remade_bag = xypath.Bag.from_list(fake_bag)
        self.assertEqual(true_bag.table, remade_bag.table)
        self.assertEqual(type(remade_bag), xypath.Bag)
        self.assertEqual(len(remade_bag), len(self.table))

    #bag
    def test_bag_equality(self):
        bag1 = self.table.filter(lambda b: True)
        bag2 = self.table.filter(lambda b: True)
        self.assertEqual(bag1, bag2)
        bag3 = xypath.Table.from_bag(bag2)
        self.assertNotEqual(bag1, bag3)

    #bag
    def test_corebag_iterator_size(self):
        """Test that the iterator yields as many results as len() claims"""
        bag = self.table.filter('Estimates')
        self.assertEqual(265, len(bag))
        self.assertEqual(len(bag), len(list(bag)))

    #bag
    def test_corebag_iterator_size_squared(self):
        """Worry: that iterating twice over bag doesn't work property.
        Test: that every pair of cells from the bags is present."""
        bag = self.table.filter('Estimates')
        count = 0
        for i in bag:
            for j in bag:
                count = count + 1
        self.assertEqual(count, 265*265)

    #bag
    def test_corebag_iterator_returns_bags(self):
        """Check the iterator returns bags, not _XYCells"""
        bag = self.table.filter('Estimates')
        for individual_cell in bag:
            self.assertIsInstance(individual_cell, xypath.Bag)

    #bag
    def test_singleton_bag_value(self):
        self.assertEqual(
            "Country code",
            self.table.filter("Country code").value)
        self.assertRaises(ValueError,
                          lambda: self.table.filter("Estimates").value)

    #bag
    def test_messytables_has_properties(self):
        for bag in self.table:
            self.assertIsInstance(bag.properties, dict)

    #bag
    def test_from_bag(self):
        world_pops_bag = self.table.filter(lambda b: b.y >= 16 and
                                                     b.y <= 22 and
                                                     b.x >= 5 and
                                                     b.x <= 16)
        world_pops_table = xypath.Table.from_bag(world_pops_bag)

        # check extending the whole table gets lots of stuff all the way down
        fifties = self.table.filter("1950-1955")
        filties_col = fifties.fill(xypath.DOWN)
        self.assertEqual(265, len(filties_col))

        # check if we extend within the new world-only table, it only gets
        # stuff from the table
        fifties = world_pops_table.filter("1950-1955")
        filties_col = fifties.fill(xypath.DOWN)
        self.assertEqual(6, len(filties_col))

    #bag
    def test_assert_one_with_zero(self):
        bag = self.table.filter('No Such Cell')
        self.assertRaises(AssertionError, lambda: bag.assert_one())
        self.assertRaises(
            xypath.NoCellsAssertionError, lambda: bag.assert_one())

    #bag
    def test_assert_one_with_multiple(self):
        bag = self.table.filter('Estimates')
        self.assertRaises(AssertionError, lambda: bag.assert_one())
        self.assertRaises(
            xypath.MultipleCellsAssertionError, lambda: bag.assert_one())

    #table
    def test_table_rows(self):
        counter = 0
        rows = list(self.table.rows())
        for row in rows:
            counter = counter + len(row)
        self.assertEqual(len(self.table), counter)  # misses none
        self.assertEqual(len(rows), 282)

    #table
    def test_table_cols(self):
        counter = 0
        cols = list(self.table.cols())
        for col in cols:
            counter = counter + len(col)
        self.assertEqual(len(self.table), counter)  # misses none
        self.assertEqual(len(cols), 17)

    #table
    def test_has_table(self):
        self.assertEqual(xypath.Table, type(self.table))
        self.assertIsInstance(self.table, xypath.Bag)
