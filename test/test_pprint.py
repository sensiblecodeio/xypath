import tcore
import xypath
from textwrap import dedent
from cStringIO import StringIO


class TestPPrint(tcore.TCore):

    def test_pprint(self):
        """
        test_pprint: basic check of pprint output against hard-coded string
        """

        EXPECTED_TABLE = dedent('''
              /  C
            ---  -------------------------
            274  American Samoa
            275  Cook Islands
            276  French Polynesia
            277  Niue
            278  Samoa
            279  Tokelau
            280  Tonga
            281  Tuvalu
            282  Wallis and Futuna Islands
            ''').lstrip('\n')

        cells = self.table.filter('Polynesia').fill(xypath.DOWN)
        stream = StringIO()
        cells.pprint(stream=stream)
        self.assertEqual(EXPECTED_TABLE, stream.getvalue())
        
    def test_pprint_removed_cell(self):
        """
        test_pprint_removed_cell: check that pprint's output is rectangular
        """

        EXPECTED_TABLE = dedent('''
              /  C
            ---  -------------------------
            274  American Samoa
            275  Cook Islands
            276  French Polynesia
            277  Niue
            278  Samoa
            279  Tokelau
            280  /
            281  Tuvalu
            282  Wallis and Futuna Islands
            ''').lstrip('\n')

        cells = self.table.filter('Polynesia').fill(xypath.DOWN)
        cells_without_tonga = cells - cells.filter('Tonga')

        stream = StringIO()
        cells_without_tonga.pprint(stream=stream)
        self.assertEqual(EXPECTED_TABLE, stream.getvalue())
                
    def test_pprint_removed_cell_collapsed(self):
        """
        test_pprint_removed_cell_collapsed: check that a collapsed row works
        """

        EXPECTED_TABLE = dedent('''
              /  C
            ---  -------------------------
            274  American Samoa
            275  Cook Islands
            276  French Polynesia
            277  Niue
            278  Samoa
            279  Tokelau
            281  Tuvalu
            282  Wallis and Futuna Islands
            ''').lstrip('\n')

        cells = self.table.filter('Polynesia').fill(xypath.DOWN)
        cells_without_tonga = cells - cells.filter('Tonga')
        stream = StringIO()
        cells_without_tonga.pprint(collapse_empty=True, stream=stream)
        self.assertEqual(EXPECTED_TABLE, stream.getvalue())
        
    def test_extrude(self):
        """
        test_extrude: check 2-to-the-left extrusion against hard-coded string
        """

        EXPECTED_TABLE = dedent('''
            /  C                          D      E
          ---  -------------------------  ---  ---
          274  American Samoa                   16
          275  Cook Islands                    184
          276  French Polynesia                258
          277  Niue                            570
          278  Samoa                           882
          279  Tokelau                         772
          280  Tonga                           776
          281  Tuvalu                          798
          282  Wallis and Futuna Islands       876
          ''').lstrip('\n')

        # Below the word "Polynesia", there are a set of islands
        cells = self.table.filter('Polynesia').fill(xypath.DOWN)
        # Right of this column, there is an empty column followed by numbers.
        cells = cells.extrude(2, 0)

        stream = StringIO()
        cells.pprint(stream=stream)

        self.assertEqual(EXPECTED_TABLE, stream.getvalue())

    def test_pprint_collapsed_column(self):
        """
        test_pprint_collapsed_column: check empty column removal
        """

        # Column D is removed because it contains no itmes with bool(x) == True

        EXPECTED_TABLE = dedent('''
              /  C                            E
            ---  -------------------------  ---
            274  American Samoa              16
            275  Cook Islands               184
            276  French Polynesia           258
            277  Niue                       570
            278  Samoa                      882
            279  Tokelau                    772
            280  Tonga                      776
            281  Tuvalu                     798
            282  Wallis and Futuna Islands  876
            ''').lstrip('\n')

        # Below the word "Polynesia", there are a set of islands
        cells = self.table.filter('Polynesia').assert_one().fill(xypath.DOWN)
        # Right of this column, there is an empty column followed by numbers.
        cells = cells.extrude(2, 0)

        stream = StringIO()
        # Collapse empty removes the empty column
        cells.pprint(collapse_empty=True, stream=stream)
        self.assertEqual(EXPECTED_TABLE, stream.getvalue())


    def test_pprint_collapsed_column_and_row(self):
        """
        test_pprint_collapsed_column_and_row: check row/column removal
        """

        # Column D is removed because it contains no itmes with bool(x) == True

        EXPECTED_TABLE = dedent('''
              /  C                            E
            ---  -------------------------  ---
            274  American Samoa              16
            275  Cook Islands               184
            276  French Polynesia           258
            277  Niue                       570
            278  Samoa                      882
            279  Tokelau                    772
            281  Tuvalu                     798
            282  Wallis and Futuna Islands  876
            ''').lstrip('\n')

        # Below the word "Polynesia", there are a set of islands
        cells = self.table.filter('Polynesia').assert_one().fill(xypath.DOWN)
        # Right of this column, there is an empty column followed by numbers.
        cells = cells.extrude(2, 0)

        tonga = cells.filter("Tonga")
        # Remove cells in the same row as tonga
        cells -= cells.same_row(tonga)

        stream = StringIO()
        # Collapse empty removes the empty column
        cells.pprint(collapse_empty=True, stream=stream)
        self.assertEqual(EXPECTED_TABLE, stream.getvalue())
