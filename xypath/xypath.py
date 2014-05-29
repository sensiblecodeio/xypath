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
from itertools import product, takewhile

import contrib.excel

UP = (0, -1)
RIGHT = (1, 0)
DOWN = (0, 1)
LEFT = (-1, 0)
UP_RIGHT = (1, -1)
DOWN_RIGHT = (1, 1)
UP_LEFT = (-1, -1)
DOWN_LEFT = (-1, 1)


class XYPathError(Exception):
    """Errors caused by problems with spreadsheet layouts should descend from this."""
    pass


class JunctionError(RuntimeError, XYPathError):
    """Junction area overlaps an input cell, and 'paranoid' isn't disabled."""
    pass


class NoCellsAssertionError(AssertionError, XYPathError):
    """Raised by Bag.assert_one() if the bag contains zero cells."""
    pass


class MultipleCellsAssertionError(AssertionError, XYPathError):
    """Raised by Bag.assert_one() if the bag contains multiple cells."""
    pass


def describe_filter_method(filter_by):
        if callable(filter_by):
            return "matching a function called {}".format(filter_by.__name__)
        if isinstance(filter_by, basestring):
            return "containing the string {!r}".format(filter_by)
        if have_ham and isinstance(filter_by, hamcrest.matcher.Matcher):
            return "containing "+str(filter_by)
        if isinstance(filter_by, re._pattern_type):
            return "matching the regex {!r}".format(filter_by.pattern)
        else:
            return "which we're surprised we found at all"


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
        return "_XYCell(%r, %r, %r)" % \
            (self.value, self.x, self.y)

    def __unicode__(self):
        return unicode(self.value)

    def junction(self, other, direction=DOWN, paranoid=True):
        """ gets the lower-right intersection of the row of one, and the
        column of the other.

        paranoid: should we panic if we're hitting one of our input cells?"""

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
        if not isinstance(x, int):
            assert y == 0, \
                "_XYCell.shift: x=%r not integer and y=%r specified" % (x, y)
            return self.shift(x[0], x[1])
        return self.table.get_at(self.x + x, self.y + y)._cell


