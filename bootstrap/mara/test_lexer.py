'''
Tests for the Mara Lexer
'''

from lexer import lex_simple


def test_lex_wrappers():
    given = '()[]{}'
    output = list(lex_simple(given))

    assert output == [
        ('LPAR', '('),
        ('RPAR', ')'),
        ('LBKT', '['),
        ('RBKT', ']'),
        ('LBRC', '{'),
        ('RBRC', '}'),
    ]


def test_lex_distinct_symbols():
    given = '@|&$\#,.'
    output = list(lex_simple(given))
    assert output == [
        ('AT', '@'),
        ('PIPE', '|'),
        ('AMP', '&'),
        ('DOLLAR', '$'),
        ('SLASH', '\\'),
        ('POUND', '#'),
        ('COMMA', ','),
        ('DOT', '.'),
    ]


def test_lex_value_identifiers():
    given = '''hello _goodbye
               pizza_sauce num0
               ____pZ0x9 _0'''
    output = list(lex_simple(given))
    assert output == [
        ('VID', 'hello'),
        ('VID', '_goodbye'), ('NL', '\n'),
        ('VID', 'pizza_sauce'),
        ('VID', 'num0'), ('NL', '\n'),
        ('VID', '____pZ0x9'),
        ('VID', '_0'),
    ]

def test_lex_literal_nums():
    given = ('1_000_000 1. 0.9 1231.0 -1 -19.0 +0 -10' +
            ' +3.14e-10 1.2e10 7.8e+10 0xAEF -0x12Aef')
    output = list(lex_simple(given))
    assert output == [
        # ('INTD', '0'),
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
        ('INTX', '0xAEF'),
        ('INTX', '-0x12Aef'),
    ]


