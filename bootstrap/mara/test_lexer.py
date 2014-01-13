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
               ____pZ0x9'''
    output = list(lex_simple(given))
    assert output == [
        ('VID', 'hello'),
        ('VID', '_goodbye'), ('NL', '\n'),
        ('VID', 'pizza_sauce'),
        ('VID', 'num0'), ('NL', '\n'),
        ('VID', '____pZ0x9'),
    ]
