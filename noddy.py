import xypath

xy = xypath.Table.from_filename("fixtures/noddy.xls", table_index=0)
category = xy.filter("category")
cats = category.fill(xypath.DOWN).filter(lambda cell: cell.value)
years = xy.filter("years").fill(xypath.RIGHT).filter(lambda cell: cell.value)


def horz():
    for cat in cats:
        product = cat.shift(xypath.RIGHT)
        units = product.shift(xypath.RIGHT).fill(xypath.DOWN,
                                                 stop_before=lambda c: c.value == "")
        for unit in units:
            status = unit.shift(xypath.RIGHT)
            yield {"product": product.value,
                   "unit": unit.value,
                   "status": status.value,
                   "_y": status.y}


def vert():
    for year in years:
        months = year.shift(xypath.DOWN).fill(xypath.RIGHT, stop_before=lambda c: c.value=="jan")
        for month in months:
            yield {"year": year.value,
                   "month": month.value,
                   "_x": month.x}

hs = list(horz())
vs = list(vert())

for ih, h in enumerate(hs):
    for iv, v in enumerate(vs):
        print ih, iv
        c=dict(v)
        c.update(h)
        c['_value'] = xy.get_at(c['_x'], c['_y']).value
        print c
