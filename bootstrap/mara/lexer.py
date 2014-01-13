'''
Mara Language Lexer
'''

from collections import namedtuple

tokens = (
    'LPAR', 'RPAR',
    'LBKT', 'RBKT',
    'LBRC', 'RBRC',

    'PIPE', 'AMP', 'DOLLAR', 'AT', 'SLASH',
    'POUND', 'COMMA', 'DOT', 'NL',
    'VID', 'TID', 'SID',
)

t_LPAR = r'\('
t_RPAR = r'\)'
t_LBKT = r'\['
t_RBKT = r'\]'
t_LBRC = r'\{'
t_RBRC = r'\}'

# Distinct symbols

t_PIPE   = r'\|'
t_AMP    = r'\&'
t_DOLLAR = r'\$'
t_AT     = r'@'
t_SLASH  = r'\\'
t_POUND  = r'\#'
t_COMMA  = r'\,'
t_DOT    = r'\.'
t_NL     = r'\n'

t_VID = r'_*[a-z][A-Za-z_0-9]*'
t_TID = r'_*[A-Z][A-Za-z_0-9]*'
t_SID = r'_*([~!%?<>*/+-]|\^)+|\&\&|\|\|'

t_ignore = ' \t\r'

import ply.lex as lex
lexer = lex.lex()

def lex_tokens(input):
    '''
    Lex an input stream, yielding one token at a time.
    '''
    lexer.input(input)
    while True:
        tok = lexer.next()
        if tok is None:
            break
        yield tok

SimpleToken = namedtuple('SimpleToken', ['type', 'value'])

def lex_simple(input):
    '''
    Lex an input stream, yielding the a simplified namedtuple
    '''
    for tok in lex_tokens(input):
        yield SimpleToken(tok.type, tok.value)




