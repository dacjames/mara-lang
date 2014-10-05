'''
Compiler.py

Translate AST to Mara Bytecode.
'''

import node
import scope
import special
import constant
from util.dispatch import method_store, multimethod
from util.functions import unique_id
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

        self._unique_name = None

    def __call__(self, i):
        try:
            reg = self.regs[i]
        except KeyError:
            reg = self.regs[i] = self.parent.next()

        return reg

    @property
    def unique_name(self):
        if self._unique_name is None:
            self._unique_name = unique_id('f')

        return self._unique_name

    def label(self, name):
        return '{f}_{n}'.format(f=self.unique_name, n=name)

class Compiler(object):
    '''
    Compilation Visitor
    '''

    _store = method_store()
    _builtins = {
        '+': 'add',
        '-': 'sub',
        '*': 'mul',
        '/': 'div',
        '<': 'lt',
        '<=': 'lte',
        '>': 'gt',
        '>=': 'gte',
        '==': 'eq',
        '!=': 'neq',
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

    def emit(self, *instructions):
        self.block += instructions

    def hole(self):
        index = len(self.block)
        self.block.append(None)
        return index

    def patch(self, index, instruction):
        if self.block[index] != None:
            raise ValueError('Must patch a hole, not ' + str(self.block[index]))
        self.block[index] = instruction

    @multimethod(_store)
    def visit(self, n):
        raise TypeError('Node type {n} not yet supported for compilation'.format(n=n.__class__))

    @visit.d(node.NoOp)
    def _(self, n):
        pass

    @visit.d(node.Int)
    def _(self, n):
        r = self.registry.frame()

        self.emit(
            ('load_c', r(0), n['constant']),
        )

        return r(0)

    @visit.d(node.Bool)
    def _(self, n):
        r = self.registry.frame()

        self.emit(
            ('load_c', r(0), n['constant'])
        )

        return r(0)

    @visit.d(node.Real)
    def _(self, n):
        r = self.registry.frame()

        self.emit(
            ('load_c', r(0), n['constant']),
        )

        return r(0)

    @visit.d(node.Val)
    def _(self, n):
        result = self.visit(n.value)
        index = n['index']

        self.emit(
            ('store_p', result, index),
        )

        return result

    @visit.d(node.Var)
    def _(self, n):
        result = self.visit(n.value)

        index = n['index']

        self.emit(
            ('store_p', result, index)
        )

        return result

    @visit.d(node.ValueId)
    def _(self, n):
        r = self.registry.frame()

        identifier = n.value

        declaration = n['namespace'][identifier]

        index = declaration['index']

        self.emit(
            ('load_p', r(0), index)
        )

        return self.result(r(0))

    @visit.d(node.Assign)
    def _(self, n):
        identifier = n.name.value

        declaration = n['namespace'][identifier]

        index = declaration['index']

        result = self.visit(n.value)

        self.emit(
            ('store_p', result, index)
        )

        return self.result(result)

    @visit.d(node.Param)
    def _(self, n):
        r = self.registry.frame()
        index = n['index']

        self.emit(
            ('load_p', r(0), index),
        )

        return self.result(r(0))

    @visit.d(node.Def)
    def _(self, n):
        r = self.registry.frame()
        l = r.label

        local_variables = n['locals']

        #  +1 for address load, +1 for hole, +1 for label
        address = len(self.block) + 3

        # store the address of the function as the result.
        self.emit(
            ('load_v', r(0), address),
            ('label', l('skip_label')),
            ('jump', l('end')),
        )

        # set attributes
        n['address'] = address
        n['result'] = r(0)

        # reserve space for local variables
        self.emit(
            ('reserve', len(local_variables)),
        )
        save = self.hole()

        # track what registers we use in the function,
        # +1 because register numbers start at 1 (0 is special)
        reg_begin_index = self.registry.counter + 1

        # generate the function body
        ret = self.visit(n.body)

        # record the registers we used
        reg_end_index = self.registry.counter + 1
        local_registers = range(reg_begin_index, reg_end_index)

        # generate the return of the result
        self.emit(
            ('copy', 0, ret),
            tuple(['restore'] + local_registers),
            ('ret',),
            ('label', l('end')),
        )

        # patch in the save
        self.patch(save, tuple(['save'] + local_registers))

        return self.result(r(0))

    @visit.d(node.While)
    def _(self, n):
        r = self.registry.frame()
        l = r.label

        # capture the "top" of the loop
        self.emit(('label', l('begin')))

        # compute the predicate
        pred_result = self.visit(n.pred)

        # generate the skip
        self.emit(('branch_zero', pred_result, l('end')))

        # generate the body
        loop_result = self.visit(n.body)

        # loop
        self.emit(('jump', l('begin')))

        # end of loop
        self.emit(('label', l('end')))

        return self.result(loop_result)

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
        self.emit(
            tuple(['call', address] + arg_registers),
            ('copy', r(0), 0),
        )

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

        self.emit(
            (op, r(0), left, right),
        )

        return self.result(r(0))

    @visit.d(node.If)
    def _(self, n):
        r = self.registry.frame()
        l = r.label

        pred_expr = n.pred
        if_body_expr = n.if_body
        else_body_expr = n.else_body

        pred = self.visit(pred_expr)

        self.emit(('branch_zero', pred, l('else_body')))

        body_result = self.visit(if_body_expr)

        self.emit(
            ('jump', l('if_end')),
            ('label', l('else_body')),
        )

        else_result = self.visit(else_body_expr)

        self.emit(('label', l('if_end')))

        self.emit(
            ('phi', r(0), body_result, else_result)
        )

        return self.result(r(0))

    @visit.d(node.Unit)
    def _(self, n):
        r = self.registry.frame()

        self.emit(
            ('load_v', r(0), special.NULL)
        )

        return self.result(r(0))

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
