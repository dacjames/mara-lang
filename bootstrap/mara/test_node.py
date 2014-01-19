import node


class DummyNode(node.Node):
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c


def test_node_shared_methods():
    dummy = DummyNode('qua', None, 0)
    other = DummyNode('qua', None, 0)

    assert repr(dummy) == "DummyNode(a='qua', b=None, c=0)"
    assert dummy == other

