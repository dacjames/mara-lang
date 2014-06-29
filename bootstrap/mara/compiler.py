'''
Compiler.py

Translate AST to Mara Bytecode.
'''

import node
import scope
from machine import NULL
from util.dispatch import method_store, multimethod
from util.reflection import deriving


class CompileError(Exception, deriving('eq', 'show')):
    def __init__(self, msg, *largs, **kwargs):
        self.message = msg.format(*largs, **kwargs)
        super(CompileError, self).__init__(self.message)


class Registry(deriving('show')):
    def __init__(self):
        self.counter = -1
        self.regs = {}

    def __call__(self, i):
        try:
            reg = self.regs[i]
        except KeyError:
            self.counter += 1
            reg = self.regs[i] = self.counter

        return reg

    def next(self):
        self.counter += 1
        return self.counter

    def frame(self):
        return RegistryFrame(parent=self)


class RegistryFrame(deriving('show', 'eq')):
    def __init__(self, parent):
        self.regs = {}
        self.parent = parent

    def __call__(self, i):
        try:
            reg = self.regs[i]
        except KeyError:
            reg = self.regs[i] = self.parent.next()

        return reg


class Compiler(object):
    '''
    Compilation Visitor
    '''

    _store = method_store()
    _builtins = {
        '+': 'add_rr',
        '-': 'sub_rr',
        '*': 'mul_rr',
        '/': 'div_rr',
    }

    def __init__(self):
        self.root = scope.Root()
        self.scope = self.root

        self.block = []
        self.registry = Registry()

        self._result = None

    def result(self, reg=None):
        if reg is None:
            return self._result

        self._result = reg
        return reg

    def compile(self, ast):
        bytecodes = self.visit(ast)
        bytecodes.append(('halt',))
        return bytecodes

    @multimethod(_store)
    def visit(self, n):
        pass

    @visit.d(node.Int)
    def _(self, n):
        r = self.registry.frame()

        self.block += [
            ('load_c', r(0), int(n.value)),
        ]

        return r(0)

    @visit.d(node.Real)
    def _(self, n):
        r = self.registry.frame()

        self.block += [
            ('load_c', r(0), float(n.value)),
        ]

        return r(0)

    @visit.d(node.BinOp)
    def _(self, n):

        r = self.registry.frame()

        func = n.func.value
        left_expr = n.args[0]
        right_expr = n.args[1]

        op = self._builtins.get(func, None)

        if op is None:
            raise CompileError('BinOp {func} is not supported.', func=func)

        left = self.visit(left_expr)
        right = self.visit(right_expr)

        self.block += [
            (op, r(0), left, right),
        ]

        return self.result(r(0))

    @visit.d(node.If)
    def _(self, n):
        pred_expr = n.pred
        body_expr = n.body

        pred = self.visit(pred_expr)
        branch_label = len(self.block)
        self.block += [
            None,  # patch with branch
            None,  # patch with else
            None,  # patch with skip
        ]
        body_label = len(self.block)
        body_result = self.visit(body_expr)

        end_label = len(self.block)

        true_offset = body_label - branch_label
        self.block[branch_label] = ('branch_one', pred, true_offset)
        self.block[branch_label + 1] = ('load_c', body_result, NULL)
        self.block[branch_label + 2] = ('jump_a', end_label)

        return self.result(body_result)

    @visit.d(node.Module)
    def _(self, n):
        exprs = n.exprs

        for expr in exprs:
            self.visit(expr)

        return self.block

    @visit.d(node.Block)
    def _(self, n):
        exprs = n.exprs

        if len(exprs) == 0:
            raise CompileError('Empty Blocks not yet supported.')

        for expr in exprs:
            result = self.visit(expr)

        return self.result(result)
