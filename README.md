## xypath

Select different parts of a spreadsheet via functions.

1. Import a table from messytable

```python
    messy = messytables.excel.XLSTableSet(open('mysheet.xls'))
    table = xypath.Table.from_messy(messy.tables[0])`
```

2. Match with lambda functions within a 'bag' of cells (such as a table)

```python
    self.table.match(lambda b: b.x == 2)
```

3. Extend (expand?) a bag of cells by checking if any cells match:

```python
    self.table.extend(lambda t, b: t.x == (b.x + 1)
```
