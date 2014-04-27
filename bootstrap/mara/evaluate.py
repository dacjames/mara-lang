import functools

from singledispatch import singledispatch
from collections import defaultdict

import node
import scope
from util.dispatch import method_store, multimethod


class Val(object):
    def __init__(self, value):
        self.value = value


class Var(object):
    def __init__(self, value):
        self.value = value


class Eval(object):
    _store = method_store()
    _builtins = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a // b,
        '^': lambda a, b: a ** b,
        '>': lambda a, b: a > b,
        '<': lambda a, b: a < b,
    }

    def __init__(self):
        self.root = scope.Root()
        self.scope = self.root

    @multimethod(_store)
    def visit(self, node):
        pass

    @visit.d(node.Int)
    def _(self, node):
        return int(node.value)

    @visit.d(node.Real)
    def _(self, node):
        return float(node.value)

    @visit.d(node.BinOp)
    def _(self, node):
        a = self.visit(node.args[0])
        b = self.visit(node.args[1])

        func = node.func.value

        return self._builtins[func](a, b)

    @visit.d(node.Module)
    def _(self, node):
        last = None
        for expr in node.exprs:
            last = self.visit(expr)

        return last

    @visit.d(node.Block)
    def _(self, node):
        last = None
        for expr in node.exprs:
            last = self.visit(expr)

        return last


    @visit.d(node.Else)
    def _(self, node):
        expr = node.expr
        body = node.body

        value = self.visit(expr)
        if value is not None:
            return value
        else:
            return self.visit(body)

    @visit.d(node.If)
    def _(self, node):
        pred = node.pred
        body = node.body

        if self.visit(pred):
            return self.visit(body)
        else:
            return None

    @visit.d(node.Tuple)
    def _(self, node):
        value = tuple(
            self.visit(value)
            for value in node.values
        )

        return value

    @multimethod(_store)
    def _assign_to(self, ident, value):
        pass

    @_assign_to.d(Val)
    def _(self, container):
        def inner(value):
            if container.value == ():
                container.value = value
                return value
            else:
                raise TypeError('Cannot reassign initialized val')
        return inner

    @_assign_to.d(Var)
    def _(self, container):
        def inner(value):
            container.value = value
            return value
        return inner


    @visit.d(node.Assign)
    def _(self, node):
        ident = node.name.value
        value = self.visit(node.value)

        self._assign_to(self.scope[ident])(value)
        return value

    @visit.d(node.Val)
    def _(self, node):
        ident = node.name.value
        value = self.visit(node.value)

        self.scope[ident] = Val(value)
        return value

    @visit.d(node.Var)
    def _(self, node):
        ident = node.name.value
        value = self.visit(node.value)

        self.scope[ident] = Var(value)
        return value

    @visit.d(node.ValueId)
    def _(self, node):
        ident = node.value
        boxed = self.scope[ident]
        value = boxed.value

        return value

