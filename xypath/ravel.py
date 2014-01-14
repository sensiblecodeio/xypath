import xypath
def _labellize(bag):
    """
    for now, just a groupby over the bag
    need to be smarter (e.g. gap recognition)
    * insight: is expensive and is invoked every time on a constant thing (the 2nd gen headers)
    """
    # for now, just groupby,
    # in future, need to be smarter (e.g. gap recognition)
    # might want to allow
    import itertools
    sort = lambda cell: cell.value
    for label, group in itertools.groupby(sorted(bag, key=sort), sort):
        yield label, xypath.Bag.from_list(group)


def ravel(in_bag, instructions, labels=None, value_bag=None):
    # What can change the nature of a spreadsheet?
    """flatten? olapify? a table.
       Takes a table plus a list of lambdas which take a bag.
       Each function specifies either a dimension (by specifying header cells)
       or a group of value cells: the latter are preceeded by a 'None'
       labels and value_bag are internal details used in recursion, and should
       not be specified in the function call.
       Almost, but not entirely, like xyzzy"""

    # Initialise some defaults for the first pass.
    # (these are explicitly passed for future passes)
    if value_bag is None:
        value_bag = in_bag.table
    if labels is None:
        labels = []

    instructions = list(instructions)

    if not instructions:
        # we've bottomed out with a full set of labels and - hopefully -
        # a singleton bag which we just want the value from.
        # If there's nothing in the bag, that's fine.
        if value_bag:
            yield labels, value_bag.value
        return

    current_function = instructions.pop(0)
    if current_function:
        # we're looking at a function to get the next set of headers.
        # note the use of list to ensure that we're working with copies
        # of the things we're mutating.
        label_cells = current_function(in_bag)
        for label, bag in _labellize(label_cells):
            new_labels = list(labels)
            new_labels.append(label)
            p = ravel(bag, instructions, new_labels, value_bag)
            for item in p:
                yield item
    else:
        # there was a None, which indicates that the next item is a
        # function to get a pile of values.
        value_function = instructions.pop(0)
        new_value_bag = value_function(in_bag).intersection(value_bag)
        p = ravel(in_bag, instructions, labels, new_value_bag)
        for item in p:
            yield item

