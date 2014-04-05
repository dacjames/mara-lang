'''
Tests for the Mara Lexer
'''

import pytest
import lexer as lexer_module

@pytest.fixture
def lex_simple():
    lexer = lexer_module.build_lexer()

    def inner(input):
        return lexer_module.lex_simple(lexer, input)
    return inner



def test_lex_wrappers(lex_simple):
    given = 'module()[]{}end'
    output = list(lex_simple(given))

    assert output == [
        ('MODULE', 'module'),
        ('LPAR', '('),
        ('RPAR', ')'),
        ('LBKT', '['),
        ('RBKT', ']'),
        ('LBRC', '{'),
        ('RBRC', '}'),
        ('END', 'end'),
    ]


def test_lex_distinct_symbols(lex_simple):
    given = 'module @ | & $ \ # , . = + - ^ / * end'
    output = list(lex_simple(given))
    assert output == [
        ('MODULE', 'module'),
        ('AT', '@'),
        ('PIPE', '|'),
        ('AMP', '&'),
        ('DOLLAR', '$'),
        ('SLASH', '\\'),
        ('POUND', '#'),
        ('COMMA', ','),
        ('DOT', '.'),
        ('EQ', '='),
        ('PLUS', '+'),
        ('MINUS', '-'),
        ('POWER', '^'),
        ('DIVIDE', '/'),
        ('TIMES', '*'),
        ('END', 'end'),
    ]


def test_lex_keywords(lex_simple):
    given = '''module
        match as
        if else
        for in
        while
        def val var ref mut
        datum trait type
    end'''

    output = list(lex_simple(given))
    assert output == [
        ('MODULE', 'module'),
        ('TERM', '\n'),
        ('MATCH', 'match'),
        ('AS', 'as'),
        ('TERM', '\n'),
        ('IF', 'if'),
        ('ELSE', 'else'),
        ('TERM', '\n'),
        ('FOR', 'for'),
        ('IN', 'in'),
        ('TERM', '\n'),
        ('WHILE', 'while'),
        ('TERM', '\n'),
        ('DEF', 'def'),
        ('VAL', 'val'),
        ('VAR', 'var'),
        ('REF', 'ref'),
        ('MUT', 'mut'),
        ('TERM', '\n'),
        ('DATUM', 'datum'),
        ('TRAIT', 'trait'),
        ('TYPE', 'type'),
        ('TERM', '\n'),
        ('END', 'end'),
    ]

def test_lex_identifiers(lex_simple):
    given = '''module
        forsight
        hello _goodbye
        pizza_sauce num0
        ____pZ0x9 _0
        < > == =>
        ~! ~~ ~>>
        ??? !
    end'''.replace('\n', ' ')

    output = list(lex_simple(given))
    assert output == [
        ('MODULE', 'module'),
        ('VID', 'forsight'),
        ('VID', 'hello'),
        ('VID', '_goodbye'),
        ('VID', 'pizza_sauce'),
        ('VID', 'num0'),
        ('VID', '____pZ0x9'),
        ('VID', '_0'),
        ('SID', '<'),
        ('SID', '>'),
        ('SID', '=='),
        ('SID', '=>'),
        ('SID', '~!'),
        ('SID', '~~'),
        ('SID', '~>>'),
        ('SID', '???'),
        ('SID', '!'),
        ('END', 'end'),
    ]


def test_lex_literal_nums(lex_simple):
    given = ('module 1_000_000 1. 0.9 1231.0 -1 -19.0 +0 -10' +
             ' +3.14e-10 1.2e10 7.8e+10 1e10 0xAEF -0x12Aef end')
    output = list(lex_simple(given))
    assert output == [
        ('MODULE', 'module'),
        ('INTP', '1_000_000'),
        ('REAL', '1.'),
        ('REAL', '0.9'),
        ('REAL', '1231.0'),
        ('INTD', '-1'),
        ('REAL', '-19.0'),
        ('INTD', '+0'),
        ('INTD', '-10'),
        ('SCI', '+3.14e-10'),
        ('SCI', '1.2e10'),
        ('SCI', '7.8e+10'),
        ('SCI', '1e10'),
        ('INTX', '0xAEF'),
        ('INTX', '-0x12Aef'),
        ('END', 'end'),
    ]

def test_lex_expr_end(lex_simple):
    given = '''module test
x = 10



y +
  5
end'''
    output = list(lex_simple(given))

    assert output == [
        ('MODULE', 'module'),
        ('VID', 'test'),
        ('TERM', '\n'),
        ('VID', 'x'),
        ('EQ', '='),
        ('INTD', '10'),
        ('TERM', '\n'),
        ('VID', 'y'),
        ('PLUS', '+'),
        ('INTD', '5'),
        ('TERM', '\n'),
        ('END', 'end'),
    ]
