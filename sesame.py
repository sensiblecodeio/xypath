from supergenerator import supergenerator, _from
from pprint import pprint
import StringIO
import xypath
import messytables

def maketable(s):
    lines = s.strip().split('\n')
    return [x.split(' ') for x in lines]

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
    years = table.column(1)
    foods = table.column(2)
    months = table.column(3)
    values = table.column(4)
    for year, month, food, value in zip(years, foods, months, values):
        yield [year, month, food, value]

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

def __from(f):
    return supergenerator(f)()

YEARS = "#!*"
FOODS = "ei"
MONTHS = "YZ"
@supergenerator
def a(table):
    years = xy.filter(lambda x: x.value in YEARS)
    months = xy.filter(lambda x: x.value in MONTHS)
    
    for year, nextyear in zip(years, years[1:]): 
        def b():
            for food in xy._range(year, nextyear)[:,1:-1]
                for month in months:
                    yield [year.value, food.value, month.value, xy.get_at(month.x, food.y).value]
        yield __from(b)



q = list(a(in_table))
pprint(q)
assert q == out_table
