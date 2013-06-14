## xypath

Select different parts of a spreadsheet via functions.

[![Build Status](https://travis-ci.org/scraperwiki/xypath.png?branch=master)](https://travis-ci.org/scraperwiki/xypath)

There are "bags" of cells: each cell keeping track of it's position, value, etc.
The bag keeps track of which table it's from.
Tables are simply specialised bags, which have the property that their table is themselves.

1. Import a table: either directly from a filename:

```python
    table = xypath.Table.from_filename("mysheet.xls")
```

   by using a filehandle:

```python
    data = requests.get("http://example.io/mysheet.xls").content
    table = xypath.Table.from_file_object(StringIO.StringIO(data))
```

   or using messytables explicitly:

```python
    messy = messytables.excel.XLSTableSet(open('mysheet.xls'))
    table = xypath.Table.from_messy(messy.tables[0])
```

2. Match cells by filtering a bag or table
```python
    bag.filter(lambda cell: cell.x == 2)   # explicit lambda function on each cell
    table.filter("kitten")                 # value is exactly 'kitten'
    table.filter(re.match(".a.*e"))        # regular expression of value; re.search works too
    table.filter(hamcrest.ends_with("c"))  # any pyhamcrest matcher
   
```
   All but the first act exclusively on the value; the lambda can act on the
   properties of the individual cells.

3. Select different cells in the table based on those currently in the bag
```python
    bag.select(lambda table_cell, bag_cell: table_cell.value == bag_cell.value)  # cells with same value
    bag.shift(x=-2)  # cells two to the left of the current cells
    bag.fill(xypath.LEFT)  # cells to the LEFT ( RIGHT, UP, DOWN, UP_RIGHT ...)
```

4. Chain methods together; everything returns a bag!
```python
    dollars = table.filter("Amount").assert_one().fill(xypath.DOWN).filter(re.search("$"))
```

5. Get the value (if there's only one cell) or get cells which are at the intersection of two other cells
```python
    lonely_cell.value()
    triplets = row_header_bag.junction(column_header_bag)
```
