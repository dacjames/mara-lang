from .. import node

import pytest


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
