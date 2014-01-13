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

class Test_Import_Missing(tcore.TMissing):
    def test_table_has_properties_at_all(self):
        self.table.sheet

class Test_Import(tcore.TCore):
    def test_table_has_sheet_properties(self):
        self.assertIn('xlrd', repr(self.table.sheet))

    #import
    def test_from_filename_with_table_name(self):
        """Can we specify only the filename and 'name' of the table?"""
        if hamcrest is None:
            raise unittest.SkipTest("Requires Hamcrest")
        table = xypath.Table.from_filename(
            self.wpp_filename,
            table_name='NOTES')
        self.assertEqual(32, len(table))
        table.filter(
            hamcrest.contains_string('(2) Including Zanzibar.')).assert_one()

    #import
    def test_from_filename_with_table_index(self):
        """Can we specify only the filename and index of the table?"""
        new_table = xypath.Table.from_filename(self.wpp_filename,
                                               table_index=5)
        self.assertEqual(1, len(new_table.filter('(2) Including Zanzibar.')))

    #import
    def test_from_file_object_table_index(self):
        with open(self.wpp_filename, 'rb') as f:
            extension = tcore.get_extension(self.wpp_filename)
            new_table = xypath.Table.from_file_object(
                f, extension, table_index=5)
        self.assertEqual(1, len(new_table.filter('(2) Including Zanzibar.')))

    #import
    def test_from_file_object_table_name(self):
        with open(self.wpp_filename, 'rb') as f:
            extension = tcore.get_extension(self.wpp_filename)
            new_table = xypath.Table.from_file_object(
                f, extension, table_name='NOTES')
        self.assertEqual(1, len(new_table.filter('(2) Including Zanzibar.')))

    #import
    def test_from_file_object_no_table_specifier(self):
        with open(self.wpp_filename, 'rb') as f:
            extension = tcore.get_extension(self.wpp_filename)
            self.assertRaises(
                TypeError,
                lambda: xypath.Table.from_file_object(f, extension))

    #import
    def test_from_file_object_ambiguous_table_specifier(self):
        with open(self.wpp_filename, 'rb') as f:
            extension = tcore.get_extension(self.wpp_filename)

            self.assertRaises(
                TypeError,
                lambda: xypath.Table.from_file_object(
                    f, extension, table_name='NOTES', table_index=4))

    #import
    def test_from_messy(self):
        new_table = xypath.Table.from_messy(self.messy.tables[0])
        self.assertEqual(265, len(new_table.filter('Estimates')))
