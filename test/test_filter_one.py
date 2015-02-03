#!/usr/bin/env python
import sys

import unittest
sys.path.append('xypath')
import xypath
import re
import tcore


class TestFilterOne(tcore.TCore):

    def test_filter_one_returns_a_single_cell(self):
        bag = self.table.filter_one('Variant')
        self.assertEquals(len(bag), 1)

    def test_filter_one_raises_error_if_no_cells_match(self):
        self.assertRaisesWithMessage(
            self.table.filter_one,
            xypath.NoCellsAssertionError,
            "We expected to find one cell containing the string 'I DO NOT EXIST', but we found none.",
            'I DO NOT EXIST'
        )

    def test_filter_one_raises_error_if_more_than_one_cell_matches(self):
        try:
            self.table.filter_one(re.compile(r'.*Europe.*'))
        except xypath.MultipleCellsAssertionError as e:
            pass
        else:
            assert False, "Didn't get a MultipleCellsAssertionError"

        assert "We expected to find one cell matching the regex '.*Europe.*', but we found 4: " in str(e)
        for cell in "C157, C146, C171, C188".split(', '):
            assert cell in str(e)
