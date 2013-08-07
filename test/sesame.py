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


def f(in_table, a):
    for food, b in a():
        for indic, c in b():
            print food, indic, c


def indics(food):
    return [food+"A", food+"B"]


def a():
    for food in foods:
        def b(food=food):
            for month in months:
                yield month, None
        yield food, b

assert f(in_table, a) == out_table
