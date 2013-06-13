#!/usr/bin/env python
import sys
import unittest
sys.path.append('xypath')
import xypath
import messytables
import hamcrest
import re
from os.path import dirname, abspath, join, splitext


def get_extension(filename):
    """
    >>> get_extension('/foo/bar/test.xls')
    'xls'
    """
    return splitext(filename)[1].strip('.')


class Test_XYPath(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.wpp_filename = join(
            abspath(dirname(__file__)), '..', 'fixtures', 'wpp.xls')
        cls.messy = messytables.excel.XLSTableSet(open(cls.wpp_filename, "rb"))
        cls.table = xypath.Table.from_messy(cls.messy.tables[0])

    def setUp(self):
        pass

    def test_has_table(self):
        self.assertEqual(xypath.Table, type(self.table))
        self.assertIsInstance(self.table, xypath.Bag)

    def test_from_filename_with_table_name(self):
        """Can we specify only the filename and 'name' of the table?"""
        table = xypath.Table.from_filename(
            self.wpp_filename,
            table_name='NOTES')
        self.assertEqual(32, len(table))
        table.filter(
            hamcrest.contains_string('(2) Including Zanzibar.')).assert_one()

    def test_from_filename_with_table_index(self):
        """Can we specify only the filename and index of the table?"""
        new_table = xypath.Table.from_filename(
                self.wpp_filename,
                table_index=5)
        self.assertEqual(1, len(new_table.filter('(2) Including Zanzibar.')))

    def test_from_file_object_table_index(self):
        with open(self.wpp_filename, 'rb') as f:
            extension = get_extension(self.wpp_filename)
            new_table = xypath.Table.from_file_object(
                f, extension, table_index=5)
        self.assertEqual(1, len(new_table.filter('(2) Including Zanzibar.')))

    def test_from_file_object_table_name(self):
        with open(self.wpp_filename, 'rb') as f:
            extension = get_extension(self.wpp_filename)
            new_table = xypath.Table.from_file_object(
                f, extension, table_name='NOTES')
        self.assertEqual(1, len(new_table.filter('(2) Including Zanzibar.')))

    def test_from_file_object_no_table_specifier(self):

        with open(self.wpp_filename, 'rb') as f:
            extension = get_extension(self.wpp_filename)
            self.assertRaises(
                TypeError,
                lambda: xypath.Table.from_file_object(f, extension))

    def test_from_file_object_ambiguous_table_specifier(self):
        with open(self.wpp_filename, 'rb') as f:
            extension = get_extension(self.wpp_filename)

            self.assertRaises(
                TypeError,
                lambda: xypath.Table.from_file_object(
                    f, extension, table_name='NOTES', table_index=4))

    def test_from_messy(self):
        new_table = xypath.Table.from_messy(self.messy.tables[0])
        self.assertEqual(265, len(new_table.filter('Estimates')))

    def test_basic_vert(self):
        r = repr(self.table.filter(lambda b: b.x == 2))
        self.assertIn("WORLD", r)
        self.assertNotIn("Country code", r)

    def test_basic_horz(self):
        r = repr(self.table.filter(lambda b: b.y == 16))
        self.assertNotIn("WORLD", r)
        self.assertIn("Country code", r)

    def test_corebag_iterator_size(self):
        """Test that the iterator yields as many results as len() claims"""
        bag = self.table.filter('Estimates')
        self.assertEqual(265, len(bag))
        self.assertEqual(len(bag), len(list(bag)))

    def test_singleton_bag_value(self):
        self.assertEqual(
            "Country code",
            self.table.filter("Country code").value)
        self.assertRaises(ValueError,
            lambda: self.table.filter("Estimates").value)

    def test_text_match_string(self):
        self.table.filter("Country code").assert_one()

    def test_text_exact_match_lambda(self):
        self.table.filter(lambda b: b.value == 'Country code').assert_one()

    def test_text_exact_match_hamcrest(self):
        self.table.filter(hamcrest.equal_to("Country code")).assert_one()

    def test_regex_match(self):
        self.assertEqual(
            2, len(self.table.filter(re.compile(r'.... developed regions$'))))

    def test_regex_not_search(self):
        """
        Expect it to use match() not search(), so shouldn't match inside the
        middle of a cell.
        """

        self.assertEqual(
            0, len(self.table.filter(re.compile(r'developed regions$'))))

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

    def test_bag_junction(self):
        a = self.table.filter("WORLD")
        b = self.table.filter("1990-1995")
        j = list(a.junction(b))
        self.assertEqual(1, len(j))
        (a_result, b_result, value_result) = j[0]
        self.assertEqual(1.523, value_result.value)

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

        self.assertEqual(1, len(a))
        self.assertEqual(1, len(b))
        self.assertEqual(16.0, b.value)

    def test_from_bag(self):
        world_pops_bag = self.table.filter(lambda b: b.y >= 16 and b.y <= 22 and b.x >= 5 and b.x <= 16)
        world_pops_table = xypath.Table.from_bag(world_pops_bag)

        # check extending the whole table gets lots of stuff all the way down
        fifties = self.table.filter("1950-1955")
        filties_col = fifties.fill(xypath.DOWN)
        self.assertEqual(265, len(filties_col))

        # check if we extend within the new world-only table, it only gets stuff from the table
        fifties = world_pops_table.filter("1950-1955")
        filties_col = fifties.fill(xypath.DOWN)
        self.assertEqual(6, len(filties_col))



