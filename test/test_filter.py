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


class Test_Filter(tcore.TCore):
    #filter
    def test_basic_vert(self):
        r = repr(self.table.filter(lambda b: b.x == 2))
        self.assertIn("WORLD", r)
        self.assertNotIn("Country code", r)

    #filter
    def test_basic_horz(self):
        r = repr(self.table.filter(lambda b: b.y == 16))
        self.assertNotIn("WORLD", r)
        self.assertIn("Country code", r)

    #filter
    def test_text_match_string(self):
        self.table.filter("Country code").assert_one()

    #filter
    def test_text_exact_match_lambda(self):
        self.table.filter(lambda b: b.value == 'Country code').assert_one()

    #filter
    def test_text_exact_match_hamcrest(self):
        self.table.filter(hamcrest.equal_to("Country code")).assert_one()

    #filter
    def test_regex_match(self):
        self.assertEqual(
            2, len(self.table.filter(re.compile(r'.... developed regions$'))))

    #filter
    def test_regex_not_search(self):
        """
        Expect it to use match() not search(), so shouldn't match inside the
        middle of a cell.
        """

        self.assertEqual(
            0, len(self.table.filter(re.compile(r'developed regions$'))))

    #filter
    def test_select(self):
        a = self.table.filter("WORLD")
        b = a.select(lambda t, b: t.y == b.y + 1 and t.x == b.x).value
        self.assertIn("More developed regions", b)

    #filter
    def test_fill(self):
        a = self.table.filter("Variant")
        b = a.fill(xypath.LEFT).value
        self.assertEqual("Index", b)

    #filter
    def test_shift(self):
        a = self.table.filter('Ethiopia')
        b = a.shift(-2, 2)  # down, left
        c = a.shift((-2, 2))  # as a tuple

        self.assertEqual(1, len(a))
        self.assertEqual(1, len(b))
        self.assertEqual(16.0, b.value)
        self.assertEqual(16.0, c.value)

    #junction
    def test_cell_junction(self):
        a = self.table.filter("WORLD").assert_one()
        b = self.table.filter("1990-1995").assert_one()
        junction_result = list(a.junction(b))
        self.assertEqual(1, len(junction_result))
        (x, y, z) = junction_result[0]
        self.assertIsInstance(x, xypath.Bag)
        self.assertIsInstance(y, xypath.Bag)
        self.assertIsInstance(z, xypath.Bag)
        self.assertEqual("WORLD", x.value)
        self.assertEqual("1990-1995", y.value)
        self.assertEqual(1.523, z.value)

    #junction
    def test_bag_junction_overlap_dir(self):
        a = self.table.filter("WORLD")
        b = self.table.filter("1990-1995")
        topleft = "Major area, region, country or area"
        cases = {xypath.RIGHT: 1.523,
                xypath.LEFT: topleft,
                xypath.DOWN: 1.523,
                xypath.UP: topleft}
        for i in cases:
            jcell = a.junction_overlap(b, i)
            self.assertEqual(cases[i], jcell.value)

    #junction
    def test_bag_junction(self):
        a = self.table.filter("WORLD")
        b = self.table.filter("1990-1995")
        j = list(a.junction(b))
        self.assertEqual(1, len(j))
        (a_result, b_result, value_result) = j[0]
        self.assertEqual(1.523, value_result.value)

    #junction
    def test_bag_junction_overlap(self):
        a = self.table.filter("WORLD")
        b = self.table.filter("1990-1995")
        j = a.junction_overlap(b).value
        self.assertEqual(1.523, j)

    #junction
    def test_bag_junction_checks_type(self):
        bag = self.table.filter('Estimates')
        self.assertRaises(TypeError, lambda: list(bag.junction('wrong_type')))
