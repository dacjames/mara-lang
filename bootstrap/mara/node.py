from abc import ABCMeta

from util.reflection import deriving
import special
import attributes


# pylint: disable=W0231


class Node(deriving('eq', 'show')):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._attrs = attributes.Attributes()

    def walk(self, visitor):
        visitor.visit(self)
        self.recurse(visitor)

    def recurse(self, visitor):
        pass

    def __getitem__(self, key):
        return self._attrs.__getitem__(key)

    def __setitem__(self, key, value):
        self._attrs.__setitem__(key, value)


class Module(Node):

    def __init__(self, name=None, exprs=None):
        Node.__init__(self)

        self.name = name
        self.exprs = exprs

    def recurse(self, visitor):
        for expr in self.exprs:
            expr.walk(visitor)


class NoOp(Node):
    def __init__(self):
        Node.__init__(self)


class _Collection(Node):

    def __init__(self, values=None):
        Node.__init__(self)
        if values is None:
            values = []
        self.values = values


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

    def __init__(self, exprs, params=None):
        Node.__init__(self)

        self.exprs = exprs

        if params is None:
            self.params = []
        else:
            self.params = params

    def recurse(self, visitor):
        for param in self.params:
            param.walk(visitor)

        for expr in self.exprs:
            expr.walk(visitor)


class BinOp(Node):

    def __init__(self, func, args):
        Node.__init__(self)

        self.func = func
        self.args = args

    def recurse(self, visitor):
        for arg in self.args:
            arg.walk(visitor)


class If(Node):

    def __init__(self, pred, if_body, else_body=None):
        Node.__init__(self)

        self.pred = pred
        self.if_body = if_body

        if else_body is not None:
            self.else_body = else_body
        else:
            self.else_body = Unit()

    def recurse(self, visitor):
        self.pred.walk(visitor)
        self.if_body.walk(visitor)
        self.else_body.walk(visitor)


class Else(Node):

    def __init__(self, expr, body):
        Node.__init__(self)

        self.expr = expr
        self.body = body

    def recurse(self, visitor):
        self.expr.walk(visitor)
        self.body.walk(visitor)


class Assign(Node):

    def __init__(self, name, value, type_=None):
        Node.__init__(self)

        self.name = name
        self.value = value
        self.type_ = type_

    def recurse(self, visitor):
        self.value.walk(visitor)


class AssignRhs(Node):

    def __init__(self, value):
        Node.__init__(self)
        self.value = value

    def recurse(self, visitor):
        self.value.walk(visitor)


class While(Node):

    def __init__(self, pred, body):
        Node.__init__(self)
        self.pred = pred
        self.body = body

    def recurse(self, visitor):
        self.pred.walk(visitor)
        self.body.walk(visitor)


class _Declaration(Node):

    def __init__(self, name, value, type_=None):
        Node.__init__(self)
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
        Node.__init__(self)

        self.clauses = clauses
        self.body = body

    def recurse(self, visitor):
        self.body.walk(visitor)


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

    def recurse(self, visitor):
        self.value.walk(visitor)


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

    def recurse(self, visitor):
        self.arg.walk(visitor)
        self.block.walk(visitor)


class Param(Node):
    def __init__(self, name, index=None, type_=None):
        Node.__init__(self)
        self.name = name
        self.index = index

        if type_ is None:
            self.type_ = Unit()
        else:
            self.type_ = type_


class Def(Node):

    def __init__(self, name, param, body, return_type=None):
        Node.__init__(self)

        body.params = param.values

        self.name = name
        self.param = param
        self.body = body

        if return_type is not None:
            self.return_type = return_type
        else:
            self.return_type = Unit()

    def recurse(self, visitor):
        self.body.walk(visitor)
