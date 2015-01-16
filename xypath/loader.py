import messytables
import xypath

def table_set(filename):
    with open(filename, 'rb') as f:
        mt_tableset = messytables.any.any_tableset(f)
    return mt_tableset

def get_sheets(mt_tableset, ids):
    if isinstance(ids, int) or isinstance(ids, basestring) or callable(ids):
        # it's a single thing, listify it
        ids = (ids, )
    for identifier in ids:
        if isinstance(identifier, int):
            mt_table = mt_tableset.tables[identifier]
            yield xypath.Table.from_messy(mt_table)
        elif isinstance(identifier, basestring):
            for mt_table in mt_tableset.tables:
                if mt_table.name == identifier:
                    yield xypath.Table.from_messy(mt_table)
        elif callable(identifier):
            for mt_table in mt_tableset.tables:
                xy_table = xypath.Table.from_messy(mt_table)
                if identifier(xy_table):
                    yield xy_table
        else:
            raise NotImplementedError("Don't know what to do with a {!r}".format(type(identifier)))
