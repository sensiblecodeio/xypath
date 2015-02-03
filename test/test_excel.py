import unittest
from nose.tools import assert_raises, assert_equal
import xypath.contrib.excel as exceltool

class Test_Loader(unittest.TestCase):
    def test_excel_address(self):
        assert_equal(exceltool.excel_address_coordinate("A1"), (0, 0))
        assert_equal(exceltool.excel_address_coordinate("IV1"), (255, 0))
        # assert_equal(exceltool.excel_address_coordinate("CHRDW1001"), (2**20-1, 1000))

    def test_invalid_excel_address(self):
        assert_raises(exceltool.InvalidExcelReference, exceltool.excel_address_coordinate, "CAT")


