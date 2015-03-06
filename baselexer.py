# encoding: utf-8
import sys
reload(sys)
sys.setdefaultencoding("utf-8")

import string
EOF = -1

class Lexer(object):
    EOF = -1
    whitespace_no_break = '\x0b\x0c\t '
    german_letters = 'äöüÄÖÜß'
    letters = string.letters + german_letters # a-zA-Z

    def __init__(self, input_file):
        self._input = input_file
        self._input_length = len(self._input)
        self._current_position = 0
        self._current_character = self._input[self._current_position] # prime lookahead

    def consume(self):
        self._current_position += 1
        if self._current_position >= self._input_length:
            self._current_character = EOF
        else:
            self._current_character = self._input[self._current_position]

    def match(self, expected_character):
        if self._current_character == expected_character:
            self.consume()
            return
        raise Exception('Expecting %s but found %s' % (expected_character, self._current_character))

    def is_letter(self, c):
        return c in self.letters

    def is_digit(self, c):
        return c in string.digits

    def is_linebreak(self, c):
        return c in '\r\n'

    def is_space(self, c):
        return c in self.whitespace_no_break