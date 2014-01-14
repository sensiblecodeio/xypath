import xypath

xy = xypath.Table.from_filename("fixtures/noddy.xls", table_index=0)
category = xy.filter("category").assert_one()
cats = category.fill(xypath.DOWN).filter(lambda cell: cell.value)
years = xy.filter("years").fill(xypath.RIGHT).filter(lambda cell: cell.value)
units_l = xy.filter("units").assert_one()
product_l = xy.filter("product").assert_one()
status_l = xy.filter("status").assert_one()
month_l = xy.filter("months").assert_one()

def horz():
    for cat in cats:
        product = cat.junction_overlap(product_l)
        units = product.junction_overlap(units_l).fill(xypath.DOWN,
                                                 stop_before=lambda c: c.value == "")  # TODO inclusive
        for unit in units:
            status = unit.junction_overlap(status_l)
            yield {"product": product.value,
                   "unit": unit.value,
                   "status": status.value,
                   "_y": status.y}


def vert():
    for year in years:
        months = year.junction_overlap(month_l).fill(xypath.RIGHT, stop_before=lambda c: c.value=="jan")
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
