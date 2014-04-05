
import util
from abc import ABCMeta, abstractmethod


class Node(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        if self.__class__ is Node:
            raise TypeError('Node is abstract and should not be instantiated.')

    def __eq__(self, other):
        '''Universal equality method based on inspecting the "public fields".
        '''
        canary = object()
        for attr in util.instance_fields(self):

            attribute = getattr(self, attr)
            other_attribute = getattr(other, attr, canary)
            equal = (other_attribute is not canary and attribute == other_attribute)

            if not equal:
                return False
        return True

    def __repr__(self):
        '''Universal representation of the node based on inspecting the name
        and "public fields".
        '''
        fields = [
            (attr, repr(getattr(self, attr)))
            for attr in util.instance_fields(self)
        ]

        field_str = ', '.join([
            '{name}={value}'.format(name=name, value=value) for
            (name, value) in fields
        ])
        return '{cls}({fields})'.format(
            cls=self.__class__.__name__,
            fields=field_str,
        )

    def visit(self, visitor):
        return visitor(self)


class Module(Node):
    def __init__(self, name=None, exprs=None):
        self.name = name
        self.exprs = exprs

class _Collection(Node):
    def __init__(self, values=[]):
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


class Assign(Node):
    def __init__(self, name, value, type_=None):
        self.name = name
        self.value = value
        self.type_ = type_


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


class For(Node):
    def __init__(self, clauses, body):
        self.clauses = clauses
        self.body = body


class ForClause(Node):
    def __init__(self, bind, in_):
        self.bind = bind
        self.in_ = in_

