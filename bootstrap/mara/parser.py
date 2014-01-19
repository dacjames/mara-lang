'''
Mara Parser
'''
import ply.yacc as yacc

from lexer import tokens
import node
import util


class ParseError(Exception):
    pass


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
    '''
    p[0] = p[1]


def p_literal(p):
    '''literal : int
               | real
               | sci
    '''
    p[0] = p[1]


def p_int(p):
    '''int  : INTD
            | INTX
            | INTP
    '''
    tok = p.slice[1]
    p[0] = node.Int(tok.value)


def p_real(p):
    '''real : REAL'''
    tok = p.slice[1]
    p[0] = node.Real(tok.value)


def p_sci(p):
    '''sci : SCI'''
    tok = p.slice[1]
    p[0] = node.Real(tok.value)


parser = yacc.yacc()

parser.parse('module test 10 end')
