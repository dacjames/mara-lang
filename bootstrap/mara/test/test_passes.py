# pylint: disable=W0611
# pylint: disable=W0621
# pylint: disable=W0212


import pytest

from .. import node
from .. import special
from .. import passes

from test_lexer import lex_simple
from test_parser import parser, maramodule


@pytest.fixture
def join_else():
    return passes.JoinElse()


def test_join_else(parser, join_else):
    given = maramodule('test', '''
        if x > 0 {}
        else {}
        if x > 1 {}
    ''')

    ast = parser.parse(given)

    ast.walk(join_else)

    expected = node.Module(name='expr', exprs=[
        node.If(
            pred=node.BinOp(func=node.SymbolId('>'), args=[node.ValueId('x'), node.Int('0')]),
            if_body=node.Block([], []),
            else_body=node.Block([], []),
        ),

        node.If(
            pred=node.BinOp(func=node.SymbolId('>'), args=[node.ValueId('x'), node.Int('0')]),
            if_body=node.Block([], []),
            else_body=special.UNIT,
        ),
    ])

    assert expected

