'''
Perform type checking.
'''

from ..util.dispatch import method_store, multimethod
from .. import node


class TypeCheck(object):
    _store = method_store()

    @multimethod(_store)
    def visit(self, n):
        pass

    @visit.d(node.Int)
    def _(self, n):
        n['type'] = node.IntType()

    @visit.d(node.Real)
    def _(self, n):
        n['type'] = node.RealType()

    @visit.d(node.Block)
    def _(self, n):
        if len(n.exprs) == 0:
            n['type'] = node.UnitType()

        else:
            n['type'] = n.exprs[-1]['type']

    @visit.d(node.Tuple)
    def _(self, n):
        n['type'] = node.Tuple([
            value['type']
            for value in n.values
        ])

    @visit.d(node.Param)
    def _(self, n):
        if n.type_ == node.Unit():
            n['type'] = node.AnyType()
        else:
            raise NotImplementedError(n)

    @visit.d(node.Unit)
    def _(self, n):
        n['type'] = node.UnitType()

    @visit.d(node.Def)
    def _(self, n):
        param_type = n.param['type']
        return_type = n.body['type']

        n['type'] = node.FunctionType(
            param_type=param_type,
            return_type=return_type,
        )
