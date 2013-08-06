import xypath
import messytables

mt, = messytables.any.any_tableset(open('../fixtures/q.csv')).tables
xy = xypath.Table.from_messy(mt)

print xy.group()
