
class b:
    def __init__(self, val):
        obj = a(val)
        print obj.val

ob = b(4)


class a:
    def __init__(self, val):
        self.val = val
