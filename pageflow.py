from baselexer import Lexer
from baseparser import Parser
from pageflowtokens import *
import codecs
import json

import sys
reload(sys)
ENCODING = 'utf-8-sig'
sys.setdefaultencoding(ENCODING)


class InvalidCharacter(Exception):
    pass


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
        buffer_ = self.read(lambda c: self.is_letter(c) or c == ' ')
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
        return (c not in '\n(')

    def _skip_one(self):
        self.consume()
        return self._text()

    def _text(self):
        buffer_ = self.read(self._is_text)
        return Text(buffer_)

    def _variable(self):
        self.match('$')
        buffer_ = self.read(self.is_letter)
        return Variable(buffer_)

    def _whitespace(self):
        self.read(self.is_space)

    def match_character(self):
        return {
            '=': self._line,
            '-': self._line_thin,
            '[': self._button,
            '{': self._image,
            '<': self._action,
            '(': self._condition,
            '.': self._text,
            '\\': self._skip_one,
        }.get(self._current_character, lambda: None)()

    def next_token(self):
        while self._current_character != Lexer.EOF:
            if self.is_space(self._current_character):
                self._whitespace()
                continue

            if self.is_linebreak(self._current_character):
                self.consume()
                return LineBreak('\\n')

            if self.is_letter(self._current_character):
                return self._text()

            if self.is_digit(self._current_character):
                return self._number()

            known = self.match_character()
            if not known:
                message = '%s' % (self._current_character)
                raise InvalidCharacter(message)
            return known
        return EoF('EOF')


class PageFlowParser(Parser):
    def __init__(self, lexer):
        super(PageFlowParser, self).__init__(lexer, 2)

    def match(self, token_type):
        token = self.next()
        super(PageFlowParser, self).match(token_type)
        return token

    def parse(self):
        return self.pages()

    def pages(self):
        pages = []
        pages.append(self.page())
        self.lb()
        while self.peek(Number):
            pages.append(self.page())
            self.lb()
        return pages

    def page(self):
        head, line, body = self.content()
        return (
            head,
            line,
            body,
            self.interactions()
        )

    def content(self):
        head = self.head()
        line = self.line()
        body = self.body()
        return (head, line, body)

    def lb(self):
        while self.peek(LineBreak):
            self.consume()

    def body(self):
        paragraphs = []
        paragraphs.append(self.text())
        self.lb()
        while self.peek(Text):
            paragraphs.append(self.text())
            self.lb()
        return paragraphs

    def head(self):
        number = self.match(Number)
        text = self.text()
        condition = None
        if self.peek(Condition):
            condition = self.match(Condition)
        self.lb()
        return (number, text, condition)

    def line(self):
        line = self.match(Line)
        self.lb()
        return line

    def text(self):
        return self.match(Text)

    def interactions(self):
        interactions_ = []
        self.lb()
        interactions_.append(self.interaction())
        self.lb()
        if self.peek(Button) or self.peek(Image) or self.peek(Action):
            interactions_.append(self.interaction())
            self.lb()
        return interactions_

    def interaction(self):
        if self.peek(Button):
            return self.match(Button)
        if self.peek(Image):
            return self.match(Image)
        if self.peek(Action):
            return self.match(Action)


def read_file(path):
    with codecs.open(path, 'r', ENCODING) as file_:
        return file_.read()


def read(path):
    file_ = read_file(path)
    lexer = FlowLexer(file_)
    parser = PageFlowParser(lexer)
    return parser.parse()


def write(string, path):
    with codecs.open(path, 'w', ENCODING) as file_:
        file_.write(string)


def to_json(tree):
    obj = dict(data=[
        dict(
            id=number.value,
            caption=head.value.strip(),
            condition=(condition.value if condition else 'page'),
            text=[
                paragraph.value.strip()
                for paragraph
                in text
            ],
            interactions=[
                dict(value=i.value, type=type(i).__name__.lower())
                for i
                in interactions
            ]
        )
        for (number, head, condition), line, text, interactions
        in tree
    ])
    return json.dumps(obj, indent=4, encoding=ENCODING, ensure_ascii=False)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print 'source, target'
        exit()
    source = sys.argv[1]

    tree = read(source)
    obj = to_json(tree)

    if len(sys.argv) == 3:
        target = sys.argv[2]
        write(obj, target)
    else:
        sys.stdout.write(obj)
