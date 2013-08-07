from pprint import pprint

def maketable(s):
    lines = s.strip().split('\n')
    return [x.split(' ') for x in lines]

foods = "ei"
months = "BCD"

in_table = maketable("""
A B C D
e 1 2 3
i 4 5 6
""")

out_table = maketable("""
e B 1
e C 2
e D 3
i B 4
i C 5
i D 6""")


def f(table, a):
    for food, b in a(table):
        for indic, c in b():
            yield [food, indic, c()]


def a(table):
    for i, food in enumerate(foods, 1):
        def b(food=food, i=i):
            for j, month in enumerate(months, 1):
                def g(food=food, month=month, i=i, j=j):
                    return in_table[i][j]
                yield month, g
        yield food, b

assert list(f(in_table, a)) == out_table
# =============================================
print "4"
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

pprint (in_table)
def f(table, a):
    for year, b in a(table):
        for food, c in b():
            for month, d in c():
                yield [year, food, month, d()]


def a(table):
    for i, year in enumerate(years, 0):
        def b(year=year, i=i):
            for j, food in enumerate(foods, i*(len(foods)+1)+2):
                def g(year=year, food=food, i=i, j=j):
                    for k, month in enumerate(months, 1):
                        def h(year=year, food=food, month=month, i=i, j=j, k=k):
                            print i, j, k, in_table[j]
                            return in_table[j][k]
                        yield month, h
                yield food, g
        yield year, b

pprint (list(f(in_table, a)))
assert list(f(in_table, a)) == out_table
