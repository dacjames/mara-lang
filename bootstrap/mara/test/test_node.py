from .. import node

import pytest

from ..util.dispatch import method_store, multimethod
from .. import special


class DummyNode(node.Node):

    def __init__(self, a, b, c):
        node.Node.__init__(self)

        self.a = a
        self.b = b
        self.c = c


def test_node_shared_methods():
    dummy = DummyNode('qua', None, 0)
    other = DummyNode('qua', None, 0)

    assert repr(dummy) == "DummyNode(a='qua', b=None, c=0)"
    assert dummy == other
    assert dummy._attrs


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


def test_node_attributes():
    # pylint: disable=W0212
    # pylint: disable=W0104

    given = node.Module(name='test', exprs=[])

    with pytest.raises(KeyError):
        given['foo']

    given['foo'] = 0
    assert given['foo'] == 0

    with pytest.raises(KeyError):
        given['foo'] = 0

    given['qua/bar'] = 0
    assert given['qua/bar'] == 0
    assert given['qua']['bar'] == 0

    given.set_soft('foo', 0)

    with pytest.raises(KeyError):
        given.set_soft('foo', 1)

    given.set_hard('foo', 1)

    assert given._attrs['foo'] == 1


class SpyVisitor(object):
    _store = method_store()

    def __init__(self):
        self.nodes = []

    def validate(self, node_names):

        expected_classes = [
            getattr(node, name)
            for name in node_names
        ]

        result_classes = [
            n.__class__
            for n in self.nodes
        ]

        for cls in result_classes:
            print cls

        assert result_classes == expected_classes

    @multimethod(_store)
    def visit(self, n):
        self.nodes.append(n)


@pytest.fixture
def spy():
    return SpyVisitor()


def test_walk_down(spy):
    given = node.Module(name='test', exprs=[
        node.Int('10'),
        node.Val(
            name=node.ValueId('x'),
            value=node.Block(exprs=[
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
            ),
            else_body=node.Unit(),
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
        'Unit',
    ]

    given.walk_down(spy)

    spy.validate(expected)


def test_walk_up(spy):
    given = node.Module(name='test', exprs=[
        node.Int('10'),
        node.Val(
            name=node.ValueId('x'),
            value=node.Block(exprs=[
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
            ),
            else_body=node.Unit(),
        ),
    ])

    expected = [
        'Int',
        'ValueId',
        'TypeId',
        'Block',
        'Val',
        'Int',
        'Real',
        'BinOp',
        'Int',
        'KV',
        'Assign',
        'Unit',
        'If',
        'Module',
    ]

    given.walk_up(spy)

    spy.validate(expected)
