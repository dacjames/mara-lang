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

    'INTD','INTX','INTP','REAL','SCI',
)

# Wrappers
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
t_DOT    = r'[.]'
t_NL     = r'\n'

# Literals
def t_SCI(tok):
    r'[-+]?[0-9]+(\.|\.[0-9]+)e[-+]?[0-9]+(\.|\.[0-9]+)?'
    return tok
def t_REAL(tok):
    r'[-+]?[0-9]+([.][0-9]+|[.])'
    return tok
def t_INTP(tok):
    r'[-+]?[0-9]+(_[0-9]+)+'
    return tok
def t_INTX(tok):
    r'[-+]?0x([0-9]|[A-F]|[a-f])+'
    return tok
def t_INTD(tok):
    r'[-+]?[0-9]+'
    return tok

# Identifiers
def t_VID(tok):
    r'_*[a-z][A-Za-z_0-9]*'
    return tok
def t_TID(tok):
    r'_*[A-Z][A-Za-z_0-9]*'
    return tok
def t_SID(tok):
    r'_*([~!%?<>*/]|\^)+|\&\&|\|\|'
    return tok

t_ignore = ' \t\r'
def t_error(tok):
    return tok

import ply.lex as lex
lexer = lex.lex()

# import ipdb; ipdb.set_trace()


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




