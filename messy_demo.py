import messytables
import xypath
from xypath import Table
import re

def textsearch(s):
    return lambda b: re.search(s, unicode(b))

messy = messytables.excel.XLSTableSet(open("fixtures/wpp.xls", 'rb'))
table = Table.from_messy(messy.tables[0])

row_two = table.match(lambda b: b.y == 2)
print row_two
print "*"
row_three = row_two.select(lambda t, b: t.y == b.y + 1)
print row_three
print "*"


print row_three.match(textsearch("liz"))

#lambda should go from [set, cell -> bool] set = current set, cell = cell in table.
#any

# up: any 
