'''
Mara Language Lexer
'''
import re
from collections import namedtuple
from ply.lex import TOKEN


class Balancer(object):
    def __init__(self):
        self.par = 0
        self.bkt = 0

    def track(self, tok):
        if tok.type == 'LPAR':
            self._openpar()
        if tok.type == 'RPAR':
            self._closepar()
        if tok.type == 'LBKT':
            self._openbkt()
        if tok.type == 'RBKT':
            self._closebkt()

    def _openpar(self):
        self.par += 1

    def _closepar(self):
        self.par -= 1

    def _openbkt(self):
        self.bkt += 1

    def _closebkt(self):
        self.bkt -= 1

    def isopen(self):
        isopen = (
            self.par > 0
            or self.bkt > 0
        )
        return isopen


KEYWORDS = set([
    'match', 'as',
    'if', 'else',
    'for', 'in',
    'while',
    'def', 'val', 'var', 'ref', 'mut',
    'datum', 'trait', 'type',
])

tokens = (
    'MODULE', 'END',
    'TERM',
    'LPAR', 'RPAR',
    'LBKT', 'RBKT',
    'LBRC', 'RBRC',

    'PIPE', 'AMP', 'DOLLAR', 'AT', 'SLASH',
    'COMMA', 'DOT', 'COLON', 'NL',
    'EQ', 'PLUS', 'MINUS', 'TIMES', 'DIVIDE', 'MOD', 'POWER',

    'TCOMMENT', 'DCOMMENT', 'BCOMMENT',

    'VID', 'TID', 'SID',

    'INTD', 'INTX', 'INTP', 'REAL', 'SCI',
) + tuple([kw.upper() for kw in KEYWORDS])

states = (
    ('code', 'exclusive'),
    ('tcomment', 'exclusive'),
    ('dcomment', 'exclusive'),
    ('bcomment', 'exclusive'),
)


def t_MODULE(tok):
    'module'
    tok.lexer.begin('code')
    tok.lexer.marabalancer = Balancer()
    return tok

## Block Comment

def t_code_BCOMMENT(tok):
    r'\#\#\#'
    tok.lexer.push_state('bcomment')

def t_bcomment_END(tok):
    r'\#\#\#'
    tok.lexer.pop_state()

def t_bcomment_BCOMMENT(tok):
    r'((?!\#\#\#)(.|\n|\r))+'
    return tok

def t_bcomment_error(tok):
    return tok

## Doc Comment

def t_code_DCOMMENT(tok):
    r'\#\#'
    tok.lexer.push_state('dcomment')

def t_dcomment_DCOMMENT(tok):
    r'[^\n]+'
    return tok

def t_dcomment_NL(tok):
    r'(\n|\r)+'
    tok.lexer.pop_state()

## Temp Comment

def t_code_TCOMMENT(tok):
    r'\#'
    tok.lexer.push_state('tcomment')

def t_tcomment_TCOMMENT(tok):
    r'[^\n]+'
    return tok

def t_tcomment_NL(tok):
    r'(\n|\r)+'
    tok.lexer.pop_state()

## End Comments

def t_code_END(tok):
    'end'
    tok.lexer.begin('INITIAL')
    return tok

t_code_ignore = ' \t'

def t_error(tok):
    return tok


def t_code_error(tok):
    return tok

# Wrappers
def t_code_LPAR(tok):
    r'\('
    tok.lexer.marabalancer.track(tok)
    return tok

def t_code_RPAR(tok):
    r'\)'
    tok.lexer.marabalancer.track(tok)
    return tok

def t_code_LBKT(tok):
    r'\['
    tok.lexer.marabalancer.track(tok)
    return tok

def t_code_RBKT(tok):
    r'\]'
    tok.lexer.marabalancer.track(tok)
    return tok

def t_code_LBRC(tok):
    r'\{'
    tok.lexer.marabalancer.track(tok)
    return tok

def t_code_RBRC(tok):
    r'\}'
    tok.lexer.marabalancer.track(tok)
    return tok

# Distinct symbols
t_code_EQ = r'='
t_code_PIPE = r'\|'
t_code_AMP = r'\&'
t_code_DOLLAR = r'\$'
t_code_AT = r'@'
t_code_SLASH = r'\\'
t_code_COMMA = r'\,'
t_code_DOT = r'[.]'
t_code_COLON = r'\:'

# Operators
t_code_PLUS = r'[+]'
t_code_MINUS = r'[-]'
t_code_TIMES = r'[*]'
t_code_DIVIDE = r'[/]'
t_code_MOD = r'[%]'
t_code_POWER = r'\^'

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


# --- Identifiers --- ##


def t_code_VID(tok):
    r'(_+[0-9]|_*[a-z])[A-Za-z_0-9]*'

    if tok.value in KEYWORDS:
        tok.type = tok.value.upper()

    return tok


def t_code_TID(tok):
    r'_*[A-Z][A-Za-z_0-9]*'
    return tok

SYMA = r'[~!?<>]'
SYMB = r'[&|%=+\-^*/:]'
SYMC = r'(\{|\[|\(|\\)'
SYM_REGEX = re.compile(r'{A}|{B}|{C}'.format(A=SYMA, B=SYMB, C=SYMC))

@TOKEN(r'{A}+|{B}({A}|{B})+'.format(A=SYMA, B=SYMB))
def t_code_SID(tok):
    return tok

def _after_module(tok):
    data = tok.lexer.lexdata
    pos = tok.lexer.lexpos

    # slide to the beginning of the line
    start = pos - 1
    current = data[start]

    pos = start - 1
    while data[pos] != current and pos > 0:
        pos -= 1

    after_module = ('module' in data[pos:start])
    return after_module


def newline_terminates(tok):
    after_symbol = SYM_REGEX.match(tok.lexer.lexdata[tok.lexer.lexpos - 2])
    after_module = _after_module(tok)

    print tok.lexer.marabalancer.isopen()

    return (
        not after_symbol
        and not tok.lexer.marabalancer.isopen()
        # and not after_module
    )

def t_code_NL(tok):
    r'(\n|\r)+'

    if newline_terminates(tok):
        tok.type = 'TERM'
        tok.value = '\n'
        return tok

def t_code_TERM(tok):
    r';'

    return tok

def lex_tokens(lexer, input):
    '''Lex an input stream, yielding one token at a time.
    '''
    lexer.begin('INITIAL')
    lexer.input(input)
    while True:
        tok = lexer.next()
        if tok is None:
            break
        yield tok

SimpleToken = namedtuple('SimpleToken', ['type', 'value'])

def lex_simple(lexer, input):
    '''Lex an input stream, yielding the a simplified namedtuple
    '''
    for tok in lex_tokens(lexer, input):
        yield SimpleToken(tok.type, tok.value)


def build_lexer():
    import ply.lex as lex
    return lex.lex()
