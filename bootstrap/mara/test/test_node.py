from .. import node

import pytest

from ..util.dispatch import method_store, multimethod
from ..import special


class DummyNode(node.Node):

    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c


class NoInitNode(node.Node):
    pass


def test_node_shared_methods():
    dummy = DummyNode('qua', None, 0)
    other = DummyNode('qua', None, 0)

    with pytest.raises(TypeError):
        assert node.Node()

    assert NoInitNode()

    assert repr(dummy) == "DummyNode(a='qua', b=None, c=0)"
    assert dummy == other


def test_compoment_equality():
    assert node.ValueId(value='x') == node.ValueId(value='x')
    assert node.Int(value='1') == node.Int(value='1')
    assert ([node.ValueId(value='x'), node.Int(value='1')] ==
            [node.ValueId(value='x'), node.Int(value='1')])
    assert node.SymbolId(value='*') == node.SymbolId(value='*')

    a = node.BinOp(
        args=[node.ValueId(value='x'), node.Int(value='1')],
        func=node.SymbolId(value='*')
    )
    b = node.BinOp(
        args=[node.ValueId(value='x'), node.Int(value='1')],
        func=node.SymbolId(value='*')
    )
    assert a == b


def test_complex_equality():
    a = node.Module(
        exprs=[
            node.BinOp(
                args=[node.ValueId(value='x'), node.Int(value='1')],
                func=node.SymbolId(value='*')
            )
        ],
        name='_anon_module_0'
    )

    b = node.Module(
        exprs=[
            node.BinOp(
                args=[node.ValueId(value='x'), node.Int(value='1')],
                func=node.SymbolId(value='*')
            )
        ],
        name='_anon_module_0'
    )

    assert a == b


class SpyVisitor(object):
    _store = method_store()

    def __init__(self):
        self.nodes = []

    def validate(self, node_names):
        global node

        expected_classes = [
            getattr(node, name)
            for name in node_names
        ]

        result_classes = [
            node.__class__
            for node in self.nodes
        ]

        assert result_classes == expected_classes

    @multimethod(_store)
    def visit(self, n):
        self.nodes.append(n)


@pytest.fixture
def spy():
    return SpyVisitor()


def test_walk(spy):
    given = node.Module(name='test', exprs=[
        node.Int('10'),
        node.Val(
            name=node.ValueId('x'),
            value=node.Block(params=[], exprs=[
                node.ValueId('x'),
                node.TypeId('T'),
            ])
        ),
        node.If(
            pred=node.BinOp(func='<', args=[
                node.Int('0'),
                node.Real('1.0'),
            ]),
            if_body=node.Assign(
                name=node.ValueId('x'),
                value=node.KV(
                    key='z',
                    value=node.Int('10')
                ),
                type_=special.UNIT,
            )
        ),
    ])

    expected = [
        'Module',
        'Int',
        'Val',
        'Block',
        'ValueId',
        'TypeId',
        'If',
        'BinOp',
        'Int',
        'Real',
        'Assign',
        'KV',
        'Int',
        'NoOp',
    ]

    given.walk(spy)

    spy.validate(expected)

