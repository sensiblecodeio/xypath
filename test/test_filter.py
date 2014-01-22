#!/usr/bin/env python
import sys

import unittest
sys.path.append('xypath')
import xypath
import messytables
try:
    import hamcrest
except ImportError:
    hamcrest = None
import re
import tcore


class TestFilter(tcore.TCore):
    def test_bag_function(self):
        self.table.filter("Country code").filter(lambda b: b.shift(x=0, y=0).value=="Country code").assert_one()
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
        if hamcrest is None:
            raise unittest.SkipTest("Requires Hamcrest")
        self.table.filter(hamcrest.equal_to("Country code")).assert_one()

    def test_regex_match(self):
        self.assertEqual(
            2, len(self.table.filter(re.compile(r'.... developed regions$'))))

    def test_regex_not_search(self):
        """
        Expect Table.filter to use match() not search(), so shouldn't match inside the
        middle of a cell.
        """

        self.assertEqual(
            0, len(self.table.filter(re.compile(r'developed regions$'))))

    def test_select(self):
        a = self.table.filter("WORLD")
        b = a.select(lambda t, b: t.y == b.y + 1 and t.x == b.x).value
        self.assertIn("More developed regions", b)

    def test_fill(self):
        a = self.table.filter("Variant")
        b = a.fill(xypath.LEFT).value
        self.assertEqual("Index", b)

    def test_shift(self):
        a = self.table.filter('Ethiopia')
        b = a.shift(-2, 2)  # down, left
        c = a.shift((-2, 2))  # as a tuple

        self.assertEqual(1, len(a))
        self.assertEqual(1, len(b))
        self.assertEqual(16.0, b.value)
        self.assertEqual(16.0, c.value)
