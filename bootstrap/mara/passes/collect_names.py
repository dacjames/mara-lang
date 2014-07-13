'''
Collect all of the names within a scope
and attribute them to the containing Block or Module node.
'''

from ..util.dispatch import method_store, multimethod
from .. import node
from .. import scope


class CollectNames(object):
    _store = method_store()

    def __init__(self):
        self.namespace = scope.Root()

    @multimethod(_store)
    def visit(self, n):
        n['namespace'] = self.namespace

    @visit.d(node.Block)
    def _(self, n):
        self.namespace = self.namespace.child()
        n['namespace'] = self.namespace

    @visit.d(node.Module)
    def _(self, n):
        self.namespace = self.namespace.child()
        n['namespace'] = self.namespace

    @visit.d(node.Val)
    def _(self, n):
        ident = n.name.value

        self.namespace.declare(ident, n)
        n['namespace'] = self.namespace

    @visit.d(node.Var)
    def _(self, n):
        ident = n.name.value

        self.namespace.declare(ident, n)
        n['namespace'] = self.namespace

    @visit.d(node.Def)
    def _(self, n):
        ident = n.name.value

        self.namespace.declare(ident, n)
        n['namespace'] = self.namespace

    @visit.d(node.Param)
    def _(self, n):
        ident = n.name.value

        self.namespace.declare(ident, n)
        n['namespace'] = self.namespace
