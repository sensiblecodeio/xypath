import xypath
import messytables

mt, = messytables.any.any_tableset(open('../fixtures/q.csv')).tables
xy = xypath.Table.from_messy(mt)
print "loaded"

xy.filter("GHO (DISPLAY)").headerheader2(xypath.DOWN, xypath.RIGHT, 'display')
xy.filter("YEAR (DISPLAY)").headerheader2(xypath.DOWN, xypath.RIGHT, "year")
bigdict = {"_placeholder": {"1": xy.filter("Numeric").fill(xypath.DOWN)}}

print "Bigdict calculated"
print list(xy.xyzzy2(bigdict, valuename="value", length=3))

# messy: grouping wasn't that expensive!
# length: horrid!
# need to specify which item we iterate over for final pass (i.e. just value cells, for pref)

