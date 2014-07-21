from abc import ABCMeta

from util.reflection import deriving
from util.functions import unique_id
import special
import attributes


# pylint: disable=W0231


class Node(deriving('eq', 'show')):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._attrs = attributes.Attributes()
        self._unique_name = None

    @property
    def unique_name(self):
        if self._unique_name is None:
            self._unique_name = unique_id(self.__class__.__name__)
        return self._unique_name

    def walk_down(self, visitor, short_circuit=False):
        visitor.visit(self)
        if short_circuit and visitor.recurse_on(self):
            self.recurse(visitor, Node.walk_down)
        else:
            self.recurse(visitor, Node.walk_down)

    def walk_up(self, visitor, short_circuit=False):
        if short_circuit and visitor.recurse_on(self):
            self.recurse(visitor, Node.walk_up)
        else:
            self.recurse(visitor, Node.walk_up)
        visitor.visit(self)

    def recurse(self, visitor, walk):
        pass

    def __contains__(self, key):
        return self._attrs.__contains__(key)

    def __getitem__(self, key):
        return self._attrs.__getitem__(key)

    def __setitem__(self, key, value):
        self._attrs.__setitem__(key, value)


class Module(Node):

    def __init__(self, name=None, exprs=None):
        Node.__init__(self)

        self.name = name
        self.exprs = exprs

    def recurse(self, visitor, walk):
        for expr in self.exprs:
            walk(expr, visitor)


class NoOp(Node):
    def __init__(self):
        Node.__init__(self)


class _Collection(Node):

    def __init__(self, values=None):
        Node.__init__(self)
        if values is None:
            values = []
        self.values = values

    def recurse(self, visitor, walk):
        for value in self.values:
            walk(value, visitor)


class Tuple(_Collection):
    pass


class List(_Collection):
    pass


class _Value(Node):

    def __init__(self, value):
        Node.__init__(self)
        self.value = value


class Int(_Value):
    pass


class Real(_Value):
    pass


class Sci(_Value):
    pass


class Bool(_Value):
    def __init__(self, value):
        assert value in ('0', '1')
        _Value.__init__(self, value)


class ValueId(_Value):
    pass


class SymbolId(_Value):
    pass


class TypeId(_Value):
    pass


class Unit(Node):

    def __init__(self):
        Node.__init__(self)


class Block(Node):

    def __init__(self, exprs):
        Node.__init__(self)

        self.exprs = exprs

    def recurse(self, visitor, walk):
        for expr in self.exprs:
            walk(expr, visitor)


class BinOp(Node):

    def __init__(self, func, args):
        Node.__init__(self)

        self.func = func
        self.args = args

    def recurse(self, visitor, walk):
        for arg in self.args:
            walk(arg, visitor)


class If(Node):

    def __init__(self, pred, if_body, else_body=None):
        Node.__init__(self)

        self.pred = pred
        self.if_body = if_body

        if else_body is not None:
            self.else_body = else_body
        else:
            self.else_body = Unit()

    def recurse(self, visitor, walk):
        walk(self.pred, visitor)
        walk(self.if_body, visitor)
        walk(self.else_body, visitor)


class Else(Node):

    def __init__(self, expr, body):
        Node.__init__(self)

        self.expr = expr
        self.body = body

    def recurse(self, visitor, walk):
        walk(self.expr, visitor)
        walk(self.body, visitor)


class Assign(Node):

    def __init__(self, name, value, type_=None):
        Node.__init__(self)

        self.name = name
        self.value = value
        self.type_ = type_

    def recurse(self, visitor, walk):
        walk(self.value, visitor)


class AssignRhs(Node):

    def __init__(self, value):
        Node.__init__(self)
        self.value = value

    def recurse(self, visitor, walk):
        walk(self.value, visitor)


class While(Node):

    def __init__(self, pred, body):
        Node.__init__(self)
        self.pred = pred
        self.body = body

    def recurse(self, visitor, walk):
        walk(self.pred, visitor)
        walk(self.body, visitor)


class _Declaration(Node):

    def __init__(self, name, value, type_=None):
        Node.__init__(self)
        self.name = name
        self.value = value

        if type_ is None:
            self.type_ = InferType()
        else:
            self.type_ = type_

    def recurse(self, visitor, walk):
        walk(self.value, visitor)


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
        Node.__init__(self)

        self.clauses = clauses
        self.body = body

    def recurse(self, visitor, walk):
        walk(self.body, visitor)


class ForClause(Node):

    def __init__(self, bind, in_):
        Node.__init__(self)

        self.bind = bind
        self.in_ = in_


class KV(Node):

    def __init__(self, key, value):
        Node.__init__(self)

        self.key = key
        self.value = value

    def recurse(self, visitor, walk):
        walk(self.value, visitor)


class _Comment(Node):

    def __init__(self, content):
        Node.__init__(self)

        self.content = content


class TempComment(_Comment):
    pass


class DocComment(_Comment):
    pass


class BlockComment(_Comment):
    pass


class Call(Node):

    def __init__(self, func, arg, block=None):
        Node.__init__(self)

        self.func = func
        self.arg = arg

        if block is not None:
            self.block = block
        else:
            self.block = Unit()

    def recurse(self, visitor, walk):
        walk(self.arg, visitor)
        walk(self.block, visitor)


class Param(Node):
    def __init__(self, name, type_=None):
        Node.__init__(self)
        self.name = name

        if type_ is None:
            self.type_ = InferType()
        else:
            self.type_ = type_


class Def(Node):

    def __init__(self, name, param, body, return_type=None):
        Node.__init__(self)

        self.name = name
        self.param = param
        self.body = body

        if return_type is not None:
            self.return_type = return_type
        else:
            self.return_type = InferType()

    def recurse(self, visitor, walk):
        walk(self.param, visitor)
        walk(self.body, visitor)


##############################################################################
# Types
##############################################################################


class InferType(Node):
    pass


class IntType(Node):
    pass


class BoolType(Node):
    pass


class RealType(Node):
    pass


class UnitType(Node):
    pass


class AnyType(Node):
    pass


class FunctionType(Node):
    def __init__(self, param_type, return_type):
        self.param_type = param_type
        self.return_type = return_type

    def recurse(self, visitor, walk):
        walk(self.param_type, visitor)
        walk(self.return_type, visitor)
