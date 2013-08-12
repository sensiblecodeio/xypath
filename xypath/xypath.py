#!/usr/bin/env python
""" musings on order of variables, x/y vs. col/row
Everyone agrees that col 2, row 1 is (2,1) which is xy ordered.
This works well with the name.
Remember that the usual iterators (over a list-of-lists)
is outer loop y first."""

import re
import messytables
import os
try:
    import hamcrest
    have_ham = True
except:
    have_ham = False

from collections import defaultdict
from copy import copy

UP = (0, -1)
RIGHT = (1, 0)
DOWN = (0, 1)
LEFT = (-1, 0)
UP_RIGHT = (1, -1)
DOWN_RIGHT = (1, 1)
UP_LEFT = (-1, -1)
DOWN_LEFT = (-1, 1)


class JunctionError(RuntimeError):
    pass


class NoCellsAssertionError(AssertionError):
    """Raised by Bag.assert_one() if the bag contains zero cells."""
    pass


class MultipleCellsAssertionError(AssertionError):
    """Raised by Bag.assert_one() if the bag contains multiple cells."""
    pass


def junction_coord(cells, direction=DOWN):
    """
    >>> cells_dr = (_XYCell(0,1,2,None), _XYCell(0,3,4,None))
    >>> junction_coord(cells_dr, DOWN)
    (1, 4)
    >>> junction_coord(cells_dr, UP)
    (3, 2)
    >>> junction_coord(cells_dr, LEFT)
    (1, 4)
    >>> junction_coord(cells_dr, RIGHT)
    (3, 2)
    >>> cells_tr = (_XYCell(0,1,4,None), _XYCell(0,3,2,None))
    >>> junction_coord(cells_tr, DOWN)
    (3, 4)
    >>> junction_coord(cells_tr, UP)
    (1, 2)
    >>> junction_coord(cells_tr, LEFT)
    (1, 2)
    >>> junction_coord(cells_tr, RIGHT)
    (3, 4)

    there are only two possible cells for the junction:
    return the one which is most UP/DOWN etc."""

    new_cells = (
                (cells[0].x, cells[1].y),
                (cells[1].x, cells[0].y)
    )
    for index, value in enumerate(direction):
        if value == 0:
            continue
        if cmp(new_cells[0][index], new_cells[1][index]) == value:
            return new_cells[0]
        else:
            return new_cells[1]


class _XYCell(object):
    """needs to contain: value, position (x,y), parent bag"""
    def __init__(self, value, x, y, table, properties=None):
        self.value = value  # of appropriate type
        self.x = x  # column number
        self.y = y  # row number
        self.table = table
        if properties is None:
            self.properties = {}
        else:
            self.properties = properties

    def __hash__(self):
        """
        An _XYCell is uniquely identified (by sets, etc) through its position,
        content, and parent table.
        """
        return hash((self.value, self.x, self.y, self.table))

    def __eq__(self, rhs):
        return hash(self) == hash(rhs)


    def copy(self, new_table=None):
        if new_table:
            return _XYCell(self.value, self.x, self.y,
                           new_table, self.properties)
        else:
            return _XYCell(self.value, self.x, self.y,
                           self.table, self.properties)

    def __repr__(self):
        return "_XYCell(%r, %r, %r, %r)" % \
            (self.value, self.x, self.y, self.table.name)

    def __unicode__(self):
        return unicode(self.value)

    def junction(self, other, direction=DOWN, paranoid=True):
        """ gets the lower-right intersection of the row of one, and the
        column of the other.

        paranoid: should we panic if we're hitting one of our input cells?"""
        (x, y) = junction_coord((self, other), direction)
        if paranoid and (x, y) == (self.x, self.y) or \
                        (x, y) == (other.x, other.y):
            raise JunctionError(
                "_XYCell.junction(_XYCell) resulted in a cell which is equal"
                " to one of the input cells.\n"
                "  self: {}\n  other: {}\n  x: {}\n  y: {}".format(
                    self, other, x, y))
        junction_bag = self.table.get_at(x, y)  # TODO: test
        if len(junction_bag) == 0:
            return
        self_bag = Bag(self.table)
        self_bag.add(self)
        other_bag = Bag(self.table)
        other_bag.add(other)
        yield (self_bag, other_bag, junction_bag)


