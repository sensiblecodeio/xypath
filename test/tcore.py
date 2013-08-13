#!/usr/bin/env python
import sys
import unittest
sys.path.append('xypath')
import xypath

import messytables
from os.path import dirname, abspath, join as pjoin, splitext

FIXTURE_DIR = pjoin(abspath(dirname(__file__)), '..', 'fixtures')

def get_extension(filename):
    """
    >>> get_extension('/foo/bar/test.xls')
    'xls'
    """
    return splitext(filename)[1].strip('.')

def get_fixture_filename(name):
    return pjoin(FIXTURE_DIR, name)

def get_messytables_fixture(name, table_index=0, memoized={}):
    """
    Memoized function for loading fixtures
    """
    
    if name not in memoized:
        with open(name, "rb") as fd:
            messy = messytables.any.any_tableset(fd)
            messytable = messy.tables[table_index]
        memoized[name] = (messy, xypath.Table.from_messy(messytable))

    return memoized[name]

class TCore(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.wpp_filename = get_fixture_filename("wpp.xls")
        cls.messy, cls.table = get_messytables_fixture(cls.wpp_filename)

    def setUp(self):
        pass

class TMissing(unittest.TestCase):
    @classmethod
    def setup_class(cls):
        cls.wpp_filename = get_fixture_filename("missingcell.csv")
        cls.messy, cls.table = get_messytables_fixture(cls.wpp_filename)

    def setUp(self):
        pass
