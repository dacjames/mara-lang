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


@pytest.fixture
def type_check():
    return passes.TypeCheck()


def test_join_else(parser, join_else):
    given = maramodule('test', '''
        if x > 0 {}
        else {}
        if x > 1 {}
    ''')

    ast = parser.parse(given)

    ast.walk_down(join_else)

    expected = node.Module(name='test', exprs=[
        node.If(
            pred=node.BinOp(func=node.SymbolId('>'), args=[node.ValueId('x'), node.Int('0')]),
            if_body=node.Block([]),
            else_body=node.Block([]),
        ),
        node.NoOp(),
        node.If(
            pred=node.BinOp(func=node.SymbolId('>'), args=[node.ValueId('x'), node.Int('1')]),
            if_body=node.Block([]),
            else_body=node.Unit(),
        ),
    ])

    assert ast.exprs[0] == expected.exprs[0]
    assert ast.exprs[1] == expected.exprs[1]
    assert ast.exprs[2] == expected.exprs[2]

    assert ast == expected


def test_join_else_regression(parser, join_else):
    given = maramodule('test', '''
        def foo(x) {
            if x + 1 {
                5
            }
            else {
                10
            }
        }
    ''')

    ast = parser.parse(given)

    ast.walk_down(join_else)

    expected = node.Module(name='test', exprs=[
        node.Def(
            name=node.ValueId('foo'),
            param=node.Tuple([
                node.Param(name=node.ValueId('x'))
            ]),
            body=node.Block(exprs=[
                node.If(
                    pred=node.BinOp(
                        func=node.SymbolId('+'),
                        args=[node.ValueId('x'), node.Int('1')]
                    ),
                    if_body=node.Block([
                        node.Int('5')
                    ]),
                    else_body=node.Block([
                        node.Int('10')
                    ]),
                ),
                node.NoOp(),
            ]),
        ),
    ])

    assert ast.exprs[0].name == expected.exprs[0].name
    assert ast.exprs[0].param == expected.exprs[0].param
    assert ast.exprs[0].body == expected.exprs[0].body
    assert ast.exprs[0] == expected.exprs[0]
    assert ast == expected


def test_collect_names(parser, collect_names):
    given = maramodule('test', '''
        val x = 10
        var y

        z = 30
        def foo (x) {}
    ''')

    expected = {
        'x': node.Val(
            name=node.ValueId('x'),
            value=node.Int('10'),
        ),
        'y': node.Var(
            name=node.ValueId('y'),
            value=node.Unit(),
        ),
        'foo': node.Def(
            name=node.ValueId('foo'),
            param=node.Tuple([node.Param(node.ValueId('x'))]),
            body=node.Block([]),
        ),
    }

    inner = {
        'x': node.Param(name=node.ValueId('x')),
    }

    ast = parser.parse(given)

    ast.walk_down(collect_names)

    assert ast['namespace']['x'] == expected['x']
    assert ast['namespace']['y'] == expected['y']
    assert ast['namespace']['foo'] == expected['foo']

    foo = ast['namespace']['foo']
    inner_result = foo.body['namespace']
    assert inner_result['x'] == inner['x']
    assert inner_result['y'] == expected['y']
    assert inner_result['foo'] == expected['foo']


def test_collect_bad_names(parser, collect_names):
    given = maramodule('test', '''
        val x = 10
        val x

        var y
        var y = 5
    ''')

    ast = parser.parse(given)

    with pytest.raises(TypeError):
        ast.walk_down(collect_names)


def test_type_check_simple(type_check):
    given = node.Def(
        name=node.ValueId('foo'),
        param=node.Tuple([node.Param(node.ValueId('x'))]),
        body=node.Block([
            node.Real('3.5'),
            node.Int('10'),
        ]),
    )

    given.walk_up(type_check)

    assert given['type'] == node.FunctionType(
        param_type=node.Tuple([node.AnyType()]),
        return_type=node.IntType(),
    )
