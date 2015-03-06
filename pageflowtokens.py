from basetoken import Token
class Number(Token):
    def __init__(self, value):
        super(Number, self).__init__(int(value))

class Action(Token): pass
class Button(Token): pass
class Condition(Token): pass
class EoF(Token): pass
class Image(Token): pass
class Line(Token): pass
class LineBreak(Token): pass
class Text(Token): pass
class Unknown(Token): pass