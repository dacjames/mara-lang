'''
Tests for the Mara Lexer
'''

from lexer import lex_simple


def test_lex_wrappers():
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


def test_lex_distinct_symbols():
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


def test_lex_keywords():
    given = '''module
        match as
        if else
        for in
        while
        def val var ref mut
        datum trait type
    end'''.replace('\n', ' ')

    output = list(lex_simple(given))
    assert output == [
        ('MODULE', 'module'),
        ('MATCH', 'match'),
        ('AS', 'as'),
        ('IF', 'if'),
        ('ELSE', 'else'),
        ('FOR', 'for'),
        ('IN', 'in'),
        ('WHILE', 'while'),
        ('DEF', 'def'),
        ('VAL', 'val'),
        ('VAR', 'var'),
        ('REF', 'ref'),
        ('MUT', 'mut'),
        ('DATUM', 'datum'),
        ('TRAIT', 'trait'),
        ('TYPE', 'type'),
        ('END', 'end'),
    ]

def test_lex_identifiers():
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


def test_lex_literal_nums():
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

def test_lex_expr_end():
    given = '''module test
x = 10
y +
  5
'''
    output = list(lex_simple(given))

    assert output == [
        ('MODULE', 'module'),
        ('VID', 'test'),
        ('VID', 'x'),
        ('EQ', '='),
        ('INTD', '10'),
        ('TERM', '\n'),
        ('VID', 'y'),
        ('SID', '+'),
        ('INTD', '5'),
        ('TERM', '\n'),
    ]
