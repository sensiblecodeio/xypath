""" musings on order of variables, x/y vs. col/row
Everyone agrees that col 2, row 1 is (2,1) which is xy ordered.
This works well with the name.
Remember that the usual iterators (over a list-of-lists)
is outer loop y first."""

from collections import defaultdict
import hamcrest
import re


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

    def junction(self, other):
        """ gets the lower-right intersection of the row of one, and the
        column of the other. """
        x = max(self.x, other.x)
        y = max(self.y, other.y)
        if (x, y) == (self.x, self.y) or (x, y) == (other.x, other.y):
            print self, other, x, y
            assert False
        junction_bag = self.table.filter(
            lambda cell: cell.x == x and cell.y == y)

        self_bag = Bag(self.table)
        self_bag.add(self)
        other_bag = Bag(self.table)
        other_bag.add(other)
        yield (self_bag, other_bag, junction_bag)


class CoreBag(object):
    """A collection of XYCells"""
    def __init__(self, table, name=None):
        self.store = []
        self.name = name
        self.table = table

    def add(self, value):
        self.store.append(value)

    def __len__(self):
        return len(self.store)

    def __repr__(self):
        return repr(self.store)

    def __iter__(self):
        return self.store.__iter__()


    def select(self, function):
        """returns a new bag (using the same table) which
        is a transformation of the bag. It can potentially
        have any cells from the table in it.

        function takes parameters (table_cell, bag_cell) and
        returns true if the table_cell should be in the new
        bag and false otherwise"""

        newbag = Bag(table=self.table)
        for table_cell in self.table.store:
            for bag_cell in self.store:
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
        elif isinstance(filter_by, re._pattern_type):
            return self._filter_internal(
                lambda cell: re.match(filter_by, unicode(cell.value)))
        else:
            raise ValueError("filter_by must be a callable or a hamcrest filter")

    def _filter_internal(self, function):
        newbag = Bag(table=self.table)
        for bag_cell in self.store:
            if function(bag_cell):
                newbag.add(bag_cell)
        return newbag

    def assert_one(self):
        assert len(self.store) == 1, "Length is %d" % len(self.store)
        return self

    def get_one(self):
        for cell in self.assert_one().store:
            return cell


class Bag(CoreBag):

    def extend(self, x=0, y=0):
        return self.select(
            lambda t, b: cmp(t.x, b.x) == x and cmp(t.y, b.y) == y
        )

    def junction(self, other):
        for self_cell in self.store:
            for other_cell in other.store:
                for triple in self_cell.junction(other_cell):
                    yield triple

    def shift(self, x=0, y=0):
        """
        Return a bag in which each cell is offset from the source bag by the
        coordinates specified.
        """
        return self.select(
            lambda tc, bc: tc.x == bc.x + x and tc.y == bc.y + y
        )

    @property
    def value(self):
        try:
            self.assert_one()
        except AssertionError:
            raise ValueError("Bag contains %d cells, can't get value" %
                             len(self.store))
        return self.get_one().value


class Table(Bag):
    """A bag which represents an entire sheet"""
    def __init__(self):
        super(Table, self).__init__(table=self, name="")
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
        for cell in bag.store:
            new_table.add(XYCell(cell.value, cell.x, cell.y, new_table))
        return new_table


