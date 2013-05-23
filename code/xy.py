def textsearch(s):
    import re
    return lambda b: re.search(s, unicode(b))
