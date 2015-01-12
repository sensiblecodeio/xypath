#!/usr/bin/env python
import unittest
import xypath.contrib.excel

class Test_Contrib(unittest.TestCase):
    def test_excel_nums(self):
        num = xypath.contrib.excel.excel_column_number
        let = xypath.contrib.excel.excel_column_label
        cases = [
        ['A', 1],
        ['Z', 26],
        ['AA', 27],
        ['AZ', 52],
        ['BA', 53],
        ['AAA', 703],
        ]
        for case in cases:
            assert num(case[0]) == case[1], num(case[0])
            assert let(case[1]) == case[0]
            assert num(case[0], index=0) == case[1] - 1
