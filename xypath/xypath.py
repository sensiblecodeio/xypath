""" musings on order of variables, x/y vs. col/row
Everyone agrees that col 2, row 1 is (2,1) which is xy ordered.
This works well with the name.
Remember that the usual iterators (over a list-of-lists)
is outer loop y first."""

from collections import defaultdict

class XYCell(object):
    """needs to contain: value, position (x,y), parent bag"""
    def __init__(self, value, x, y, table):
        self.value = value  # of appropriate type
        self.x = x  # column number
        self.y = y  # row number
        self.table = table

    def __repr__(self):
        return "XYCell(%r, %r, %r, %r)" % \
            (self.value, self.x, self.y, self.table.name)

    def __unicode__(self):
        #return "[%r (%r, %r)]" % (self.value, self.x, self.y, self.table)
        return unicode(self.value)

    def __str__(self):
        return str(self.value)

    def junction(self, other):
        """ gets the lower-right intersection of the row of one, and the
        column of the other. """
        # TODO maybe think about lookup as name
        # TODO check other is a cell
        x = max(self.x, other.x)
        y = max(self.y, other.x)
        if (x, y) == (self.x, self.y) or (x, y) == (other.x, other.y):
            print self, other, x, y
            assert False
        bag = self.table.match(lambda b: b.x == x and b.y == y).assertone()
        return bag


class CoreBag(list):
    """A collection of XYCells"""
    def add(self, value):
        self.append(value)

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

    def assertsome(self):
        assert len(self) > 0
        return self

    def assertone(self):
        # TODO cassert len(self) == 1
        return self

    def getit(self):
        for cell in self.assertone():
            return cell


class Bag(CoreBag):

    def textsearch(self, s):
        import re
        return self.match(
            lambda b: re.search(s, unicode(b))
        )

    def extend(self, x, y):
        return self.select(
            lambda t, b: cmp(t.x, b.x) == x and cmp(t.y, b.y) == y
        )

    def junction(self, other):
        for self_cell in self:
            for other_cell in other:
                yield (self_cell, other_cell,
                       self_cell.junction(other_cell).getit())


class Table(Bag):
    """A bag which represents an entire sheet"""
    def __init__(self):
        self.table = self
        self.name = ""
        self.x_index = defaultdict(lambda: Bag(self))
        self.y_index = defaultdict(lambda: Bag(self))
        self.xy_index = defaultdict(lambda: Bag(self))

    def add(self, cell):
        self.x_index[cell.x].add(cell)
        self.y_index[cell.y].add(cell)
        self.xy_index[(cell.x, cell.y)].add(cell)
        super(Table, self).add(cell)

    @staticmethod
    def from_messy(messy_rowset):
        new_table = Table()
        for y, row in enumerate(messy_rowset):
            for x, cell in enumerate(row):
                new_table.add(XYCell(cell.value, x, y, new_table))
        return new_table