class CoreBag(object):
    def pprint(self, *args, **kwargs):
        return contrib.excel.pprint(self, *args, **kwargs)

    def as_list(self, *args, **kwargs):
        return contrib.excel.as_list(self, *args, **kwargs)

    def filter_one(self, filter_by):
        return contrib.excel.filter_one(self, filter_by)

    def excel_locations(self, *args, **kwargs):
        return contrib.excel.excel_locations(self, *args, **kwargs)

    """Has a collection of _XYCells"""
    def __init__(self, table):
        self.__store = set()
        self.table = table

    def add(self, cell):
        if not isinstance(cell, _XYCell):
            raise TypeError("Can only add _XYCell types to Bags: {}".format(
                            cell.__class__))
        self.__store.add(cell)

    def __eq__(self, other):
        if not isinstance(other, CoreBag):
            return False
        return (self.table is other.table and
                self.__store == other.__store)

    def __len__(self):
        return len(self.__store)

    def __repr__(self):
        return repr(self.__store)

    @classmethod
    def singleton(cls, cell, table):
        """
        Construct a bag with one cell in it
        """
        bag = cls(table=table)
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
        assert self.table is rhs.table,\
            "Can't difference bags from separate tables"
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

    def __and__(self, rhs):
        return self.intersection(rhs)

    def intersection(self, rhs):
        assert self.table is rhs.table, \
            "Can't take intersection of bags from separate tables"
        new = copy(self)
        new.__store = self.__store.intersection(rhs.__store)
        return new

    def select(self, function):
        return self.table.select_other(function, self)

    def select_other(self, function, other):
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
            raise ValueError("filter_by must be function, hamcrest filter, compiled regex or string.")

    def _filter_internal(self, function):
        newbag = Bag(table=self.table)
        for bag_cell in self.unordered_cells:
            if function(bag_cell):
                newbag.add(bag_cell)
        return newbag

    def assert_one(self, message="assert_one() : {} cells in bag, not 1"):
        if len(self.__store) == 1:
            return self

        elif len(self.__store) == 0:
            raise NoCellsAssertionError(
                message.format(
                    len(self.__store)
                )
            )

        elif len(self.__store) > 1:
            raise MultipleCellsAssertionError(
                message.format(
                    len(self.__store)
                )
            )

    @property
    def _cell(self):
        try:
            xycell = list(self.assert_one().__store)[0]
        except AssertionError:
            l = len(list(self.__store))
            raise XYPathError("Can't use multicell bag as cell: (len %r)" % l)
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
    def from_list(cells):
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

    def fill(self, direction, stop_before=None):
        """Should give the same output as fill, except it
        doesn't support non-cardinal directions or stop_before.
        Twenty times faster than fill in test_ravel."""
        if direction in (UP_RIGHT, DOWN_RIGHT, UP_LEFT,
                                        UP_RIGHT):
            return self._fill(direction, stop_before)

        def what_to_get(cell):
            """converts bag coordinates into thing to pass to get_at"""
            cell_coord = (cell.x, cell.y)
            retval = []
            for cell_coord, direction_coord in zip(cell_coord, direction):
                if direction_coord != 0:
                    retval.append(None)
                else:
                    retval.append(cell_coord)
            return tuple(retval)  # TODO yuck

        if direction not in (UP, RIGHT, DOWN, LEFT):
            raise ValueError("Must be a cardinal direction!")

        ### this is what same_row/col should look like!
        small_table = None
        for cell in self.unordered_cells:
            got_rowcol = self.table.get_at(*what_to_get(cell))
            if small_table:
                small_table = small_table.union(got_rowcol)
            else:
                small_table = got_rowcol

        # now we use the small_table as if it was the table.
        (left_right, up_down) = direction
        bag = small_table.select_other(
            lambda table, bag: cmp(table.x, bag.x) == left_right
            and cmp(table.y, bag.y) == up_down,
            self
        )
        if stop_before is not None:
            return bag.stop_before(stop_before)
        else:
            return bag

    def stop_before(self, stop_function):
        """Assumes the data is:
           * in a single row or column
           * proceeding either downwards or rightwards
        """
        return Bag.from_list(list(
            takewhile(lambda c: not stop_function(c), self)))

    def _fill(self, direction, stop_before=None):
        """
        If the bag contains only one cell, select all cells in the direction
        given, excluding the original cell. For example, from a column heading
        cell, you can "fill down" to get all the values underneath it.

        If you provide a stop_before function, it will be called on each cell
        as a stop condition. For example, if you provide a stop_before function
        which tests cell.value for an empty string. This would stop the fill
        function before it reaches the bottom of the sheet, for example.
        """
        raise DeprecationWarning("2D fill is deprecated. Yell if you need it.")
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

    def same_row(self, bag):
        """
        Select cells in this bag which are in the same
        row as a cell in the other `bag`.
        """
        # TODO: make less crap - use Table.get_at()
        all_y = set()
        for cell in bag.unordered_cells:
            all_y.add(cell.y)
        return self.filter(lambda c: c.y in all_y)

    def same_col(self, bag):
        """
        Select cells in this bag which are in the same
        row as a cell in the other `bag`.
        """
        # TODO: make less crap
        all_x = set()
        for cell in bag.unordered_cells:
            all_x.add(cell.x)
        return self.filter(lambda c: c.x in all_x)


class Table(Bag):
    """A bag which represents an entire sheet"""
    def __init__(self, name=""):
        super(Table, self).__init__(table=self)
        self._x_index = defaultdict(lambda: Bag(self))
        self._y_index = defaultdict(lambda: Bag(self))
        self._xy_index = defaultdict(lambda: Bag(self))
        self._max_x = -1
        self._max_y = -1
        self.sheet = None

    def rows(self):
        for row_num in range(0, self._max_y + 1):  # inclusive
            yield self._y_index[row_num]

    def cols(self):
        for col_num in range(0, self._max_x + 1):  # inclusive
            yield self._x_index[col_num]

    def add(self, cell):
        self._x_index[cell.x].add(cell)
        self._y_index[cell.y].add(cell)
        self._xy_index[(cell.x, cell.y)].add(cell)
        self._max_x = max(self._max_x, cell.x)
        self._max_y = max(self._max_y, cell.y)
        super(Table, self).add(cell)

    def get_at(self, x=None, y=None):
        # we use .get() here to avoid new empty Bags being inserted
        # into the index stores when a non-existant coordinate is requested.
        if x is None and y is None:
            raise TypeError('get_at requires at least one x or y value')
        if x is None:
            return self._y_index.get(y, Bag(self))
        if y is None:
            return self._x_index.get(x, Bag(self))
        return self._xy_index.get((x, y), Bag(self))

    @staticmethod
    def from_filename(filename, table_name=None, table_index=None):
        extension = os.path.splitext(filename)[1].strip('.')
        with open(filename, 'rb') as f:
            return Table.from_file_object(f, extension,
                                          table_name=table_name,
                                          table_index=table_index)

    @staticmethod
    def from_file_object(fobj, extension='',
                         table_name=None, table_index=None):
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
        new_table = Table()
        for bag_cell in bag.unordered:
            new_table.add(bag_cell._cell.copy(new_table))
        return new_table
