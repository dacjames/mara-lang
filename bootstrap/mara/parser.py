#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Mara Parser
'''
import ply.yacc as yacc

from lexer import tokens  # pylint: disable=W0611
from lexer import KEYWORDS
from lexer import build_lexer, lex_tokens, lex_simple
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
            | definition
            | specification
            | binding
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
               | TRUE
               | FALSE
    '''
    tok = p.slice[1]

    if tok.type in ('INTD', 'INTX', 'INTP'):
        p[0] = node.Int(tok.value)

    elif tok.type == 'REAL':
        p[0] = node.Real(tok.value)

    elif tok.type == 'SCI':
        p[0] = node.Sci(tok.value)

    elif tok.type == 'TRUE':
        p[0] = node.Bool('1')

    elif tok.type == 'FALSE':
        p[0] = node.Bool('0')

    return p[0]


def p_tuple(p):
    '''tuple : full_tuple
             | empty_tuple
    '''
    p[0] = p[1]


def p_empty_tuple(p):
    '''empty_tuple : LPAR RPAR
    '''
    p[0] = node.Tuple([])


def p_full_tuple(p):
    '''full_tuple : LPAR expr_list_comma RPAR
    '''
    p[0] = node.Tuple(p[2])


def p_list(p):
    '''list : LBKT RBKT
            | LBKT expr_list_comma RBKT
    '''
    if len(p) == 3:
        p[0] = node.List([])
    else:
        p[0] = node.List(p[2])


def p_vid(p):
    '''vid : VID
    '''

    p[0] = node.ValueId(p[1])

    return p[0]


def p_tid(p):
    '''tid : TID
    '''

    p[0] = node.TypeId(p[1])

    return p[0]


def p_sid(p):
    '''sid : SID
    '''

    p[0] = node.SymbolId(p[1])

    return p[0]


def p_name(p):
    '''name : vid
            | tid
    '''
    p[0] = p[1]

    return p[0]


def p_if(p):
    '''if : prefix_if
          | postfix_if
    '''

    p[0] = p[1]

    return p[0]

def p_prefix_if(p):
    '''prefix_if : IF expr block
                 | IF block_call
    '''
    # The second rule manually resolves a conflict between if and block calls.
    # expressions like:
    #    if foo(x) { etc }
    # will parse as
    #    if (foo(x) { etc })
    # when we actually want them to parse as
    #    if (foo(x)) { etc }

    if len(p) == 3:
        call = p[2]
        newcall = node.Call(arg=call.arg, func=call.func)
        p[0] = node.If(pred=newcall, if_body=call.block)
    else:
        p[0] = node.If(pred=p[2], if_body=p[3])

    return p[0]


