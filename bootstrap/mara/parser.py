'''
Mara Parser
'''
import ply.yacc as yacc

from lexer import tokens
import node
import util

ERROR_WINDOW = 10

class ParseError(Exception):
    def __init__(self, tok, lexer):
        data = lexer.lexdata
        pos = lexer.lexpos

        lex_state_string = (
            data[pos - ERROR_WINDOW: pos] +
            '<=' + data[pos] +
            data[pos + 1: pos + ERROR_WINDOW]
        )

        Exception.__init__(self, (tok, lex_state_string))


precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('left', 'POWER'),
)


def p_module(p):
    '''module : MODULE TERM expr_list END
              | MODULE VID TERM expr_list END
    '''
    if len(p) == 5:
        p[0] = node.Module(
            name=util.anonymous_name('module'),
            exprs=p[3],
        )
    elif len(p) == 6:
        p[0] = node.Module(name=p[2], exprs=p[4])

    return p[0]

def p_expr(p):
    '''expr : literal
            | name
            | if
            | while
            | binop
            | block
            | LPAR expr RPAR
            | assign
            | declaration
    '''
    if p.slice[1].type == 'LPAR':
        p[0] = p[2]
    else:
        p[0] = p[1]

    return p[0]

def p_literal(p):
    '''literal : INTD
               | INTX
               | INTP
               | REAL
               | SCI
    '''
    tok = p.slice[1]

    if tok.type in ('INTD', 'INTX', 'INTP'):
        p[0] = node.Int(tok.value)

    if tok.type == 'REAL':
        p[0] = node.Real(tok.value)

    if tok.type == 'SCI':
        p[0] = node.Sci(tok.value)

    return p[0]

def p_name(p):
    '''name : VID
            | SID
            | TID
    '''
    tok = p.slice[1]

    if tok.type == 'VID':
        p[0] = node.ValueId(tok.value)

    if tok.type == 'SID':
        p[0] = node.SymbolId(tok.value)

    if tok.type == 'TID':
        p[0] = node.TypeId(tok.value)

    return p[0]

def p_if(p):
    '''if : IF expr block
          | expr IF expr'''

    if p[1] == 'if':
        p[0] = node.If(pred=p[2], body=p[3])
    else:
        p[0] = node.If(pred=p[3], body=p[1])

    return p[0]

def p_while(p):
    '''while : WHILE expr block
             | expr WHILE expr'''

    if p[1] == 'while':
        p[0] = node.While(pred=p[2], body=p[3])
    else:
        p[0] = node.While(pred=p[3], body=p[1])

    return p[0]

def p_binop(p):
    '''binop : expr PLUS expr
             | expr MINUS expr
             | expr TIMES expr
             | expr DIVIDE expr
             | expr MOD expr
             | expr POWER expr
             | expr SID expr
    '''
    func = node.SymbolId(p.slice[2].value)
    p[0] = node.BinOp(func=func, args=[p[1], p[3]])

    return p[0]

def p_block(p):
    '''block : LBRC expr_list RBRC
             | LBRC RBRC
    '''

    if len(p) == 4:
        p[0] = node.Block(exprs=p[2], params=[])

    elif len(p) == 3:
        p[0] = node.Block(exprs=[], params=[])

    else:
        raise Exception(len(p))

    return p[0]

def p_expr_list(p):
    '''expr_list : expr TERM expr_list
                 | expr TERM
                 | expr
    '''
    if len(p) == 2:
        p[0] = [p[1]]

    elif len(p) == 3:
        p[0] = [p[1]]

    else:
        p[0] = [p[1]] + p[3]

    return p[0]

def p_assign(p):
    '''assign : expr EQ expr
              | expr TID EQ expr
    '''
    if len(p) == 4:
        p[0] = node.Assign(name=p[1], value=p[3], type_=None)
        return

    if len(p) == 5:
        p[0] = node.Assign(name=p[1], value=p[4], type_=node.TypeId(p[2]))
        return

    raise ParseError(list(p), len(p))

    return p[0]

def p_declaration(p):
    '''declaration : val
                   | var
    '''
    p[0] = p[1]
    return p[0]

def _declaration(cls, p):

    return cls(name=node.ValueId(p[2]), value=p[3], type_=None)

def p_val(p):
    '''val : VAL VID expr
    '''
    p[0] = _declaration(node.Val, p)

    return p[0]

def p_var(p):
    '''var : VAR VID expr
    '''
    p[0] = _declaration(node.Var, p)


def p_error(tok):
    raise ParseError(tok, tok.lexer)


def build_parser():
    return yacc.yacc()
