#!/usr/bin/env python

from collections import OrderedDict

def headerheader(self, dir1, dir2, **kwargs):  # XYZZY
    """Given a header (e.g. "COUNTRY") get all things in one direction
       from it (e.g. down: "FRANCE", "GERMANY"), then use those to get
       a suitable xyzzy dict"""
    header = self.fill(dir1).group(**kwargs)
    return {k: header[k].fill(dir2) for k in header}

def xyzzy(self, fields, valuename='_value'):  # XYZZY
    fieldkeys = fields.keys()
    assert valuename not in fieldkeys
    # TODO: test at this stage that fieldvalue bags don't overlap:
    # i.e. len(union of all bags) = sum(length of each bag) for each field.
    # instead of checking all combinations have no more than one match

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
        # if len(path) != len(fieldkeys):
        #     if len(path) > 0:
        #         print "found %r matches for %r: %r" % (len(path), cell, path.keys())
        #     continue
        # add dictionary of cell details to list
        path[valuename] = cell.value
        yield path
