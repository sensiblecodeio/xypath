""" musings on order of variables, x/y vs. col/row
Everyone agrees that col 2, row 1 is (2,1) which is xy ordered.
This works well with the name.
Remember that the usual iterators (over a list-of-lists)
is outer loop y first."""

from collections import defaultdict
import hamcrest

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
        return unicode(self.value)

    def __str__(self):
        return str(self.value)

    def junction(self, other):
        """ gets the lower-right intersection of the row of one, and the
        column of the other. """
        x = max(self.x, other.x)
        y = max(self.y, other.y)
        if (x, y) == (self.x, self.y) or (x, y) == (other.x, other.y):
            print self, other, x, y
            assert False
        bag = self.table.xy_index[(x,y)]
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

    def filter(self, filter_by):
        """
        Returns a new bag containing only cells which match the filter_by predicate.

        filter_by can be either a) a callable, which takes a cell as a parameter, and
        returns whether or not to include the cell, or b) a hamcrest match rule, such
        as hamcrest.equal_to
        """
        if callable(filter_by):
            return self._filter_internal(filter_by)
        elif isinstance(filter_by, basestring):
            return self._filter_internal(lambda cell: unicode(cell.value) == filter_by)
        elif isinstance(filter_by, hamcrest.matcher.Matcher):
            return self._filter_internal(lambda cell: filter_by.matches(cell.value))
        else:
            raise ValueError("filter_by must be a callable or a hamcrest filter")

    def _filter_internal(self, function):
        newbag = Bag(table=self.table)
        for bag_cell in self:
            if function(bag_cell):
                newbag.add(bag_cell)
        return newbag

    def assert_one(self):
        assert len(self) == 1, "Length is %d" % len(self)
        return self

    def get_one(self):
        for cell in self.assert_one():
            return cell


class Bag(CoreBag):

    def extend(self, x, y):
        return self.select(
            lambda t, b: cmp(t.x, b.x) == x and cmp(t.y, b.y) == y
        )

    def junction(self, other):
        for self_cell in self:
            for other_cell in other:
                yield (self_cell, other_cell,
                       self_cell.junction(other_cell).get_one())

    def shift(self, x, y):
        """
        Return a bag in which each cell is offset from the source bag by the
        coordinates specified.
        """
        return self.select(
            lambda tc, bc: tc.x == bc.x + x and tc.y == bc.y + y
        )


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

    @staticmethod
    def from_bag(bag):
        new_table = Table()
        for cell in bag:
            new_table.add(XYCell(cell.value, cell.x, cell.y, new_table))
        return new_table
