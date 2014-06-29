#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Mara Parser
'''
import ply.yacc as yacc

from lexer import tokens  # pylint: disable=W0611
from lexer import KEYWORDS
import node
import util

ERROR_WINDOW = 10


class ParseError(Exception):

    def __init__(self, tok, lexer):
        data = lexer.lexdata
        pos = lexer.lexpos

        lex_state_string = (
            data[pos - ERROR_WINDOW: pos] +
            '`' + data[pos] + '`' +
            data[pos + 1: pos + ERROR_WINDOW]
        )

        Exception.__init__(self, (tok, lex_state_string))


precedence = (
    tuple(['right'] + list(KEYWORDS)),
    ('right', 'SID'),
    ('right', 'VID', 'TID'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'TIMES', 'DIVIDE', 'MOD'),
    ('left', 'POWER'),
)


def p_module(p):
    '''module : MODULE TERM expr_list_term END
              | MODULE VID TERM expr_list_term END
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
    '''expr : comment
            | literal
            | tuple
            | list
            | name
            | if
            | else
            | ifelse
            | while
            | binop
            | kv
            | wrapped
            | assign
            | declaration
            | call
    '''

    p[0] = p[1]

    return p[0]


def p_wrapped(p):
    '''wrapped : LPAR expr RPAR
    '''
    p[0] = p[2]

    return p[0]


def p_comment(p):
    '''comment : temp_comment
               | doc_comment
               | block_comment
    '''
    p[0] = p[1]


def _comment(rule, cls, tok):
    # pylint: disable=W0621

    def p_comment(p):
        p[0] = cls(p[1])

    p_comment.__doc__ = '{rule} : {tok}'.format(rule=rule, tok=tok)
    return p_comment

p_temp_comment = _comment('temp_comment', node.TempComment, 'TCOMMENT')
p_doc_comment = _comment('doc_comment', node.DocComment, 'DCOMMENT')
p_block_comment = _comment('block_comment', node.BlockComment, 'BCOMMENT')


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


def p_tuple(p):
    '''tuple : LPAR RPAR
             | LPAR expr_list_comma RPAR
    '''
    if len(p) == 3:
        p[0] = node.Tuple([])
    else:
        p[0] = node.Tuple(p[2])


def p_list(p):
    '''list : LBKT RBKT
            | LBKT expr_list_comma RBKT
    '''
    if len(p) == 3:
        p[0] = node.List([])
    else:
        p[0] = node.List(p[2])


