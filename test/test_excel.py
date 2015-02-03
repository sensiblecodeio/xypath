import unittest
from nose.tools import assert_raises, assert_equal
import xypath.contrib.excel as exceltool

class Test_Loader(unittest.TestCase):
    def test_excel_address(self):
        assert_equal(exceltool.excel_address_coordinate("A1"), (0, 0))
        assert_equal(exceltool.excel_address_coordinate("IV1"), (255, 0))
        assert_equal(exceltool.excel_address_coordinate("BGQCV1001"), (2**20-1, 1000))

    def test_invalid_excel_address(self):
        assert_raises(exceltool.InvalidExcelReference, exceltool.excel_address_coordinate, "CAT")

    def test_excel_col(self):
        assert_equal(exceltool.excel_column_number("A"), 1)
        assert_equal(exceltool.excel_column_number("Z"), 26)
        assert_equal(exceltool.excel_column_number("Z")+1, exceltool.excel_column_number("AA"))
        assert_equal(exceltool.excel_column_number("AZ")+1, exceltool.excel_column_number("BA"))
        assert_equal(exceltool.excel_column_number("ZZ")+1, exceltool.excel_column_number("AAA"))
        assert_equal(exceltool.excel_column_number("CAZ")+1, exceltool.excel_column_number("CBA"))

    def test_col_label(self):
        assert_equal(exceltool.excel_column_label(1), "A")
        assert_equal(exceltool.excel_column_label(256), "IV")
        assert_equal(exceltool.excel_column_label(2**20), "BGQCV")
