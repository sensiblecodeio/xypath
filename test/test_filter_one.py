#!/usr/bin/env python
import sys

import unittest
sys.path.append('xypath')
import xypath

import tcore


class TestFilterOne(tcore.TCore):

    def test_filter_one_returns_a_single_cell(self):
        bag = self.table.filter_one('Variant')
        self.assertEquals(len(bag), 1)

    def test_filter_one_raises_error_if_no_cells_match(self):
        self.assertRaises(
            xypath.NoCellsAssertionError,
            self.table.filter_one,
            'I DO NOT EXIST'
        )

    def test_filter_one_raises_error_if_more_than_one_cell_matches(self):
        self.assertRaises(
            xypath.MultipleCellsAssertionError,
            self.table.filter_one,
            'Estimates'
        )
