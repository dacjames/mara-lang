import functools

from singledispatch import singledispatch
from collections import defaultdict

import node
from util.dispatch import method_store, multimethod

class Eval(object):
    _store = method_store()
    _builtins = {
        '+': lambda a, b: a + b,
        '-': lambda a, b: a - b,
        '*': lambda a, b: a * b,
        '/': lambda a, b: a // b,
        '^': lambda a, b: a ** b,
    }

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
