from __future__ import absolute_import
#!/usr/bin/env python
import sys
sys.path.append('xypath')
import xypath
import tcore
import unittest

class Test_Bag(tcore.TCore):
    def test_bag_from_list(self):
        "That Bag.from_list works and table is preserved"
        true_bag = self.table.filter(lambda b: b.value > "F")
        fake_bag = list(true_bag.table)
        self.assertEqual(type(fake_bag), list)
        remade_bag = xypath.Bag.from_list(fake_bag)
        self.assertEqual(true_bag.table, remade_bag.table)
        self.assertEqual(type(remade_bag), xypath.Bag)
        self.assertEqual(len(remade_bag), len(self.table))

    def test_bag_equality(self):
        lhs = self.table.filter("WORLD")
        rhs = self.table.filter("WORLD")

        self.assertEqual(lhs, rhs)

        rhs = self.table.filter("Variant")

        self.assertNotEqual(lhs, rhs)

    def test_bag_locations(self):
        world=self.table.filter("WORLD")
        empty=self.table.filter(lambda cell: False)

        self.assertEqual(world.excel_locations(), "C18")
        self.assertEqual(empty.excel_locations(), "")
        self.assertIn(", ...", self.table.excel_locations())

    def test_bags_from_different_tables_are_not_equal(self):
        bag1 = self.table.filter(lambda b: True)
        bag2 = xypath.Table.from_bag(bag1)
        self.assertNotEqual(bag1, bag2)

    def test_corebag_iterator_size(self):
        """Test that the iterator yields as many results as len() claims"""
        bag = self.table.filter('Estimates')
        self.assertEqual(265, len(bag))
        self.assertEqual(len(bag), len(list(bag)))

    def test_corebag_iterator_nonduplicate(self):
        """
        Ensure that each call of CoreBag.__iter__ returns a new iterator

        Supercedes _test_corebag_iterator_size_squared
        """

        bag = self.table.filter('Estimates')
        assert iter(bag) is not iter(bag)

    def _test_corebag_iterator_size_squared(self):
        """Worry: that iterating twice over bag doesn't work property.
        Test: that every pair of cells from the bags is present."""
        bag = self.table.filter('Estimates')

        SIZE = 4
        # Limit bag size so that test isn't slow
        bag = bag.from_list([cell for cell in bag][:SIZE])

        n_bag = len(bag)
        assert n_bag == SIZE

        count = 0
        for i in bag:
            for j in bag:
                count = count + 1

        self.assertEqual(count, n_bag * n_bag)

    def test_corebag_iterator_returns_bags(self):
        """Check the iterator returns bags, not _XYCells"""
        bag = self.table.filter('Estimates')
        for individual_cell in bag:
            self.assertIsInstance(individual_cell, xypath.Bag)

    def test_singleton_bag_value(self):
        self.assertEqual(
            "Country code",
            self.table.filter("Country code").value)
        self.assertRaises(xypath.XYPathError,
                          lambda: self.table.filter("Estimates").value)

    def test_messytables_has_properties(self):
        for bag in self.table.unordered:
            bag.properties.get("jam")  # is vaguely dict-like

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

    def test_fill_down_without_termination(self):
        world_cell = self.table.filter('WORLD').assert_one()
        filled_down = world_cell.fill(xypath.DOWN)
        assert world_cell not in filled_down
        self.assertEqual(264, len(filled_down))

    def test_expand_down_without_termination(self):
        world_cell = self.table.filter('WORLD').assert_one()
        expand_down = world_cell.expand(xypath.DOWN)
        assert world_cell in expand_down
        self.assertEqual(265, len(expand_down))

    def test_fill_right_without_termination(self):
        world_cell = self.table.filter('WORLD').assert_one()
        filled_right = world_cell.fill(xypath.RIGHT)
        assert world_cell not in filled_right
        self.assertEqual(14, len(filled_right))

    def test_bag_intersection(self):
        bag = self.table.filter('Estimates')
        another_bag = self.table.filter("WORLD")
        union = bag | another_bag
        intersection = union & another_bag
        assert intersection.value == "WORLD"

    def test_bag_union(self):
        bag = self.table.filter('Estimates')
        another_bag = self.table.filter("WORLD")

        union = bag | another_bag
        self.assertEqual(len(bag) + len(another_bag), len(union))

    def test_bag_set_difference(self):
        super_bag = self.table.filter("WORLD").assert_one().fill(xypath.DOWN)
        sub_bag = self.table.filter("AFRICA").assert_one()

        diff = super_bag - sub_bag

        self.assertEqual(len(super_bag) - len(sub_bag), len(diff))

    def test_bag_set_difference_rhs_non_subset_of_lhs(self):
        super_bag = self.table.filter("WORLD").assert_one().fill(xypath.DOWN)
        unrelated_bag = self.table.filter("Estimates")

        diff = super_bag - unrelated_bag

        self.assertEqual(len(super_bag), len(diff))
        self.assertEqual(super_bag, diff)

    def test_bag_empty_is_ok(self):
        badbag = self.table.filter("BODGERANDBADGER").fill(xypath.RIGHT)

    def test_bag_ordering(self):


        # The purpose of this test is to have a "reasonably pathological" bag
        # so that the sort test is meaningful

        col1 = self.table.filter("Index").fill(xypath.DOWN)
        col2 = self.table.filter("Variant").fill(xypath.DOWN)

        bag = col1 | col2

        self.assertEqual([1.0, "Estimates", 2.0, "Estimates"],
                         [cell.value for cell in list(bag)[:4]])

        def yx(cell):
            return (cell.y, cell.x)

        self.assertEqual(sorted(bag, key=yx), list(bag))

    def test_assert_one_with_zero(self):
        bag = self.table.filter('No Such Cell')
        self.assertRaises(AssertionError, lambda: bag.assert_one())
        self.assertRaises(
            xypath.NoCellsAssertionError, lambda: bag.assert_one())

    def test_assert_one_with_multiple(self):
        bag = self.table.filter('Estimates')
        self.assertRaises(AssertionError, lambda: bag.assert_one())
        self.assertRaises(
            xypath.MultipleCellsAssertionError, lambda: bag.assert_one())

    def test_table_rows(self):
        counter = 0
        rows = list(self.table.rows())
        for row in rows:
            counter = counter + len(row)
        self.assertEqual(len(self.table), counter)  # misses none
        self.assertEqual(len(rows), 282)

    def test_table_cols(self):
        counter = 0
        cols = list(self.table.cols())
        for col in cols:
            counter = counter + len(col)
        self.assertEqual(len(self.table), counter)  # misses none
        self.assertEqual(len(cols), 17)

    def test_has_table(self):
        self.assertEqual(xypath.Table, type(self.table))
        self.assertIsInstance(self.table, xypath.Bag)

    def test_select_other(self):
        raise self.skipTest("select_other not tested")

    def test_getattr(self):
        assert self.table.filter("WORLD").is_bold()
        assert not self.table.filter("WORLD").is_not_bold()
        assert self.table.filter("WORLD").font_name_is("Arial")
        assert not self.table.filter("WORLD").font_name_is_not("Arial")
        assert self.table.filter("WORLD").font_name_is_not("Comic Sans MS")

