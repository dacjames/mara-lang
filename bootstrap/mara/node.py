
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


class Module(Node):
    def __init__(self, name=None, exprs=None):
        self.name = name
        self.exprs = exprs


class Tuple(Node):
    def __init__(self, values=[]):
        self.values = values


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
    def __init__(self, exprs):
        self.exprs = exprs


class BinOp(Node):
    def __init__(self, func, args):
        self.func = func
        self.args = args


class If(Node):
    def __init__(self, pred, body):
        self.pred = pred
        self.body = body

class Assign(Node):
    def __init__(self, name, value):
        self.name = name
        self.value = value
