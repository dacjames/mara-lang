'''
Compiler.py

Translate AST to Mara Bytecode.
'''

import node
import scope
import special
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
        self.pool = ConstantPool()
        self.functions = {}

        self._result = None

    def result(self, reg=None):
        if reg is None:
            return self._result

        self._result = reg
        return reg

    def compile(self, ast):
        ast.walk(self.pool)
        bytecodes = self.visit(ast)
        bytecodes.append(('halt',))
        return bytecodes

    @multimethod(_store)
    def visit(self, n):
        raise TypeError('Node type {n} not yet supported for compilation'.format(n=n.__class__))

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
        n['result'] = result

        return result

    @visit.d(node.Var)
    def _(self, n):
        result = self.visit(n.value)
        n['result'] = result

        return result

    @visit.d(node.ValueId)
    def _(self, n):
        identifier = n.value

        declaration = n['namespace'][identifier]

        source = declaration['result']

        return source

    @visit.d(node.Def)
    def _(self, n):
        r = self.registry.frame()

    @visit.d(node.Call)
    def _(self, n):
        r = self.registry.frame()

        identifier = n.func.value

        declaration = n['namespace'][identifier]

        function_id = declaration['function_id']

        arg_tuple = declaration.arg
        arg_registers = [self.visit(value) for value in arg_tuple]

        self.block += [
            tuple(['call', function_id] + arg_registers),
            ('copy', r(0), 0),
        ]


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

    @visit.d(node.NoOp)
    def _(self, n):
        r = self.registry.frame()

        self.block += [
            ('load_v', r(0), special.NULL)
        ]

        return r(0)

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


class ConstantPool(object):
    '''
    A pool for holding compile time constants.
    '''

    _store = method_store()

    def __init__(self):
        self._pool = []

    def __getitem__(self, key):
        return self._pool.__getitem__(key)

    @multimethod(_store)
    def visit(self, n):
        pass

    @visit.d(node.Int)
    def _(self, n):
        self._add(n, lambda n: int(n.value))

    @visit.d(node.Real)
    def _(self, n):
        self._add(n, lambda n: float(n.value))

    def _add(self, n, accessor):
        index = len(self._pool)
        value = accessor(n)

        self._pool.append(value)
        n['constant'] = index

