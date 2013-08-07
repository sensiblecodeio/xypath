from supergenerator import supergenerator, _from
from pprint import pprint


def maketable(s):
    lines = s.strip().split('\n')
    return [x.split(' ') for x in lines]

foods = "ei"
months = "BC"
years = "#!*"
# indicators = ",."

in_table = maketable("""
A B C
#
e 1 2
i 3 4
!
e 5 6
i 7 8
*
e 9 A
f B C
""")

out_table = maketable("""
# e B 1
# e C 2
# i B 3
# i C 4
! e B 5
! e C 6
! i B 7
! i C 8
* e B 9
* e C A
* i B B
* i C C
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
                            yield [year, food, month, in_table[j][k]]
                yield _from(c())
        yield _from(b())


q = list(a(in_table))
pprint(q)
assert q == out_table
