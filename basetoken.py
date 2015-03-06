
class Token(object):
    def __init__(self, value=None):
        self.value = value

    def type(self):
        return type(self).__name__

    def is_a(self, token_type):
        return isinstance(self, token_type)

    def __str__(self):
        name = self.type().upper()
        return "<'%s', %s>" % (name, self.value or name)

    def __repr__(self):
        return str(self)