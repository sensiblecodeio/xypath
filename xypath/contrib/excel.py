import sys
from itertools import product
from ..extern.tabulate import tabulate
import xypath
import re

class InvalidExcelReference(Exception):
    pass

def excel_address_coordinate(address, partial=False):
    """Given a cell reference, return a tuple suitable for inserting into Table.get_at()"""
    match = re.match("([A-Za-z]*)([0-9]*)$", address)
    if not match:
        raise InvalidExcelReference(address)
    col_name, row_num = match.groups()
    if col_name:
        col = excel_column_number(col_name, index=0)
    else:
        col = None
    if row_num:
        row = int(row_num) - 1
    else:
        row = None
    if row is None and col is None:
        raise InvalidExcelReference(address)
    if (row is None or col is None) and not partial:
        raise InvalidExcelReference("{!r} is partial".format(address))
    return (col, row)


def excel_column_number(raw_column_name, index=1):
     """Given a column name, give me the column number
     A=1
     Z=26
     AA=27
     AZ=52
     BA=53 etc"""

     def char_value(c):
         return ord(c)-64

     value = 0
     for char in raw_column_name.upper():
         value = value * 26
         value = value + char_value(char)
     return value - 1 + index

def excel_column_label(n):

    """
    Excel's column counting convention, counting from A at n=1
    """
    def inner(n):
        if n <= 0:
            return []
        if not n:
            return [0]
        div, mod = divmod(n - 1, 26)
        return inner(div) + [mod]
    return "".join(chr(ord("A") + i) for i in inner(n))


def excel_locations(bag, limit=3):
    """describe the locations of cells in a bag
       in Excel notation"""
    def _excel_location(cell):
        excelcol = excel_column_label(cell.x + 1)
        assert excelcol
        return "{}{}".format(excelcol,
                             cell.y)
    builder = []
    for i, singleton in enumerate(bag.unordered):
        if i >= limit:
            builder.append("...")
            break
        builder.append(_excel_location(singleton))
    return ', '.join(builder)


def filter_one(self, filter_by):
    errormsg = "We expected to find one cell {}, but we found {}."
    foundmsg = 'one'
    filtered = self.filter(filter_by)
    filter_length = len(filtered)

    if filter_length == 0:
        foundmsg = 'none'
    elif filter_length > 1:
        foundmsg = "{}: {}".format(
            filter_length,
            filtered.excel_locations(filtered)
        )

    return filtered.assert_one(
        errormsg.format(
            xypath.describe_filter_method(filter_by),
            foundmsg
        )
    )


def as_list(self, collapse_empty=False, excel_labels=False):
    """
    Generate a rectangular 2D list representing the bag, where the contents
    are the values of the cells, or None if there is no cell present at a
    particular location.

    collapse_empty: Remove empty rows and columns for a more compact
        representation

    excel_labels: Put "excel-like" row/column labels around the table
    """
    cells = list(self)
    cxs = [cell.x for cell in cells]
    cys = [cell.y for cell in cells]
    xmin, xmax = min(cxs), max(cxs)
    ymin, ymax = min(cys), max(cys)

    width, height = xmax-xmin+1, ymax-ymin+1

    result = [[None]*width for i in xrange(height)]

    for x, y in product(xrange(xmin, xmax+1), xrange(ymin, ymax+1)):
        cell = self.table.get_at(x, y)
        result[y-ymin][x-xmin] = cell.value if cell in self else None

    # Indices of the rows/columns that are present, starting at (1, 1)
    row_indices = list(range(ymin+1, ymax+1+1))
    col_indices = list(range(xmin+1, xmax+1+1))

    if collapse_empty:
        # Note the dreaded "delete from thing you're iterating over"
        # pattern here. Hence `reversed`.

        # Remove empty rows
        for j, y in reversed(list(enumerate(result))):
            if not any(y):
                del result[j]
                del row_indices[j]

        search_indices = list(range(width))
        # Find empty columns
        for y in result:
            for i, s_index in reversed(list(enumerate(search_indices))):
                if y[s_index]:
                    # We've found a thing. Don't need to search it anymore.
                    del search_indices[i]
        # A search_index making it here, is empty, delete it from all rows
        for y in result:
            for i in reversed(search_indices):
                del y[i]

        # Fix the set of column indices which remain
        for i in reversed(search_indices):
            del col_indices[i]

    if excel_labels:
        # Add row numbers to each row
        for j, row in zip(row_indices, result):
            row[0:0] = [j]

        # Add column labels to the headers
        header = [None] + [excel_column_label(i) for i in col_indices]
        result[0:0] = [header]

    return result


def pprint(self, collapse_empty=False,
           excel_labels=True, stream=sys.stdout):
    result = self.as_list(collapse_empty, excel_labels)

    for row in result:
        for i, cell in enumerate(row):
            if cell is None:
                cell = "/"
            cell = str(cell)
            row[i] = cell

    if excel_labels:
        print >>stream, tabulate(result[1:], headers=result[0])
    else:
        print >>stream, tabulate(result)
