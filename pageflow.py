from basetoken import Token
from baselexer import Lexer
from baseparser import Parser
import codecs

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

class InvalidCharacter(Exception): pass

class FlowLexer(Lexer):
    def __init__(self, file_):
        super(FlowLexer, self).__init__(file_)

    def read(self, condition):
        buffer_ = ''
        while condition(self._current_character):
            buffer_ += self._current_character
            self.consume()
        return buffer_

    def _wrapped(self, head, tail):
        self.match(head)
        buffer_ = self.read(self.is_letter)
        self.match(tail)
        return buffer_

    def _button(self):
        buffer_ = self._wrapped(*'[]')
        return Button(buffer_)

    def _image(self):
        buffer_ = self._wrapped(*'{}')
        return Image(buffer_)

    def _action(self):
        buffer_ = self._wrapped(*'<>')
        return Action(buffer_)

    def _condition(self):
        self.match('(')
        self.match(':')
        buffer_ = self.read(self.is_letter)
        self.match(')')
        return Condition(buffer_)

    def _line(self):
        self.match('=')
        self.match('=')
        self.read(lambda c: c in '=')
        return Line('=')

    def _line_thin(self):
        self.match('-')
        self.match('-')
        self.read(lambda c: c in '-')
        return Line('-')

    def _number(self):
        buffer_ = self.read(self.is_digit)
        self.match('.')
        return Number(buffer_)

    def _is_text(self, c):
        # not lb, not condition, not variable
        return (c not in '\n(')

    def _text(self):
        buffer_ = self.read(self._is_text)
        buffer_ = buffer_.encode('utf-8')
        return Text(buffer_)

    def _variable(self):
        self.match('$')
        buffer_ = self.read(self.is_letter)
        return Variable(buffer_)

    def _whitespace(self):
        self.read(self.is_space)

    def next_token(self):
        while self._current_character != Lexer.EOF:
            if self.is_space(self._current_character):
                self._whitespace()
                continue

            if self.is_linebreak(self._current_character):
                self.consume()
                return LineBreak('\\n')

            if self._current_character == '=':
                return self._line()

            if self._current_character == '-':
                return self._line_thin()

            if self.is_letter(self._current_character):
                return self._text()

            if self.is_digit(self._current_character):
                return self._number()

            if self._current_character == '[':
                return self._button()

            if self._current_character == '{':
                return self._image()

            if self._current_character == '<':
                return self._action()

            if self._current_character == '(':
                return self._condition()

            if self._current_character == '.':
                return self._text()

            if self._current_character == '\\':
                return self._text()

            raise InvalidCharacter('%s (%s)' % (self._current_character, ord(self._current_character)))
        return EoF('EOF')

class Expression(object):
    def __str__(self):
        return type(self).__name__

class PageFlowParser(Parser):
    def __init__(self, lexer):
        super(PageFlowParser, self).__init__(lexer, 2)

    def match(self, token_type):
        token = self.next()
        if token.is_a(LineBreak): print
        else: print token
        super(PageFlowParser, self).match(token_type)
        return token

    def parse(self):
        self.pages()

    def pages(self):
        self.page()
        self.lb()
        while self.peek(Number):
            self.page()
            self.lb()

    def page(self):
        print
        print
        self.content()
        self.interactions()

    def content(self):
        self.head()
        self.line()
        self.body()

    def lb(self):
        while self.peek(LineBreak):
            self.consume()

    def body(self):
        self.text()
        self.lb()
        while self.peek(Text):
            self.text()
            self.lb()

    def head(self):
        self.match(Number)
        self.text()
        if self.peek(Condition):
            self.match(Condition)
        self.lb()

    def line(self):
        self.match(Line)
        self.lb()

    def text(self):
        self.match(Text)

    def interactions(self):
        self.lb()
        self.interaction()
        self.lb()
        if self.peek(Button) or self.peek(Image) or self.peek(Action):
            self.interaction()
            self.lb()

    def interaction(self):
        print
        if self.peek(Button):
            self.match(Button)
        if self.peek(Image):
            self.match(Image)
        if self.peek(Action):
            self.match(Action)

import sys

with codecs.open('text.txt', 'r', 'utf-8-sig') as file_:
    if 'stream' in sys.argv:
        lex = FlowLexer(file_.read())
        token = lex.next_token()
        while not token.is_a(EoF):
            print str(token).decode('utf-8-sig')
            token = lex.next_token()
        exit()
    else:
        parser = PageFlowParser(FlowLexer(file_.read()))
        parser.parse()