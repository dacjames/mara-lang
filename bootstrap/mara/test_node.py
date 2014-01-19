import node

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

