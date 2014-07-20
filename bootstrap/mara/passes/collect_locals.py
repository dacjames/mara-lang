'''
Collect all the local variables (including parameters),
attaching them to the containing defintion.
'''

from ..util.dispatch import method_store, multimethod
from .. import node


class CollectLocals(object):
    _store = method_store()

    def __init__(self):
        self.definition = None

    @multimethod(_store)
    def visit(self, n):
        pass

    @visit.d(node.Def)
    def _(self, n):
        self.definition = n

        n['locals'] = {}

    @visit.d(node.Val)
    def _(self, n):
        self._collect(n)

    @visit.d(node.Var)
    def _(self, n):
        self._collect(n)

    @visit.d(node.Param)
    def _(self, n):
        self._collect(n)

    def _collect(self, n):
        ident = n.name.value

        namespace = n['namespace']
        qualified = namespace.qualify(ident)

        locals_ = self.definition['locals']

        n['index'] = len(locals_)

        locals_[qualified] = n