class CoreBag(object):
    """Has a collection of _XYCells"""
    def __init__(self, table, name=None):
        self.__store = set()
        self.name = name
        self.table = table

    def add(self, cell):
        if not isinstance(cell, _XYCell):
            raise TypeError("Can only add _XYCell types to Bags: {}".format(
                            cell.__class__))
        self.__store.add(cell)

    def __eq__(self, other):
        return (self.name == other.name and
                self.table is other.table and
                self.__store == other.__store)

    def __len__(self):
        return len(self.__store)

    def __repr__(self):
        return repr(self.__store)

    @classmethod
    def singleton(cls, cell, table, name=None):
        """
        Construct a bag with one cell in it
        """
        bag = cls(table=table, name=name)
        bag.add(cell)
        return bag

    @property
    def unordered(self):
        """
        Obtain an unordered iterator over this bag. iter(bag) is sorted on
        demand, and therefore inefficient if being done repeatedly where order
        does not matter.
        """
        return (Bag.singleton(c, table=self.table) for c in self.__store)

    @property
    def unordered_cells(self):
        """
        Analogous to the `unordered` property, except that it returns _XYCells
        instead of Bags.
        """
        return iter(self.__store)

    def __iter__(self):
        """
        Return a view of the cells in this back in left-right, top-bottom order
        Note: this is expensive for large bags (when done repeatedly). If you
        don't care about order, use `bag.unordered`, which gives an unordered
        iterator.
        """
        def yx(cell):
            return cell.y, cell.x

        for cell in sorted(self.__store, key=yx):
            yield Bag.singleton(cell, table=self.table)

    def __sub__(self, rhs):
        return self.difference(rhs)

    def difference(self, rhs):
        assert self.table is rhs.table, "Can't difference bags from separate tables"
        new = copy(self)
        new.__store = self.__store.difference(rhs.__store)
        return new

    def __or__(self, rhs):
        return self.union(rhs)

    def union(self, rhs):
        assert self.table is rhs.table, "Can't union bags from separate tables"
        new = copy(self)
        new.__store = self.__store.union(rhs.__store)
        return new

    def select(self, function):
        """returns a new bag (using the same table) which
        is a transformation of the bag. It can potentially
        have any cells from the table in it.

        function takes parameters (table_cell, bag_cell) and
        returns true if the table_cell should be in the new
        bag and false otherwise"""

        newbag = Bag(table=self.table)
        for table_cell in self.table.__store:
            for bag_cell in self.__store:
                if function(table_cell, bag_cell):
                    newbag.add(table_cell)
                    break
        return newbag

    def filter(self, filter_by):
        """
        Returns a new bag containing only cells which match
        the filter_by predicate.

        filter_by can be either a) a callable, which takes a
        cell as a parameter, and returns whether or not to
        include the cell, or b) a hamcrest match rule, such
        as hamcrest.equal_to
        """
        if callable(filter_by):
            return self._filter_internal(filter_by)
        elif isinstance(filter_by, basestring):
            return self._filter_internal(lambda cell: unicode(cell.value).strip() == filter_by)
        elif have_ham and isinstance(filter_by, hamcrest.matcher.Matcher):
            return self._filter_internal(lambda cell: filter_by.matches(cell.value))
        elif isinstance(filter_by, re._pattern_type):
            return self._filter_internal(
                lambda cell: re.match(filter_by, unicode(cell.value)))
        else:
            raise ValueError("filter_by must be callable or a hamcrest filter")

    def _filter_internal(self, function):
        newbag = Bag(table=self.table)
        for bag_cell in self:
            if function(bag_cell):
                newbag.add(bag_cell._cell)
        return newbag

    def assert_one(self, message="assert_one() : {} cells in bag, not 1"):
        if len(self.__store) == 1:
            return self

        elif len(self.__store) == 0:
            raise NoCellsAssertionError(
                message.format(len(self.__store)))

        elif len(self.__store) > 1:
            raise MultipleCellsAssertionError(
                message.format(len(self.__store)))

    @property
    def _cell(self):
        try:
            xycell = list(self.assert_one().__store)[0]
        except AssertionError:
            raise ValueError("Can't get cell properties of non-singleton Bag.")
        else:
            assert isinstance(xycell, _XYCell)
            return xycell

    @property
    def value(self):
        return self._cell.value

    @property
    def x(self):
        return self._cell.x

    @property
    def y(self):
        return self._cell.y

    @property
    def properties(self):
        return self._cell.properties


