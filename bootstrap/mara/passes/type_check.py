'''
Perform type checking.
'''

from ..util.dispatch import method_store, multimethod
from .. import node


class TypeCheck(object):
    _store = method_store()

    def __init__(self):
        self._builtin_types = {
            'Int': node.IntType(),
            'Real': node.RealType(),
            'Bool': node.BoolType(),
        }

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
        if n.type_ == node.InferType():
            n['type'] = node.AnyType()
        else:
            raise NotImplementedError(n)

    @visit.d(node.Unit)
    def _(self, n):
        n['type'] = node.UnitType()

    @visit.d(node.Def)
    def _(self, n):
        param_type = n.param['type']
        body_type = n.body['type']

        return_type = self.resolve_type(n.return_type)

        if return_type == node.InferType():
            return_type = body_type

        elif body_type != return_type:
            raise TypeError('Type Mismatch: {0} != {1}'.format(body_type, return_type))

        n['type'] = node.FunctionType(
            param_type=param_type,
            return_type=return_type,
        )

    @multimethod(_store)
    def resolve_type(self, n):
        raise TypeError(n)

    @resolve_type.d(node.InferType)
    def _(self, n):
        return n

    @resolve_type.d(node.TypeId)
    def _(self, n):
        name = n.value
        if name in self._builtin_types:
            return self._builtin_types[name]
        else:
            raise TypeError(name)
