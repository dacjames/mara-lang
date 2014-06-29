from abc import ABCMeta

from util.reflection import deriving


# pylint: disable=W0231


class Node(deriving('eq', 'show')):
    __metaclass__ = ABCMeta

    def __init__(self):
        if self.__class__ is Node:
            raise TypeError('Node is abstract and should not be instantiated.')


class Module(Node):

    def __init__(self, name=None, exprs=None):
        self.name = name
        self.exprs = exprs


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


class BinOp(Node):

    def __init__(self, func, args):
        self.func = func
        self.args = args


class If(Node):

    def __init__(self, pred, body):
        self.pred = pred
        self.body = body


class Else(Node):

    def __init__(self, expr, body):
        self.expr = expr
        self.body = body


class Assign(Node):

    def __init__(self, name, value, type_=None):
        self.name = name
        self.value = value
        self.type_ = type_


class AssignRhs(Node):

    def __init__(self, value):
        self.value = value


class While(Node):

    def __init__(self, pred, body):
        self.pred = pred
        self.body = body


class _Declaration(Node):

    def __init__(self, name, value, type_=None):
        self.name = name
        self.value = value
        self.type_ = type_


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


class ForClause(Node):

    def __init__(self, bind, in_):
        self.bind = bind
        self.in_ = in_


class KV(Node):

    def __init__(self, key, value):
        self.key = key
        self.value = value


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

    def __init__(self, func, arg):
        self.func = func
        self.arg = arg