def p_postfix_if(p):
    '''postfix_if : expr IF expr
                  | wrapped IF expr
    '''
    p[0] = node.If(pred=p[3], if_body=p[1])

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
                    | wrapped ELSE expr
    '''
    p[0] = node.Else(body=p[3], expr=p[1])
    return p[0]


def p_ifelse(p):
    '''ifelse : prefix_if prefix_else
    '''
    p[0] = node.If(pred=p[1].pred, if_body=p[1].if_body, else_body=p[2].body)

    return p[0]


def p_while(p):
    '''while : prefix_while
             | postfix_while
    '''
    p[0] = p[1]


def p_prefix_while(p):
    '''prefix_while : WHILE expr block
                    | WHILE block_call
    '''
    # The second rule manually resolves a conflict between while and block calls.
    # expressions like:
    #    while foo(x) { etc }
    # will parse as
    #    while (foo(x) { etc })
    # when we actually want them to parse as
    #    while (foo(x)) { etc }

    if len(p) == 3:
        call = p[2]
        newcall = node.Call(arg=call.arg, func=call.func)
        p[0] = node.While(pred=newcall, body=call.block)
    else:
        p[0] = node.While(pred=p[2], body=p[3])


def p_postfix_while(p):
    '''postfix_while : expr WHILE expr
                     | wrapped WHILE expr
    '''
    p[0] = node.While(pred=p[3], body=p[1])


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
        p[0] = node.Block(exprs=p[2])

    elif len(p) == 3:
        p[0] = node.Block(exprs=[])

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
    '''assign : vid assign_rhs
    '''
    p[0] = node.Assign(name=p[1], value=p[2].value)

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

    return cls(name=p[2], value=value)


def _typed_declaration(cls, p):
    if len(p) == 5:
        value = p[4].value
    else:
        value = node.Unit()

    return cls(name=p[2], value=value, type_=p[3])


def p_val(p):
    '''val : val_untyped
           | val_typed
    '''
    p[0] = p[1]

    return p[0]


def p_val_untyped(p):
    '''val_untyped : VAL vid
                   | VAL vid assign_rhs
    '''
    p[0] = _untyped_declaration(node.Val, p)


def p_val_typed(p):
    '''val_typed : VAL vid tid
                 | VAL vid tid assign_rhs
    '''
    p[0] = _typed_declaration(node.Val, p)


def p_var(p):
    '''var : var_untyped
           | var_typed
    '''
    p[0] = p[1]

    return p[0]


def p_var_untyped(p):
    '''var_untyped : VAR vid
                   | VAR vid assign_rhs
    '''
    p[0] = _untyped_declaration(node.Var, p)

    return p[0]


def p_var_typed(p):
    '''var_typed : VAR vid tid
                 | VAR vid tid assign_rhs
    '''
    p[0] = _typed_declaration(node.Var, p)

    return p[0]


def p_definition(p):
    '''definition : def_abstract
                  | def_concrete
    '''
    p[0] = p[1]

    return p[0]


def p_def_abstract(p):
    '''def_abstract : def_typed
                    | def_untyped
    '''
    definition = p[1]
    definition.body = node.Unit()

    p[0] = definition

def p_def_concrete(p):
    '''def_concrete : def_abstract block
    '''
    definition = p[1]
    definition.body = p[2]

    p[0] = definition

def p_def_typed(p):
    '''def_typed : DEF def_name def_param def_return
    '''
    p[0] = node.Def(
        name=p[2],
        param=p[3],
        body=None,
        return_type=p[4],
    )

    return p[0]


def p_def_untyped(p):
    '''def_untyped : DEF def_name def_param
    '''
    p[0] = node.Def(
        name=p[2],
        param=p[3],
        body=None,
    )


def p_def_name(p):
    '''def_name : tid
                | vid
                | binding
    '''
    p[0] = p[1]


def p_def_param(p):
    '''def_param : empty_tuple
                 | full_param
    '''
    p[0] = p[1]


def p_full_param(p):
    '''full_param : LPAR param_list RPAR
    '''
    p[0] = node.Tuple(values=p[2])


def p_param_list(p):
    '''param_list : param COMMA param_list
                 | param COMMA
                 | param
    '''

    if len(p) == 2:
        p[0] = [p[1]]

    elif len(p) == 3:
        p[0] = [p[1]]

    else:
        p[0] = [p[1]] + p[3]

    return p[0]


def p_def_return(p):
    '''def_return : tid
    '''
    p[0] = p[1]


def p_param(p):
    '''param : untyped_param
             | typed_param
             | bounded_param
    '''
    p[0] = p[1]


def p_typed_param(p):
    '''typed_param : vid tid
    '''
    p[0] = node.Param(name=p[1], type_=p[2])


def p_untyped_param(p):
    '''untyped_param : vid
    '''
    p[0] = node.Param(name=p[1])

def p_bounded_param(p):
    '''bounded_param : tid tid
    '''
    p[0] = node.Param(name=p[1], type_=p[2])


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
    if isinstance(p[2], node.Tuple):
        values = p[2].values
    else:
        values = [p[2]]

    p[0] = node.Call(func=p[1], arg=node.Tuple(values=values))

    return p[0]


def p_postfix_call(p):
    '''postfix_call : expr DOT name
    '''

    if isinstance(p[1], node.Tuple):
        values = p[1].values
    else:
        values = [p[1]]

    p[0] = node.Call(func=p[3], arg=node.Tuple(values=values))

    return p[0]


def p_compound_call(p):
    '''compound_call : postfix_call expr
    '''
    a = p[1]
    b = p[2]

    if isinstance(p[2], node.Tuple):
        arg = node.Tuple(values=p[1].arg.values + p[2].values)
    else:
        arg = node.Tuple(values=p[1].arg.values + [p[2]])

    p[0] = node.Call(func=p[1].func, arg=arg)

    return p[0]


def p_block_call(p):
    '''block_call : blockless_call block
    '''

    call = p[1]
    call.block = p[2]
    p[0] = call

    return p[0]

def p_binding(p):
    '''binding : name BIND name
    '''
    # According to mara semantics, can only bind to a type
    # but we parse bindings to values to aid in error reporting.

    p[0] = node.Binding(left=p[1], right=p[3])

def p_specification(p):
    '''specification : proto
                     | trait
                     | object
    '''
    p[0] = p[1]


def _spec(kind):
    def _p_spec(p):
        p[0] = p[1]

    _p_spec.__doc__ = '''
        {kind} : default_{kind}
               | generic_{kind}
    '''.format(kind=kind)

    _p_spec.__name__ = 'p_{kind}'.format(kind=kind)

    return _p_spec


def _default_spec(rule, terminal, cls):
    def _p_default_spec(p):
        p[0] = cls(name=p[2], body=p[3])

    _p_default_spec.__doc__ = '''{rule} : {terminal} tid block
    '''.format(rule=rule, terminal=terminal)

    _p_default_spec.__name__ = 'p_{rule}'.format(rule=rule)

    return _p_default_spec


def _generic_spec(rule, terminal, cls):
    def _p_generic_spec(p):
        p[0] = cls(name=p[2], body=p[4], param=p[3])

    _p_generic_spec.__doc__ = '''{rule} : {terminal} tid def_param block
    '''.format(rule=rule, terminal=terminal)

    _p_generic_spec.__name__ = 'p_{rule}'.format(rule=rule)

    return _p_generic_spec

p_proto         = _spec('proto')
p_default_proto = _default_spec('default_proto', 'PROTO', node.Proto)
p_generic_proto = _generic_spec('generic_proto', 'PROTO', node.Proto)

p_object            =_spec('object')
p_default_object    = _default_spec('default_object', 'OBJECT', node.Object)
p_generic_object    = _generic_spec('generic_object', 'OBJECT', node.Object)

p_trait         = _spec('trait')
p_default_trait = _default_spec('default_trait', 'TRAIT', node.Trait)
p_generic_trait = _generic_spec('generic_trait', 'TRAIT', node.Trait)


def p_error(tok):
    raise ParseError(tok, tok.lexer)


class Parser(object):
    def __init__(self):
        self._parser = yacc.yacc(tabmodule='__plycache__/parser.out', outputdir='./__plycache__')
        self._lexer = build_lexer()

    def parse(self, document):
        return self._parser.parse(document, lexer=self._lexer)

    def simple_stream(self, document):
        for tok in lex_simple(self._lexer, document):
            yield tok

    def token_stream(self, document):
        for tok in lex_tokens(self._lexer, document):
            yield tok
