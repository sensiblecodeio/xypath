def excel_column_label(n):
    """
    Excel's column counting convention, counting from A at n=1
    """
    def inner(n):
        if n <= 0:
            return []
        if not n:
            return [0]
        div, mod = divmod(n - 1, 26)
        return inner(div) + [mod]
    return "".join(chr(ord("A") + i) for i in inner(n))

