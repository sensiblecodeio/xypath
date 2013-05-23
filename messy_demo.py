import messytables
import timeit
""" musings on order of variables, x/y vs. col/row
Everyone agrees that col 2, row 1 is (2,1) which is xy ordered.
This works well with the name.
Remember that the usual iterators (over a list-of-lists)
is outer loop y first."""


class XYCell(object):
    """needs to contain: value, position (x,y), parent bag"""
    def __init__(self, value, x, y, table):
        self.value = value  # of appropriate type
        self.x = x  # column number
        self.y = y  # row number
        self.table = table

    def __repr__(self):
        return "XYCell(%r, %r, %r, %r)" % (self.value, self.x, self.y, self.table.name)

    def __unicode__(self):
        return "[%r (%r, %r)]" % (self.value, self.x, self.y, self.table)


class Bag(set):
    """A collection of XYCells"""
    def __init__(self, table, name=None):
        self.name = name
        self.table = table

    def select(self, function):
        """returns a new bag (using the same table) which
        is a transformation of the bag. It can potentially
        have any cells from the table in it.

        function takes parameters (table_cell, bag_cell) and
        returns true if the table_cell should be in the new
        bag and false otherwise"""

        #return Bag(cell for cell in self.table if function(cell, self))
        newbag = Bag(table=self.table)
        for table_cell in self.table:
            for bag_cell in self:
                if function(table_cell, bag_cell):
                    newbag.add(table_cell)
                    break
        return newbag

    def match(self, function):
        newbag = Bag(table=self.table)
        for bag_cell in self:
            if function(bag_cell):
                newbag.add(bag_cell)
        return newbag


class Table(Bag):
    """A bag which represents an entire sheet"""
    def __init__(self):
        self.table = self
        self.name = ""

    @staticmethod
    def from_messy(messy_rowset):
        new_table = Table()
        for y, row in enumerate(messy_rowset):
            for x, cell in enumerate(row):
                new_table.add(XYCell(cell.value, x, y, new_table))
        return new_table


messy = messytables.excel.XLSTableSet(open("fixtures/pakdate.xls", 'rb'))
table = Table.from_messy(messy.tables[0])

print "*"
row_two = table.match(lambda b: b.y == 2)
print row_two
print "*"
row_three = row_two.select(lambda t, b: t.y == b.y + 1)
print row_three
print "*"

#lambda should go from [set, cell -> bool] set = current set, cell = cell in table.
#any

# up: any 
