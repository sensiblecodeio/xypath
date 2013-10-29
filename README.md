## xypath

Select different parts of a spreadsheet via functions.

[![Build Status](https://travis-ci.org/scraperwiki/xypath.png?branch=master)](https://travis-ci.org/scraperwiki/xypath)


```
----------------------------------------------------------------------
| animal  | habitat    | max age | population 2012 | Population 2013 |
| zebra   | grasslands | 40      | 20M             | 21M             |
| baboon  | jungle     | 45      | 35M             | 40M             |
| narwhal | ocean      | 115     | 1M              | 500,000         |
----------------------------------------------------------------------
| AnimalSheet |
                                               * not strictly accurate
```

## Example

Question: **What is the change in population for each type of animal between 2012 and 2013?**

First, we need to load the spreadsheet. Supposing we've got it on disk already.

```python
import messytables
table = xypath.Table.from_filename("animals.xls", table_name='AnimalSheet')
```

Next we need to find the *row* and *column* headers. In this case the row headers are "zebra", "baboon" and "narwhal" and the column headers are "population 2012" and "Population 2013" (note the change in case!)

One way of getting the row headers would be to find "animal" and *fill down* to get the actual animals:

```python
animals = table.filter('animal').assert_one().fill(xypath.DOWN)
```

Let's break that down. First we use the table ``filter`` method which finds one or more cells matching the given argument. If you simply provide a string like ``animal`` it will search for exact matches. ``filter`` returns a ``Bag`` which is a cell container with some useful properties.

``assert_one`` blows up if the Bag doesn't contain exactly one cell.

We then do ``fill(xypath.DOWN)`` which gets all the cells below and *excluding* the "animal" cell.

Next we need to find the column containing the year. For this we will use a regular expression.
```python
years = table.filter(re.compile('[Pp]opulation \d{4}'))
```

The ``filter`` function recognises that it's been passed a regular expression and uses it to find matching cells in the table.

Now we've got two bags:

1. ``animal`` contains "zebra", "baboon" and "narwhal"
2. ``years`` contains "population 2012" and "Population 2013"

Next we want to find the cells which line up with each of those animal and year cells.

```python
for (animal, year, population) = animals.junction(years):
    print("{0} : {1} : {2}".format(
        animal.value, year.value, population.value))
```

This would print:
```
zebra : population in 2012 : 20M
baboon : population in 2012 : 35M
narwhal : population in 2012 : 1M
zebra : Population in 2012 : 21M
baboon : Population in 2012 : 40M
narwhal : Population in 2012 : 500,000
```

You can ``junction`` two Bags of header cells together the intersection between each pair of cells. Junction always yields a three-long tuple, in this case containing ``(animal, year, population)``.

It's left up to the reader to the year from the population string and convert the millions to reasonable numbers!

## Loading tables

```python
table = xypath.Table.from_filename("mysheet.xls")
```

By using a file-object:

```python
with open('spreadsheet.xls') as f:
    table = xypath.Table.from_file_object(f, table_index=0)
```

Note that you need to specify which table in the spreadsheet ``table_name`` (relating to ie Excel sheet name) or ``table_index`` (where 0 is the first sheet found)


From a URL (via a StringIO file-like-object):

```python
import requests
from cStringIO import StringIO

response = requests.get("http://example.io/mysheet.xls")
f = StringIO(response.content)
table = xypath.Table.from_file_object(f, table_name='Sheet1')
```


Or using the underlying messytables library directly:

```python
xypath_tables = []
with open('spreadsheet.xls', 'rb') as f:
    for messy_table in messytables.excel.XLSTableSet(f).tables:
        xypath_table = xypath.Table.from_messy(messy_table)
```

## Filtering

You can use the ``filter(..)`` method to get ``Bags`` of cells which match certain criteria.

```python
bag.filter("kitten")                     # cell.value is exactly 'kitten'
table.filter(re.compile(".a.*e"))        # regular expression of cell.value
table.filter(hamcrest.ends_with("c"))    # any pyhamcrest matcher on cell.value
```

All the above matchers act exclusively on the *value* of the cell.

It's also possible to pass any callable to ``filter``. In this case, filter passes the ``cell`` to the callable
so it's possible to access properties such as ``cell.x`` and ``cell.value``:

```python
def is_header_cell(cell):
    return cell.x == 0 and cell.value.lower().startswith('population ')

table.filter(is_header_cell)

table.filter(lambda cell: cell.x == 2)   # explicit lambda function on each cell
```

## Other Selection Methods

Select different cells in the table based on those currently in the bag
```python
def has_same_text(table_cell, bag_cell):
    return table_cell.value == bag_cell.value
    
bag.select(has_same_text)  # cells with same value
bag.shift(x=-2)            # cells two to the left of the current cells
bag_b = bag_a.fill(xypath.LEFT)      # cells to the LEFT (RIGHT, UP, DOWN, UP_RIGHT ...) excluding bag_a
```

## Method Chaining

Chain methods together; everything returns a bag!
```python
dollars = table.filter("Amount").assert_one().fill(xypath.DOWN).filter(re.search("$"))
```

## Singleton Bags

When a Bag contains only one cell (a *singleton* Bag), you can call ``bag.value`` and get the value of the single cell inside the bag. This is also true for ``cell.x``, ``cell.y`` etc.

Get the value (of a bag containing only one cell) or 
```python
lonely_cell.value
```

Get cells which are at the intersection of two other cells:
```
triplets = row_header_bag.junction(column_header_bag)
```
