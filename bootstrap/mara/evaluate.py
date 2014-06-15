import functools

from collections import defaultdict

import node
import scope
from util.dispatch import method_store, multimethod


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

        self.root.declare('true', scope.ValBox(True))
        self.root.declare('false', scope.ValBox(False))

    ##########################################################################

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
        self.scope = self.scope.child()
        for expr in node.exprs:
            last = self.visit(expr)

        self.scope = self.scope.parent

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

    @visit.d(node.While)
    def _(self, node):
        pred = node.pred
        body = node.body

        while self.visit(pred):
            self.visit(body)


    @visit.d(node.Tuple)
    def _(self, node):
        value = tuple(
            self.visit(value)
            for value in node.values
        )

        return value

    @visit.d(node.Assign)
    def _(self, node):
        ident = node.name.value
        value = self.visit(node.value)

        self.scope.assign(ident, value)
        return value

    @visit.d(node.Val)
    def _(self, n):
        ident = n.name.value

        value = self.visit(n.value)
        self.scope.declare(ident, scope.ValBox(value))

        return value

    @visit.d(node.Var)
    def _(self, node):
        ident = node.name.value
        value = self.visit(node.value)

        self.scope.declare(ident, scope.VarBox(value))
        return value

    @visit.d(node.ValueId)
    def _(self, node):
        ident = node.value
        boxed = self.scope[ident]
        value = boxed.value

        return value
