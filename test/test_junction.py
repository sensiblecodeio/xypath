#!/usr/bin/env python
import sys
sys.path.append('xypath')
import xypath
import tcore


class TestJunctionMissing(tcore.TMissing):
    def test_cell_missing(self):
        a = self.table.filter("2").assert_one()
        b = self.table.filter("4").assert_one()
        junction_result = list(a.junction(b))
        self.assertEqual(len(junction_result), 0)


class TestJunction(tcore.TCore):
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

    def test_bag_junction(self):
        a = self.table.filter("WORLD")
        b = self.table.filter("1990-1995")
        j = list(a.junction(b))
        self.assertEqual(1, len(j))
        (a_result, b_result, value_result) = j[0]
        self.assertEqual(1.523, value_result.value)

    def test_bag_junction_overlap(self):
        a = self.table.filter("WORLD")
        b = self.table.filter("1990-1995")
        j = a.junction_overlap(b).value
        self.assertEqual(1.523, j)

    def test_bag_junction_checks_type(self):
        bag = self.table.filter('Estimates')
        self.assertRaises(TypeError, lambda: list(bag.junction('wrong_type')))

    def test_junction_raises(self):
        a = self.table.filter('WORLD')
        b = self.table.filter('AFRICA')  # is below WORLD
        self.assertRaises(xypath.JunctionError, lambda: list(a.junction(b)))
