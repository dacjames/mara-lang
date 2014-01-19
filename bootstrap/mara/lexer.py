'''
Mara Language Lexer
'''

from collections import namedtuple

tokens = (
    'MODULE', 'END',
    'LPAR', 'RPAR',
    'LBKT', 'RBKT',
    'LBRC', 'RBRC',

    'PIPE', 'AMP', 'DOLLAR', 'AT', 'SLASH',
    'POUND', 'COMMA', 'DOT', 'NL',
    'VID', 'TID', 'SID',

    'INTD','INTX','INTP','REAL','SCI',
)

states = (
    ('code', 'exclusive'),
)


def t_MODULE(tok):
    'module'
    tok.lexer.begin('code')
    return tok

def t_code_END(tok):
    'end'
    tok.lexer.begin('INITIAL')
    return tok

t_code_ignore = ' \t\r'

def t_error(tok):
    return tok

def t_code_error(tok):
    return tok

# Wrappers
t_code_LPAR = r'\('
t_code_RPAR = r'\)'
t_code_LBKT = r'\['
t_code_RBKT = r'\]'
t_code_LBRC = r'\{'
t_code_RBRC = r'\}'

# Distinct symbols
t_code_PIPE   = r'\|'
t_code_AMP    = r'\&'
t_code_DOLLAR = r'\$'
t_code_AT     = r'@'
t_code_SLASH  = r'\\'
t_code_POUND  = r'\#'
t_code_COMMA  = r'\,'
t_code_DOT    = r'[.]'
t_code_NL     = r'\n'

# Literals
def t_code_SCI(tok):
    r'[-+]?[0-9]+(\.?|\.[0-9]+)e[-+]?[0-9]+(\.|\.[0-9]+)?'
    return tok
def t_code_REAL(tok):
    r'[-+]?[0-9]+([.][0-9]+|[.])'
    return tok
def t_code_INTP(tok):
    r'[-+]?[0-9]+(_[0-9]+)+'
    return tok
def t_code_INTX(tok):
    r'[-+]?0x([0-9]|[A-F]|[a-f])+'
    return tok
def t_code_INTD(tok):
    r'[-+]?[0-9]+'
    return tok

# Identifiers
def t_code_VID(tok):
    r'(_+[0-9]|_*[a-z])[A-Za-z_0-9]*'
    return tok
def t_code_TID(tok):
    r'_*[A-Z][A-Za-z_0-9]*'
    return tok
def t_code_SID(tok):
    r'_*([~!%?<>*/]|\^)+|\&\&|\|\|'
    return tok



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




