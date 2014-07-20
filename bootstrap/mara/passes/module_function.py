'''
Wrap modules' top-level exprs in an anonymous function.
'''

from ..util.dispatch import method_store, multimethod
from .. import node


class ModuleFunction(object):
    _store = method_store()

    def __init__(self):
        self.definition = None
        self.module = None

    @multimethod(_store)
    def visit(self, n):
        pass

    @visit.d(node.Module)
    def _(self, n):
        self.module = n

        wrapper = node.Def(
            name=node.ValueId(n.name),
            param=node.Tuple([]),
            body=node.Block(exprs=n.exprs),
        )

        call = node.Call(
            func=node.ValueId(n.name),
            arg=node.Tuple([]),
        )

        n.exprs = [
            wrapper,
            call,
        ]