def p_name(p):
    '''name : VID
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
    '''if : prefix_if
          | postfix_if
    '''

    p[0] = p[1]

    return p[0]


def p_prefix_if(p):
    '''prefix_if : IF expr block
    '''
    p[0] = node.If(pred=p[2], body=p[3])

    return p[0]


def p_postfix_if(p):
    '''postfix_if : expr IF expr
    '''
    p[0] = node.If(pred=p[3], body=p[1])

    return p[0]


def p_else(p):
    '''else : prefix_else
            | postfix_else
    '''
    p[0] = p[1]
    return p[0]


def p_prefix_else(p):
    '''prefix_else : ELSE block
    '''
    p[0] = node.Else(body=p[2], expr=None)
    return p[0]


def p_postfix_else(p):
    '''postfix_else : expr ELSE expr
    '''
    p[0] = node.Else(body=p[3], expr=p[1])
    return p[0]


def p_ifelse(p):
    '''ifelse : prefix_if prefix_else
    '''
    p[0] = node.IfElse(pred=p[1].pred, if_body=p[1].body, else_body=p[2].body)

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


def p_kv(p):
    '''kv : expr COLON expr
    '''
    p[0] = node.KV(key=p[1], value=p[3])


def p_block(p):
    '''block : LBRC expr_list_term RBRC
             | LBRC RBRC
    '''

    if len(p) == 4:
        p[0] = node.Block(exprs=p[2], params=[])

    elif len(p) == 3:
        p[0] = node.Block(exprs=[], params=[])

    else:
        raise Exception(len(p))

    return p[0]


def _seperated_expr_list(rule, sep):
    def _expr_list(p):

        if len(p) == 2:
            p[0] = [p[1]]

        elif len(p) == 3:
            p[0] = [p[1]]

        else:
            p[0] = [p[1]] + p[3]

        return p[0]

    _expr_list.__doc__ = '''
        {rule} : expr {sep} {rule}
                  | expr {sep}
                  | expr
        '''.format(rule=rule, sep=sep)

    return _expr_list

p_expr_list_term = _seperated_expr_list('expr_list_term', 'TERM')
p_expr_list_comma = _seperated_expr_list('expr_list_comma', 'COMMA')


def p_assign(p):
    '''assign : VID assign_rhs
    '''
    p[0] = node.Assign(name=node.ValueId(p[1]), value=p[2].value, type_=None)

    return p[0]


def p_assign_rhs(p):
    '''assign_rhs : EQ expr
                  | EQ block
    '''
    p[0] = node.AssignRhs(value=p[2])

    return p[0]


def p_declaration(p):
    '''declaration : val
                   | var
    '''
    p[0] = p[1]
    return p[0]


def _untyped_declaration(cls, p):
    if len(p) == 4:
        value = p[3].value
    else:
        value = node.Unit()

    return cls(name=node.ValueId(p[2]), value=value, type_=None)


def _typed_declaration(cls, p):
    if len(p) == 5:
        value = p[4].value
    else:
        value = node.Unit()

    return cls(name=node.ValueId(p[2]), value=value, type_=node.TypeId(p[3]))


def p_val(p):
    '''val : val_untyped
           | val_typed
    '''
    p[0] = p[1]

    return p[0]


def p_val_untyped(p):
    '''val_untyped : VAL VID
                   | VAL VID assign_rhs
    '''
    p[0] = _untyped_declaration(node.Val, p)


def p_val_typed(p):
    '''val_typed : VAL VID TID
                 | VAL VID TID assign_rhs
    '''
    p[0] = _typed_declaration(node.Val, p)


def p_var(p):
    '''var : var_untyped
           | var_typed
    '''
    p[0] = p[1]

    return p[0]


def p_var_untyped(p):
    '''var_untyped : VAR VID
                   | VAR VID assign_rhs
    '''
    p[0] = _untyped_declaration(node.Var, p)

    return p[0]


def p_var_typed(p):
    '''var_typed : VAR VID TID
                 | VAR VID TID assign_rhs
    '''
    p[0] = _typed_declaration(node.Var, p)

    return p[0]


def p_call(p):
    '''call : blockless_call
            | block_call
    '''
    p[0] = p[1]

    return p[0]


def p_blockless_call(p):
    '''blockless_call : prefix_call
                      | postfix_call
                      | compound_call
    '''
    p[0] = p[1]
    return p[0]


def p_prefix_call(p):
    '''prefix_call : name expr
                   | wrapped expr
    '''
    p[0] = node.Call(func=p[1], arg=p[2])

    return p[0]


def p_postfix_call(p):
    '''postfix_call : expr DOT name
    '''
    p[0] = node.Call(func=p[3], arg=p[1])

    return p[0]


def p_compound_call(p):
    '''compound_call : postfix_call expr
    '''
    if isinstance(p[2], node.Tuple):
        arg = node.Tuple(values=[p[1].arg] + p[2].values)

    else:
        arg = node.Tuple(values=[p[1].arg, p[2]])

    p[0] = node.Call(func=p[1].func, arg=arg)

    return p[0]


def p_block_call(p):
    '''block_call : blockless_call block
    '''

    call = p[1]
    call.block = p[2]
    p[0] = call

    return p[0]


def p_error(tok):
    raise ParseError(tok, tok.lexer)


def build_parser():
    return yacc.yacc(tabmodule='__plycache__/parser.out', outputdir='./__plycache__')
