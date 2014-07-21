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

    @visit.d(node.Bool)
    def _(self, n):
        n['type'] = node.BoolType()

    @visit.d(node.Val)
    def _(self, n):
        n['type'] = self._declaration(n)

    @visit.d(node.Var)
    def _(self, n):
        n['type'] = self._declaration(n)

    def _declaration(self, n):
        declared_type = self.resolve_type(n.type_)
        value_type = n.value['type']

        final_type = self.infer_check(inferable=declared_type, fixed=value_type)

        if value_type != node.Unit() and final_type == node.UnitType():
            raise TypeError('Cannot assign Unit')

        return final_type

    @visit.d(node.Assign)
    def _(self, n):
        ident = n.name.value
        declaration = n['namespace'][ident]

        declared_type = self._declaration(declaration)
        value_type = n.value['type']

        final_type = self.infer_check(inferable=declared_type, fixed=value_type)

        if final_type == node.UnitType():
            raise TypeError('Cannot assign Unit')

        # propogate type inference back to the declaration.
        if declared_type != final_type:
            declaration.set_hard('type', final_type)

        n['type'] = final_type

    @visit.d(node.ValueId)
    def _(self, n):
        ident = n.value
        declaration = n['namespace'][ident]

        n['type'] = self._declaration(declaration)

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

    @visit.d(node.If)
    def _(self, n):
        pred_type = n.pred['type']
        if_type = n.if_body['type']
        else_type = n.else_body['type']

        # ensure that the predicate is of type Bool
        self.infer_check(inferable=pred_type, fixed=node.BoolType())

        final_type = self.infer_check(inferable=if_type, fixed=else_type)

        n['type'] = final_type

    @visit.d(node.Def)
    def _(self, n):
        n['type'] = self._definition(n)

    def _definition(self, n):
        param_type = n.param['type']
        body_type = n.body['type']

        return_type = self.resolve_type(n.return_type)
        final_type = self.infer_check(inferable=return_type, fixed=body_type)

        return node.FunctionType(
            param_type=param_type,
            return_type=final_type,
        )

    @visit.d(node.Call)
    def _(self, n):
        ident = n.func.value
        definition = n['namespace'][ident]

        n['type'] = self._definition(definition)

    def infer_check(self, inferable, fixed):
        if fixed == node.UnitType():
            return fixed

        elif inferable == node.InferType():
            return fixed

        elif inferable != fixed:
            raise TypeError('Type Mismatch: {0} != {1}'.format(inferable, fixed))

        return fixed

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
