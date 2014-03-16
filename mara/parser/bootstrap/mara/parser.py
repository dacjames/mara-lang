'''
Mara Parser
'''
import ply.yacc as yacc

from lexer import tokens
import node
import util


class ParseError(Exception):
    pass

precedence = (
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('left', 'POWER'),
)


def p_module(prod):
    '''module : MODULE expr END
              | MODULE VID expr END
    '''
    if len(prod) == 4:
        prod[0] = node.Module(
            name=util.anonymous_name('module'),
            exprs=[prod[2]],
        )
    elif len(prod) == 5:
        prod[0] = node.Module(name=prod[2], exprs=[prod[3]])


def p_expr(p):
    '''expr : literal
            | name
            | if
            | binop
            | block
            | LPAR expr RPAR
    '''
    if p.slice[1].type == 'LPAR':
        p[0] = p[2]
    else:
        p[0] = p[1]



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


def p_if(p):
    '''if : IF expr expr'''
    p[0] = node.If(pred=p[2], body=p[3])


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


def p_block(p):
    '''block : LBRC expr RBRC
    '''
    p[0] = node.Block(exprs=[p[2]])



parser = yacc.yacc()

print parser.parse('module simple if x < 0 {x * 2} end')
