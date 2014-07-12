# pylint: disable=W0611
# pylint: disable=W0621
# pylint: disable=W0212


import pytest

from .. import node
from .. import special
from .. import passes
from .. import scope

from test_lexer import lex_simple
from test_parser import parser, maramodule


@pytest.fixture
def join_else():
    return passes.JoinElse()


@pytest.fixture
def collect_names():
    return passes.CollectNames()


@pytest.fixture
def resolve_names():
    return passes.ResolveNames()


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


def test_collect_names(parser, collect_names):
    given = maramodule('test', '''
        val x = 10
        var y

        z = 30
    ''')

    expected = {
        'x': scope.ValBox(node.Val(
            name=node.ValueId('x'),
            value=node.Int('10'),
        )),
        'y': scope.ValBox(node.Val(
            name=node.ValueId('y'),
            value=node.Unit(),
        )),
    }

    ast = parser.parse(given)

    ast.walk(collect_names)

    assert ast['namespace'] == expected


def test_collect_bad_names(parser, collect_names):
    given = maramodule('test', '''
        val x = 10
        val x

        var y
        var y = 5
    ''')

    ast = parser.parse(given)

    with pytest.raises(TypeError):
        ast.walk(collect_names)
