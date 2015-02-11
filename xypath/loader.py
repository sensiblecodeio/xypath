import messytables
import xypath

def table_set(filename, *args, **kwargs):
    """get all the tables for a single spreadsheet"""
    with open(filename, 'rb') as f:
        mt_tableset = messytables.any.any_tableset(f, *args, **kwargs)
    return mt_tableset

def get_sheets(mt_tableset, ids):
    """get a subset of the tables from a tableset.
    Select them via a list or single item from:

    a string: tables with that name
    a number: the table with that index
    "*": get all of them
    a function: tables for which f(table) is truthy.
        i.e. you can use this with XYPath expressions.

    [5, 'kitten',
    lambda table: table.get_at(0,0).value == 'dog']
    will get you the 6th tab, all tabs named 'kitten'
    and all tabs where the top-left cell contains 'dog'."""

    def xy():
        xy_table = xypath.Table.from_messy(mt_table)
        xy_table.index = table_index
        return xy_table

    if isinstance(ids, (int, basestring)) or callable(ids):
        # it's a single thing, listify it
        ids = (ids, )

    for table_index, mt_table in enumerate(mt_tableset.tables):
        for identifier in ids:
            if identifier == '*':
                yield xy()
            elif isinstance(identifier, int):
                if identifier == table_index:
                    yield xy()
            elif isinstance(identifier, basestring):
                if identifier == mt_table.name:
                    yield xy()
            elif callable(identifier):
                xy_table = xy()
                if identifier(xy_table):
                    yield xy_table
            else:
                raise NotImplementedError("Don't know what to do with a {!r}".format(type(identifier)))
