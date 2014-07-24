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
        if 'def_context' not in n and 'spec_context' not in n:
            self.namespace = self.namespace.child(n.unique_name)

        n['namespace'] = self.namespace

    @visit.d(node.Module)
    def _(self, n):
        self.namespace = self.namespace.child(n.unique_name)
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

        n.body['def_context'] = n

        n['namespace'] = self.namespace
        self.namespace = self.namespace.child(n.unique_name)

    @visit.d(node.Param)
    def _(self, n):
        ident = n.name.value

        self.namespace.declare(ident, n)
        n['namespace'] = self.namespace

    @visit.d(node.Object)
    def _(self, n):
        self._visit_spec(n)

    @visit.d(node.Trait)
    def _(self, n):
        self._visit_spec(n)

    @visit.d(node.Proto)
    def _(self, n):
        self._visit_spec(n)

    def _visit_spec(self, n):
        ident = n.name.value

        self.namespace.declare(ident, n)

        n.body['spec_context'] = n

        n['namespace'] = self.namespace
        self.namespace = self.namespace.child(ident)