class Bag(CoreBag):

    @staticmethod
    def from_list(cells, name=None):
        """
        Make a non-bag iterable of cells into a Bag. Some magic may be lost,
        especially if it's zero length.
        TODO: This should probably be part of the core __init__ class.
        TODO: Don't do a piece-by-piece insertion, just slap the whole listed
              iterable in, because this is slow.
        """ # TODO
        bag = Bag(table=None)
        for i, cell_bag in enumerate(cells):
            bag.add(cell_bag._cell)
            if i == 0:
                bag.table = cell_bag.table
            else:
                assert bag.table == cell_bag.table
        return bag

    def fill(self, direction):
        if direction not in (UP, RIGHT, DOWN, LEFT, UP_RIGHT, DOWN_RIGHT,
                             UP_LEFT, DOWN_LEFT):
            raise ValueError("Invalid direction! Use one of UP, RIGHT, "
                             "DOWN_RIGHT etc")
        (x, y) = direction
        return self.select(
            lambda t, b: cmp(t.x, b.x) == x and cmp(t.y, b.y) == y
        )

    def junction(self, other, *args, **kwargs):
        if not isinstance(other, CoreBag):
            raise TypeError(
                "Bag.junction() called with invalid type {}, must be "
                "(Core)Bag".format(other.__class__))

        # Generate ordered lists of dimension cells exactly once (avoid doing
        # it in the inner loop because of the sorted() in __iter__)
        self_cells = list(self)
        other_cells = list(other)

        for self_cell in self_cells:
            for other_cell in other_cells:

                assert self_cell._cell.__class__ == other_cell._cell.__class__

                for triple in self_cell._cell.junction(other_cell._cell, *args, **kwargs):
                    yield triple

    def junction_overlap(self, other, *args, **kwargs):
        """ returns only the overlap cell """
        bag = Bag(table=self.table)
        for triple in self.junction(other, *args, **kwargs):
            bag.add(triple[2]._cell)
        return bag

    def shift(self, x=0, y=0):
        """
        Return a bag in which each cell is offset from the source bag by the
        coordinates specified. Coordinates can be specified as:
        Bag.shift(0,2) - full specification
        Bag.shift(y=2) - partial specification
        Bag.shift((0,2)) - use of tuple for x, unspecified y
        """
        if not isinstance(x, int):
            assert y == 0, \
                "Bag.shift: x=%r not integer and y=%r specified" % (x, y)
            return self.shift(x[0], x[1])
        bag = Bag(table=self.table)
        for b_cell in self.unordered:
            t_cell = self.table.get_at(b_cell.x + x, b_cell.y + y).assert_one()
            bag.add(t_cell._cell)
        return bag


class Table(Bag):
    """A bag which represents an entire sheet"""
    def __init__(self, name=""):
        super(Table, self).__init__(table=self, name=name)
        self.x_index = defaultdict(lambda: Bag(self))
        self.y_index = defaultdict(lambda: Bag(self))
        self.xy_index = defaultdict(lambda: Bag(self))
        self._max_x = -1
        self._max_y = -1
        self.sheet = None

    def rows(self):
        for row_num in range(0, self._max_y + 1):  # inclusive
            yield self.y_index[row_num]

    def cols(self):
        for col_num in range(0, self._max_x + 1):  # inclusive
            yield self.x_index[col_num]

    def add(self, cell):
        self.x_index[cell.x].add(cell)
        self.y_index[cell.y].add(cell)
        self.xy_index[(cell.x, cell.y)].add(cell)
        self._max_x = max(self._max_x, cell.x)
        self._max_y = max(self._max_y, cell.y)
        super(Table, self).add(cell)

    def get_at(self, x=None, y=None):
        if x is None and y is None:
            raise TypeError('get_at requires at least one x or y value')
        if x is None:
            return self.y_index[y]
        if y is None:
            return self.x_index[x]
        return self.xy_index[(x, y)]

    @staticmethod
    def from_filename(filename, table_name=None, table_index=None):
        extension = os.path.splitext(filename)[1].strip('.')
        with open(filename, 'rb') as f:
            return Table.from_file_object(f, extension,
                                          table_name=table_name,
                                          table_index=table_index)

    @staticmethod
    def from_file_object(fobj, extension, table_name=None, table_index=None):
        if (table_name is not None and table_index is not None) or \
                (table_name is None and table_index is None):
            raise TypeError("Must give exactly one of table_name, table_index")

        table_set = messytables.any.any_tableset(fobj, extension=extension)

        if table_name is not None:
            return Table.from_messy(table_set[table_name])
        elif table_index is not None:
            return Table.from_messy(table_set.tables[table_index])

    @staticmethod
    def from_messy(messy_rowset):
        assert isinstance(messy_rowset, messytables.core.RowSet), "Expected a RowSet, got a %r"%type(messy_rowset)
        new_table = Table()
        if hasattr(messy_rowset, 'sheet'):
            new_table.sheet = messy_rowset.sheet
        for y, row in enumerate(messy_rowset):
            for x, cell in enumerate(row):
                new_table.add(_XYCell(cell.value, x, y,
                                      new_table, cell.properties))
        return new_table

    @staticmethod
    def from_bag(bag):
        new_table = Table()
        for bag_cell in bag.unordered:
            new_table.add(bag_cell._cell.copy(new_table))
        return new_table
