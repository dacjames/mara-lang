'''
Compiler.py

Translate AST to Mara Bytecode.
'''

import node
import scope
import special
import constant
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
        self.functions = {}
        self.pool = None

        self._result = None

    def result(self, reg=None):
        if reg is None:
            return self._result

        self._result = reg
        return reg

    def compile(self, ast, pool):
        self.pool = pool
        try:
            bytecodes = self.visit(ast)
        except CompileError:
            for code in self.block:
                print code
            raise
        bytecodes.append(('halt',))
        return bytecodes

    @multimethod(_store)
    def visit(self, n):
        raise TypeError('Node type {n} not yet supported for compilation'.format(n=n.__class__))

    @visit.d(node.NoOp)
    def _(self, n):
        pass

    @visit.d(node.Int)
    def _(self, n):
        r = self.registry.frame()

        self.block += [
            ('load_c', r(0), n['constant']),
        ]

        return r(0)

    @visit.d(node.Real)
    def _(self, n):
        r = self.registry.frame()

        self.block += [
            ('load_c', r(0), n['constant']),
        ]

        return r(0)

    @visit.d(node.Val)
    def _(self, n):
        result = self.visit(n.value)
        index = n['index']

        self.block += [
            ('store_p', result, index),
        ]

        return result

    @visit.d(node.Var)
    def _(self, n):
        result = self.visit(n.value)

        index = n['index']

        self.block += [
            ('store_p', result, index)
        ]

        return result

    @visit.d(node.ValueId)
    def _(self, n):
        r = self.registry.frame()

        identifier = n.value

        declaration = n['namespace'][identifier]

        index = declaration['index']

        self.block += [
            ('load_p', r(0), index)
        ]

        return self.result(r(0))

    @visit.d(node.Assign)
    def _(self, n):
        identifier = n.name.value

        declaration = n['namespace'][identifier]

        index = declaration['index']

        result = self.visit(n.value)

        self.block += [
            ('store_p', result, index)
        ]

        return self.result(result)

    @visit.d(node.Param)
    def _(self, n):
        r = self.registry.frame()
        index = n['index']

        self.block += [
            ('load_p', r(0), index),
        ]

        return self.result(r(0))

    @visit.d(node.Def)
    def _(self, n):
        r = self.registry.frame()

        local_variables = n['locals']

        #  +1 for address load, +1 for hole
        address = len(self.block) + 2

        # store the address of the function as the result.
        self.block += [
            ('load_v', r(0), address),
            None,  # patch with skip
        ]
        skip_label = len(self.block) - 1

        # set attributes
        n['address'] = address
        n['result'] = r(0)

        # reserve space for local variables
        self.block += [
            ('reserve', len(local_variables)),
        ]

        # generate loads for all the function params
        for param in n.param.values:
            self.visit(param)

        # generate the function body
        ret = self.visit(n.body)

        # generate the return of the result
        self.block += [
            ('copy', 0, ret),
            ('ret',),
        ]
        end_label = len(self.block)

        # skip past the declaration
        self.block[skip_label] = ('jump_a', end_label)

        return self.result(r(0))

    @visit.d(node.Call)
    def _(self, n):
        r = self.registry.frame()

        identifier = n.func.value

        # lookup the function's declaration
        declaration = n['namespace'][identifier]

        # lookup the address of the function body
        address = declaration['address']

        # generate evaluations of all the arguments
        arg_registers = [
            self.visit(value)
            for value in n.arg.values
        ]

        # generate the call
        self.block += [
            tuple(['call', address] + arg_registers),
            ('copy', r(0), 0),
        ]

        return self.result(r(0))


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
        r = self.registry.frame()

        pred_expr = n.pred
        if_body_expr = n.if_body
        else_body_expr = n.else_body

        pred = self.visit(pred_expr)
        branch_label = len(self.block)
        self.block += [
            None,  # patch with branch
        ]

        body_result = self.visit(if_body_expr)

        skip_label = len(self.block)
        self.block += [
            None,  # patch with skip
        ]

        else_label = len(self.block)
        else_result = self.visit(else_body_expr)

        end_label = len(self.block)

        else_offset = else_label - branch_label
        self.block[branch_label] = ('branch_zero', pred, else_offset)
        self.block[skip_label] = ('jump_a', end_label)

        self.block += [
            ('phi', r(0), body_result, else_result)
        ]

        return self.result(r(0))

    @visit.d(node.Unit)
    def _(self, n):
        r = self.registry.frame()

        self.block += [
            ('load_v', r(0), special.NULL)
        ]

        return self.result(r(0))

    @visit.d(node.Module)
    def _(self, n):
        exprs = n.exprs

        local_variables = n['locals']

        self.block += [
            ('reserve', len(local_variables))
        ]

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
