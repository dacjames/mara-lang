'''
Collect all of the names within a scope
and attribute them to the containing Block or Module node.
'''

from ..util.dispatch import method_store, multimethod
from .. import node


class CollectNames(object):
    _store = method_store()

    @multimethod(_store)
    def visit(self, n):
        pass

    @visit.d(node.Block)
    def _(self, n):
        self.scan(n)

    @visit.d(node.Module)
    def _(self, n):
        self.scan(n)

    def scan(self, n):
        namespace = {}

        for expr in n.exprs:
            try:
                name = expr.name
                namespace[name.value] = expr
            except AttributeError:
                continue

        n.attrs['namespace'] = namespace
