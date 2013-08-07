from supergenerator import supergenerator, _from
from pprint import pprint
import StringIO
import xypath
import messytables

def maketable(s):
    lines = s.strip().split('\n')
    return [x.split(' ') for x in lines]

foods = "ei"
months = "YZ"
years = "#!*"
# indicators = ",."

in_table_raw = """
X Y Z
#
e 1 2
i 3 4
!
e 5 6
i 7 8
*
e 9 A
f B C
"""

in_table = maketable(in_table_raw)

out_table = maketable("""
# e Y 1
# e Z 2
# i Y 3
# i Z 4
! e Y 5
! e Z 6
! i Y 7
! i Z 8
* e Y 9
* e Z A
* i Y B
* i Z C
""")


@supergenerator
def a(table):
    for i, year in enumerate(years, 0):
        @supergenerator
        def b():
            for j, food in enumerate(foods, i*(len(foods)+1)+2):
                @supergenerator
                def c():
                    for k, month in enumerate(months, 1):
                            yield [year, food, month, table[j][k]]
                yield _from(c())
        yield _from(b())


q = list(a(in_table))
assert q == out_table

mt, = messytables.any.any_tableset(
    StringIO.StringIO(in_table_raw.replace(' ', '\t')), extension='tsv').tables
xy = xypath.Table.from_messy(mt)

"""
year, nextyear in zip(years, years[1:])
range(year, nextyear)

a[1:,1:]
a.shiftdown(1).shiftright(1)
"""

@supergenerator
def a(table):
    
    for year in xy.filter(lambda x: x.value in years):
        @supergenerator
        def b():
            for food in xy.filter(lambda x: x.value in foods and 1): # in terms of year!
                @supergenerator
                def c():
                    for month in xy.filter(lambda x: x.value in months):
                            yield [year.value, food.value, month.value, xy.get_at(month.x, food.y).value] #table]
                yield _from(c())
        yield _from(b())



q = list(a(in_table))
pprint(q)
assert q == out_table
