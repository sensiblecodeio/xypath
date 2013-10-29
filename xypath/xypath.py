#!/usr/bin/env python
""" musings on order of variables, x/y vs. col/row
Everyone agrees that col 2, row 1 is (2,1) which is xy ordered.
This works well with the name.
Remember that the usual iterators (over a list-of-lists)
is outer loop y first."""

import re
import messytables
import os
import sys
try:
    import hamcrest
    have_ham = True
except:
    have_ham = False

from collections import defaultdict
from copy import copy
from itertools import product, takewhile

from .extern.tabulate import tabulate

UP = (0, -1)
RIGHT = (1, 0)
DOWN = (0, 1)
LEFT = (-1, 0)
UP_RIGHT = (1, -1)
DOWN_RIGHT = (1, 1)
UP_LEFT = (-1, -1)
DOWN_LEFT = (-1, 1)


class JunctionError(RuntimeError):
    """Raised if paranoid _XYCell.junction finds it is returning one of the
       input cells - i.e. the input cells are in the same row or column"""
    pass


class NoCellsAssertionError(AssertionError):
    """Raised by Bag.assert_one() if the bag contains zero cells."""
    pass


class MultipleCellsAssertionError(AssertionError):
    """Raised by Bag.assert_one() if the bag contains multiple cells."""
    pass


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


