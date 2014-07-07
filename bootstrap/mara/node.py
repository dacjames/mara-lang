from abc import ABCMeta

from util.reflection import deriving
import special


# pylint: disable=W0231


class Node(deriving('eq', 'show')):
    __metaclass__ = ABCMeta

    def __init__(self):
        if self.__class__ is Node:
            raise TypeError('Node is abstract and should not be instantiated.')

    def walk(self, visitor):
        visitor.visit(self)
        self.recurse(visitor)

    def recurse(self, visitor):
        pass


class Module(Node):

    def __init__(self, name=None, exprs=None):
        self.name = name
        self.exprs = exprs

    def recurse(self, visitor):
        for expr in self.exprs:
            expr.walk(visitor)


class NoOp(Node):
    def __init__(self):
        pass


class _Collection(Node):

    def __init__(self, values=None):
        if values is None:
            values = []
        self.values = values


class Tuple(_Collection):
    pass


class List(_Collection):
    pass


class _Value(Node):

    def __init__(self, value):
        self.value = value


class Int(_Value):
    pass


class Real(_Value):
    pass


class Sci(_Value):
    pass


class ValueId(_Value):
    pass


class SymbolId(_Value):
    pass


class TypeId(_Value):
    pass


class Unit(Node):
    pass


class Block(Node):

    def __init__(self, exprs, params):
        self.exprs = exprs
        self.params = params

    def recurse(self, visitor):
        for expr in self.exprs:
            expr.walk(visitor)


class BinOp(Node):

    def __init__(self, func, args):
        self.func = func
        self.args = args

    def recurse(self, visitor):
        for arg in self.args:
            arg.walk(visitor)


class If(Node):

    def __init__(self, pred, body, else_body=special.UNIT):
        self.pred = pred
        self.body = body
        self.else_body = else_body

    def recurse(self, visitor):
        self.pred.walk(visitor)
        self.body.walk(visitor)


class Else(Node):

    def __init__(self, expr, body):
        self.expr = expr
        self.body = body

    def recurse(self, visitor):
        self.expr.walk(visitor)
        self.body.walk(visitor)


# class IfElse(Node):

#     def __init__(self, pred, if_body, else_body):
#         self.pred = pred
#         self.if_body = if_body
#         self.else_body = else_body

#     def recurse(self, visitor):
#         self.pred.walk(visitor)
#         self.if_body.walk(visitor)
#         self.else_body.walk(visitor)


class Assign(Node):

    def __init__(self, name, value, type_=None):
        self.name = name
        self.value = value
        self.type_ = type_

    def recurse(self, visitor):
        self.value.walk(visitor)


class AssignRhs(Node):

    def __init__(self, value):
        self.value = value

    def recurse(self, visitor):
        self.value.walk(visitor)


class While(Node):

    def __init__(self, pred, body):
        self.pred = pred
        self.body = body

    def recurse(self, visitor):
        self.pred.walk(visitor)
        self.body.walk(visitor)


class _Declaration(Node):

    def __init__(self, name, value, type_=None):
        self.name = name
        self.value = value
        self.type_ = type_

    def recurse(self, visitor):
        self.value.walk(visitor)


class Val(_Declaration):
    pass


class Var(_Declaration):
    pass


class Mut(_Declaration):
    pass


class Ref(_Declaration):
    pass


class For(Node):

    def __init__(self, clauses, body):
        self.clauses = clauses
        self.body = body

    def recurse(self, visitor):
        self.body.walk(visitor)


class ForClause(Node):

    def __init__(self, bind, in_):
        self.bind = bind
        self.in_ = in_


class KV(Node):

    def __init__(self, key, value):
        self.key = key
        self.value = value

    def recurse(self, visitor):
        self.value.walk(visitor)


class _Comment(Node):

    def __init__(self, content):
        self.content = content


class TempComment(_Comment):
    pass


class DocComment(_Comment):
    pass


class BlockComment(_Comment):
    pass


class Call(Node):

    def __init__(self, func, arg, block=special.UNIT):
        self.func = func
        self.arg = arg
        self.block = block

    def recurse(self, visitor):
        self.arg.walk(visitor)
        self.block.walk(visitor)


class Def(Node):

    def __init__(self, name, param, body, return_type=special.UNIT):
        self.name = name
        self.param = param
        self.body = body
        self.return_type = return_type

    def recurse(self, visitor):
        self.body.walk(visitor)
