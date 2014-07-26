'''
Tests for the Mara Lexer
'''

import pytest
from .. import lexer as lexer_module

# pylint: disable=W0621


@pytest.fixture
def lex_simple():
    lexer = lexer_module.build_lexer()

    def inner(input_stream):
        return lexer_module.lex_simple(lexer, input_stream)
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
    given = r'module @ | & $ \ , . = + - ^ / * : :: end'
    output = list(lex_simple(given))
    assert output == [
        ('MODULE', 'module'),
        ('AT', '@'),
        ('PIPE', '|'),
        ('AMP', '&'),
        ('DOLLAR', '$'),
        ('SLASH', '\\'),
        ('COMMA', ','),
        ('DOT', '.'),
        ('EQ', '='),
        ('PLUS', '+'),
        ('MINUS', '-'),
        ('POWER', '^'),
        ('DIVIDE', '/'),
        ('TIMES', '*'),
        ('COLON', ':'),
        ('BIND', '::'),
        ('END', 'end'),
    ]


def test_lex_keywords(lex_simple):
    given = '''module
        match as
        if else
        for in
        while
        def val var let
        object trait proto
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
        ('LET', 'let'),
        ('TERM', '\n'),
        ('OBJECT', 'object'),
        ('TRAIT', 'trait'),
        ('PROTO', 'proto'),
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


def test_lex_literal_nums_and_bools(lex_simple):
    given = ('module 1_000_000 1. 0.9 1231.0 -1 -19.0 +0 -10' +
             ' +3.14e-10 1.2e10 7.8e+10 1e10 0xAEF -0x12Aef true false end')
    output = list(lex_simple(given))
    assert output == [
        ('MODULE', 'module'),
        ('INTP', '1_000_000'),
        ('INTD', '1'),
        ('DOT', '.'),
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
        ('TRUE', 'true'),
        ('FALSE', 'false'),
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
        ('TERM', '\n\n\n\n'),
        ('VID', 'y'),
        ('PLUS', '+'),
        ('INTD', '5'),
        ('TERM', '\n'),
        ('END', 'end'),
    ]


def test_open_state(lex_simple):
    given = '''module test
        [
            x +
            y
            z
        ]
        (
            x +
            y
            z
        )
        {
            x +
            y
            z
        }
    '''

    expected = [
        ('MODULE', 'module'),
        ('VID', 'test'),
        ('TERM', '\n'),

        ('LBKT', '['),
        ('VID', 'x'),
        ('PLUS', '+'),
        ('VID', 'y'),
        ('VID', 'z'),
        ('RBKT', ']'),
        ('TERM', '\n'),

        ('LPAR', '('),
        ('VID', 'x'),
        ('PLUS', '+'),
        ('VID', 'y'),
        ('VID', 'z'),
        ('RPAR', ')'),
        ('TERM', '\n'),

        ('LBRC', '{'),
        ('VID', 'x'),
        ('PLUS', '+'),
        ('VID', 'y'),
        ('TERM', '\n'),
        ('VID', 'z'),
        ('TERM', '\n'),
        ('RBRC', '}'),
        ('TERM', '\n'),
    ]

    result = list(lex_simple(given))

    assert result == expected


def test_lex_comments(lex_simple):
    given = '''module test
    x
    # asdf
    ## asdf
    ###
    asdf
    qwerty
    ###
    '''

    expected = [
        ('MODULE', 'module'),
        ('VID', 'test'),
        ('TERM', '\n'),
        ('VID', 'x'),
        ('TERM', '\n'),
        ('TCOMMENT', ' asdf'),
        ('TERM', '\n'),
        ('DCOMMENT', ' asdf'),
        ('TERM', '\n'),
        ('BCOMMENT', '\n    asdf\n    qwerty\n    '),
        ('TERM', '\n'),
    ]

    result = list(lex_simple(given))

    assert result == expected


def test_control_with_empty(lex_simple):
    given = '''module test
    if x {

        10


    }
    '''

    expected = [
        ('MODULE', 'module'),
        ('VID', 'test'),
        ('TERM', '\n'),
        ('IF', 'if'),
        ('VID', 'x'),
        ('LBRC', '{'),
        ('INTD', '10'),
        ('TERM', '\n\n\n'),
        ('RBRC', '}'),
        ('TERM', '\n'),
    ]

    result = list(lex_simple(given))

    assert result == expected
