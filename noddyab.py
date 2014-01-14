import xypath

all_xy = xypath.Table.from_filename("fixtures/noddyab.xls", table_index=0)


def bagsplit():
    table_ys = [cell.y for cell in all_xy.filter("Table")]
    #table_ys.insert(0, 0)
    table_ys.append(float("inf"))
    for min_y, max_y in zip(table_ys[:-1], table_ys[1:]):
        print min_y, max_y
        bag = all_xy.filter(lambda cell: cell.y < max_y and cell.y >= min_y)
        yield xypath.Table.from_bag(bag)


def process_bag(xy):
    table = xy.filter("Table").shift(xypath.RIGHT).assert_one()
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
                yield {"category": category.value,
                       "product": product.value,
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

    for h in hs:
        for v in vs:
            c = dict(v)
            c.update(h)
            c['_value'] = xy.get_at(c['_x'], c['_y']).value
            c['table'] = table.value
            yield c


for bag in bagsplit():
    print [x.values() for x in process_bag(bag)]

