#!/usr/bin/env python

from collections import OrderedDict
from itertools import groupby
import xypath
from xypath import Bag

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
    # TODO: test at this stage that fieldvalue bags don't overlap:
    # i.e. len(union of all bags) = sum(length of each bag) for each field.
    # instead of checking all combinations have no more than one match
    # DONE, use are_distinct. Still need to remove existing expensive code.

    for cell in self:
        path = OrderedDict()
        for i, field in enumerate(fields):  # country, year
            for fieldvalue in fields[field]:  # AFG, GBR; 1998, 1999

                if cell in fields[field][fieldvalue]:  # i.e. in bag
                    assert field not in path  # only one match per field
                    path[field] = fieldvalue
                    break  # speedup - need test at top of function, really!
            if len(path) != i+1:
                break  # save unnecessary work

        # skip values which aren't complete in all dimensions
        if len(path) != len(fieldkeys):
            # if len(path) > 0:
            #     print "found %r matches for %r: %r" % (len(path), cell, path.keys())
            continue
        # add dictionary of cell details to list
        path[valuename] = cell.value
        yield path
