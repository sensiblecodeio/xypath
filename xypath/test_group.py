import xypath
import messytables

mt, = messytables.any.any_tableset(open('../fixtures/q.csv')).tables
xy = xypath.Table.from_messy(mt)

bigdict = {"display": xy.filter("GHO (DISPLAY)").headerheader(xypath.DOWN, xypath.RIGHT),
           "year": xy.filter("YEAR (DISPLAY)").headerheader(xypath.DOWN, xypath.RIGHT),
           "_placeholder": {"1": xy.filter("Numeric").fill(xypath.DOWN)}}

print list(xy.xyzzy(bigdict))

