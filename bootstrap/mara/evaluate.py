'''
Evaluate.py

Impliments a simple, tree-based evaulator.
'''

import node
import scope
import special
from util.dispatch import method_store, multimethod

class Eval(object):
    '''
    Evaluation Visitor
    '''
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
    def visit(self, n):
        '''
        Primary visitor method
        '''
        pass

    @visit.d(node.Int)
    def _(self, n):
        return int(n.value)

    @visit.d(node.Real)
    def _(self, n):
        return float(n.value)

    @visit.d(node.Unit)
    def _(self, n):
        return special.UNIT

    @visit.d(node.BinOp)
    def _(self, n):
        a = self.visit(n.args[0])
        b = self.visit(n.args[1])

        func = n.func.value

        return self._builtins[func](a, b)

    @visit.d(node.Module)
    def _(self, n):
        last = None
        for expr in n.exprs:
            last = self.visit(expr)

        return last

    @visit.d(node.Block)
    def _(self, n):
        last = None
        self.scope = self.scope.child()
        for expr in n.exprs:
            last = self.visit(expr)

        self.scope = self.scope.parent

        return last

    @visit.d(node.Else)
    def _(self, n):
        expr = n.expr
        body = n.body

        value = self.visit(expr)
        if value is not None:
            return value
        else:
            return self.visit(body)

    @visit.d(node.If)
    def _(self, n):
        pred = n.pred
        body = n.body

        if self.visit(pred):
            return self.visit(body)
        else:
            return None

    @visit.d(node.While)
    def _(self, n):
        pred = n.pred
        body = n.body

        while self.visit(pred):
            self.visit(body)

    @visit.d(node.Tuple)
    def _(self, n):
        value = tuple(
            self.visit(value)
            for value in n.values
        )

        return value

    @visit.d(node.Assign)
    def _(self, n):
        ident = n.name.value
        value = self.visit(n.value)

        self.scope.assign(ident, value)
        return value

    @visit.d(node.Val)
    def _(self, n):
        ident = n.name.value

        value = self.visit(n.value)
        self.scope.declare(ident, scope.ValBox(value))

        return value

    @visit.d(node.Var)
    def _(self, n):
        ident = n.name.value
        value = self.visit(n.value)

        self.scope.declare(ident, scope.VarBox(value))
        return value

    @visit.d(node.ValueId)
    def _(self, n):
        ident = n.value
        boxed = self.scope[ident]
        value = boxed.value

        return value