def junction_coord(cells, direction=DOWN):
    """
    Under the hood: given two cells and a favoured direction, get the
    position of the cell with the column of one and the row of the other:

    A---->+
    |     ^
    |     |
    |     |
    v     |
    *<----B

    Both + and * are candidates for the junction of A and B - we take the
    one furthest down by default (specified by direction)

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
    """
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
    __slots__ = ['value', 'x', 'y', 'table', 'properties']
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
        In order to make a set of cells (used in Bag), they *must* be hashable.
        An _XYCell is uniquely identified (by sets, etc) through its position,
        content, and parent table.
        Note that properties is ignored (since dicts are unhashable);
        value may be redundant.
        """
        return hash((self.value, self.x, self.y, self.table))

    def __eq__(self, rhs):
        """See _XYCell.__hash__ for equality conditions"""
        return hash(self) == hash(rhs)

    def copy(self, new_table=None):
        """Make a copy of the cell.
           Its table will be new_table, if specified"""
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
        junction_bag = self.table.get_at(x, y)
        if len(junction_bag) == 0:
            return
        self_bag = Bag(self.table)
        self_bag.add(self)
        other_bag = Bag(self.table)
        other_bag.add(other)
        yield (self_bag, other_bag, junction_bag)

    def shift(self, x=0, y=0):
        """Get the cell which is offset from this cell by x columns, y rows"""
        if not isinstance(x, int):
            assert y == 0, \
                "_XYCell.shift: x=%r not integer and y=%r specified" % (x, y)
            return self.shift(x[0], x[1])
        return self.table.get_at(self.x + x, self.y + y)._cell


class CoreBag(object):
    """Has a collection of _XYCells"""
    def __init__(self, table, name=None):
        self.__store = set()
        self.name = name
        self.table = table

    def add(self, cell):
        """Add a cell to a bag"""
        if not isinstance(cell, _XYCell):
            raise TypeError("Can only add _XYCell types to Bags: {}".format(
                            cell.__class__))
        self.__store.add(cell)

    def __eq__(self, other):
        """Compare two bags:
           They are equal only if:
           * the names are the same (value)
           * their tables are the same table (object)
           * the set of cells they contain are the same"""

        if not isinstance(other, CoreBag):
            return False
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
        """Bags quack like sets. Implements - operator."""
        return self.difference(rhs)

    def difference(self, rhs):
        """Bags quack like sets"""
        assert self.table is rhs.table,\
            "Can't difference bags from separate tables"
        new = copy(self)
        new.__store = self.__store.difference(rhs.__store)
        return new

    def __or__(self, rhs):
        """Bags quack like sets. Implements | operator.
           For mathematical purity, the + (__add__) operator isn't appropriate."""
        return self.union(rhs)

    def union(self, rhs):
        """Bags quack like sets"""
        assert self.table is rhs.table, "Can't union bags from separate tables"
        new = copy(self)
        new.__store = self.__store.union(rhs.__store)
        return new

    def select(self, function):
        """Select cells from this bag's table based on
           the cells in this bag.
           e.g.
           bag.select(lambda bag_cell, table_cell: bag_cell.y == table_cell.y and
               bag_cell.value == table_cell.value)
           would give cells in the table with the same name on the same row as a
           cell in the bag"""
        return self.table.select_other(function, self)

    def select_other(self, function, other):
        """A more general version of select, where another bag to select from
           is explicitly specified rather than using the original bag's table"""
        """note: self.select(f) = self.table.select_other(f, self)"""
        newbag = Bag(table=self.table)
        for bag_cell in self.__store:
            for other_cell in other.__store:
                if function(bag_cell, other_cell):
                    newbag.add(bag_cell)
                    break
        return newbag

    def filter(self, filter_by):
        """
        Returns a new bag containing only cells which match
        the filter_by predicate.

        filter_by can be:
            a) a callable, which takes a cell as a parameter
               and returns True if the cell should be returned
               such as lambda cell: cell.value = "dog"
            b) a string, which will be matched exactly: e.g. u'dog'
            c) a hamcrest match rule, such as hamcrest.equal_to("dog")
               (requires hamcrest to be available)
            d) a compiled regular expression, such as re.compile('dog')
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
            # TODO hamcrest may not be installed which will raise this error
            raise ValueError("filter_by must be callable or a hamcrest filter")

    def _filter_internal(self, function):
        newbag = Bag(table=self.table)
        for bag_cell in self.unordered_cells:
            if function(bag_cell):
                newbag.add(bag_cell)
        return newbag

    def assert_one(self, message="assert_one() : {} cells in bag, not 1"):
        """Chainable; raise an error if the bag passed contains 0, 2 or more
           cells. Otherwise returns the original (singleton) bag unchanged."""

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
        """Under the hood: get the cell inside a singleton bag - i.e. a bag
           which contains precisely one cell."""
        try:
            xycell = list(self.assert_one().__store)[0]
        except AssertionError:
            l = len(list(self.__store))
            raise ValueError("Can't get cell properties of non-singleton Bag (length: %r)" % l)
        else:
            assert isinstance(xycell, _XYCell)
            return xycell

    @property
    def value(self):
        """getter for singleton's cell value"""
        return self._cell.value

    @property
    def x(self):
        """getter for singleton's cell column number"""
        return self._cell.x

    @property
    def y(self):
        """getter for singleton's cell row number"""
        return self._cell.y

    @property
    def properties(self):
        """getter for singleton's cell properties"""
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
        """  # TODO
        bag = Bag(table=None)
        for i, cell_bag in enumerate(cells):
            bag.add(cell_bag._cell)
            if i == 0:
                bag.table = cell_bag.table
            else:
                assert bag.table == cell_bag.table
        return bag

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
        """ Print the table nicely (to stdout, by default)"""
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

    def fill(self, direction, stop_before=None):
        """
        If the bag contains only one cell, select all cells in the direction
        given, excluding the original cell. For example, from a column heading
        cell, you can "fill down" to get all the values underneath it.

        If you provide a stop_before function, it will be called on each cell
        as a stop condition. For example, if you provide a stop_before function
        which tests cell.value for an empty string. This would stop the fill
        function before it reaches the bottom of the sheet, for example.
        """
        if direction not in (UP, RIGHT, DOWN, LEFT, UP_RIGHT, DOWN_RIGHT,
                             UP_LEFT, DOWN_LEFT):
            raise ValueError("Invalid direction! Use one of UP, RIGHT, "
                             "DOWN_RIGHT etc")

        (left_right, up_down) = direction
        bag = self.select(
            lambda table, bag: cmp(table.x, bag.x) == left_right
            and cmp(table.y, bag.y) == up_down
        )

        if stop_before is not None:
            # NOTE(PMF): stop_before is limited to singleton bags, in the DOWN
            # or RIGHT direction. This isn't ideal, but with the above "magic"
            # cmp code I can't think of an elegant general way of doing this. I
            # also can't imagine what it means to run fill in multiple
            # directions, or with non singleton bags. TODO: Constrain?

            if direction not in (DOWN, RIGHT):
                raise ValueError("Oops, stop_before only works down or right!")
            self.assert_one("You can't use stop_before for bags with more than"
                            " one cell inside.")

            return Bag.from_list(list(
                takewhile(lambda c: not stop_before(c), bag)))

        return bag

    def junction(self, other, *args, **kwargs):
        """For every combination of pairs of cells from this bag and the other bag,
           get the cell that is at the same row as one of them, and column as the other.
           There are two: so we specify a direction to say which one wins (in the
           cell-based version of this function) - defaulting to the one furthest down"""
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

                for triple in self_cell._cell.junction(other_cell._cell,
                                                       *args, **kwargs):
                    yield triple

    def junction_overlap(self, other, *args, **kwargs):
        """as junction, but returns only the overlap cell"""
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

    def extrude(self, dx, dy):
        """
        Extrude all cells in the bag by (dx, dy), by looking

        For example, given the bag with a cell at (0, 0):

            {(0, 0)}

        .extrude(2, 0) gives the bag with the cells (to the right):

            {(0, 0), (1, 0), (2, 0)}

        .extrude(0, -2) gives the bag with the cells (up):

            {(0, 0), (0, -1), (0, -2)}

        """

        if dx < 0:
            dxs = range(0, dx - 1, -1)
        else:
            dxs = range(0, dx + 1, +1)

        if dy < 0:
            dys = range(0, dy - 1, -1)
        else:
            dys = range(0, dy + 1, +1)

        bag = Bag(table=self.table)
        for cell in self.unordered_cells:
            for i, j in product(dxs, dys):
                bag.add(self.table.get_at(cell.x + i, cell.y + j)._cell)

        return bag

    def same_row(self, singleton_bag):
        """
        Select cells in this bag which are in the same
        row as `singleton_bag`
        """
        # TODO why are we not using self.table.y_index[cell.y]?
        cell = singleton_bag._cell
        this_y = cell.y
        return self.filter(lambda c: c.y == this_y)

    def same_col(self, singleton_bag):
        """
        Select cells in this bag which are in the same
        column as `singleton_bag`
        """
        # TODO why are we not using self.table.x_index[cell.x]?
        cell = singleton_bag._cell
        this_x = cell.x
        return self.filter(lambda c: c.x == this_x)


class Table(Bag):
    """A bag which represents an entire sheet.
       Features indices to speed retrieval by coordinate.
       Also includes functions for importing tables into XYPath"""
    def __init__(self, name=""):
        super(Table, self).__init__(table=self, name=name)
        self.x_index = defaultdict(lambda: Bag(self))
        self.y_index = defaultdict(lambda: Bag(self))
        self.xy_index = defaultdict(lambda: Bag(self))
        self._max_x = -1
        self._max_y = -1
        self.sheet = None

    def rows(self):
        """Get bags containing each row's cells, in order"""
        for row_num in range(0, self._max_y + 1):  # inclusive
            yield self.y_index[row_num]

    def cols(self):
        """Get bags containing each column's cells, in order"""
        for col_num in range(0, self._max_x + 1):  # inclusive
            yield self.x_index[col_num]

    def add(self, cell):
        """Under the hood: add a cell to a table and the table's indices.
           Used in the construction of a table.
           """
        self.x_index[cell.x].add(cell)
        self.y_index[cell.y].add(cell)
        self.xy_index[(cell.x, cell.y)].add(cell)
        self._max_x = max(self._max_x, cell.x)
        self._max_y = max(self._max_y, cell.y)
        super(Table, self).add(cell)

    def get_at(self, x=None, y=None):
        """Directly get a singleton bag, via the indices.
           Faster than Bag.filter"""
        # we use .get() here to avoid new empty Bags being inserted
        # into the index stores when a non-existant coordinate is requested.
        if x is None and y is None:
            raise TypeError('get_at requires at least one x or y value')
        if x is None:
            return self.y_index.get(y, Bag(self))
        if y is None:
            return self.x_index.get(x, Bag(self))
        return self.xy_index.get((x, y), Bag(self))

    @staticmethod
    def from_filename(filename, table_name=None, table_index=None):
        """Wrapper around from_file_object, automatically handles
         extracting extension"""
        extension = os.path.splitext(filename)[1].strip('.')
        with open(filename, 'rb') as f:
            return Table.from_file_object(f, extension,
                                          table_name=table_name,
                                          table_index=table_index)

    @staticmethod
    def from_file_object(fobj, extension='',
                         table_name=None, table_index=None):
        """Load table from file object. You must specify a single table's name or
           its position number. If you don't know these, try from_messy"""
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
        """Import a rowset (table) from messytables, e.g. to work with each
           table in turn:
               tables = messytables.any.any_tableset(fobj)
               for mt_table in tables:
                   xy_table = xypath.Table.from_messy(mt_table)
                   ..."""
        assert isinstance(messy_rowset, messytables.core.RowSet),\
            "Expected a RowSet, got a %r" % type(messy_rowset)
        new_table = Table.from_iterable(
            messy_rowset,
            value_func=lambda cell: cell.value,
            properties_func=lambda cell: cell.properties)

        if hasattr(messy_rowset, 'sheet'):
            new_table.sheet = messy_rowset.sheet
        return new_table

    @staticmethod
    def from_iterable(table, value_func=lambda cell: cell,
                      properties_func=lambda cell: {}):
        """Make a table from a pythonic table structure.
           The table must be an iterable which returns rows (in top-to-bottom order),
           which in turn are iterables which returns cells (in left-to-right order).
           value_func and properties_func specify how the cell maps onto an _XYCell's
           value and properties. The defaults assume that you have a straight-forward
           list of lists of values."""

        new_table = Table()
        for y, row in enumerate(table):
            for x, cell in enumerate(row):
                new_table.add(
                    _XYCell(
                        value_func(cell),
                        x,
                        y,
                        new_table,
                        properties_func(cell)))
        return new_table

    @staticmethod
    def from_bag(bag):
        """Make a copy of a bag which is its own table.
           Useful when a single imported table is two logical tables"""
        new_table = Table()
        for bag_cell in bag.unordered:
            new_table.add(bag_cell._cell.copy(new_table))
        return new_table
