def textsearch(s):
    import re
    return lambda b: re.search(s, unicode(b))

def extend(x, y):
    return lambda t, b: cmp(t.x, b.x) == x and cmp(t.y, b.y) == y

