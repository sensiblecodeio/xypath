#!/usr/bin/env python

from collections import OrderedDict
from itertools import groupby
from xypath import Bag


class LookupFailureError(Exception):
    pass


def group(self, keyfunc=None):  # XYZZY
    """get a dictionary containing lists of singleton bags with the same
       value (by default; other functions available)"""
    groups = {}
    if keyfunc is None:
        keyfunc = lambda x: x.value
    protogroups = groupby(sorted(self, key=keyfunc), key=keyfunc)
    for k, v in protogroups:
        newbag = Bag.from_list(v)
        newbag.table = self.table
        groups[k] = newbag
    return groups


def headerheader(self, dir1, dir2, **kwargs):  # XYZZY
    """Given a header (e.g. "COUNTRY") get all things in one direction
       from it (e.g. down: "FRANCE", "GERMANY"), then use those to get
       a suitable xyzzy dict"""
    header = group(self.fill(dir1), **kwargs)
    return {k: header[k].fill(dir2) for k in header}


def are_distinct(fields):
    """True if the fields passed to xyzzy don't contain repeating cells."""
    allbags = set()
    bagcount = 0
    for field in fields:
        for bag in field.values():
            allbags = allbags.union(bag)
            bagcount = bagcount + len(bag)
    return len(allbags) == bagcount


def xyzzy(self, fields, valuename='_value'):  # XYZZY
    assert are_distinct(fields.values())
    fieldkeys = fields.keys()
    assert valuename not in fieldkeys

    def fieldlookup(cell):
        for fieldvalue in fields[field]:  # AFG, GBR; 1998, 1999
            if cell in fields[field][fieldvalue]:  # i.e. in bag
                return fieldvalue
        raise LookupFailureError

    for cell in self:
        path = OrderedDict()
        try:
            for field in fields:  # country, year
                path[field] = fieldlookup(cell)
        except LookupFailureError:
            continue

        path[valuename] = cell.value
        yield path
