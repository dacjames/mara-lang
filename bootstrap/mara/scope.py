#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Scope Objects
'''

from util.dispatch import method_store, multimethod
from util.reflection import deriving
import special
import node


# class ScopeBox(deriving('eq', 'show')):
#     def __init__(self, value):
#         self.value = value

#     def unbox(self):
#         return self.value


# # class ValBox(ScopeBox):
# #     pass


# # class VarBox(ScopeBox):
# #     pass


# # class DefBox(ScopeBox):
# #     pass


# # class ParamBox(ScopeBox):
# #     pass


class _Scope(deriving('members_dict')):
    _store = method_store()

    def __init__(self):
        self.members = {}

    def __getitem__(self, key):
        return self.members.__getitem__(key)

    def __contains__(self, key):
        return self.has_key(key)  # noqa

    def keys(self):
        return self.members.keys()

    def values(self):
        return self.members.values()

    def items(self):
        return self.members.items()

    def has_key(self, key):
        # pylint: disable=E1101
        return self.members.has_key(key)  # noqa

    def get(self, key, default=None):
        return self.members.get(key, default)

    def clear(self):
        return self.members.clear()

    def setdefault(self, default):
        return self.members.setdefault(default)

    def iterkeys(self):
        # pylint: disable=E1101
        return self.members.iterkeys()

    def itervalues(self):
        # pylint: disable=E1101
        return self.members.itervalues()

    def iteritems(self):
        # pylint: disable=E1101
        return self.members.iteritems()

    def pop(self):
        return self.members.pop()

    def popitem(self):
        return self.members.popitem()

    def copy(self):
        return self.members.copy()

    ##########################################################################

    def child(self):
        return Scope(parent=self)

    def merge(self, other):
        self.members = dict(self.members.items() + other.members.items())
        return self

    def declare(self, ident, value):

        if ident in self.members:
            raise TypeError('Cannot re-declare variable: ' + ident)
        else:
            self.members[ident] = value

        return value

    def assign(self, ident, new_value):
        if ident in self:
            old_value = self[ident]
            return self._assign(old_value)(new_value)
        else:
            self.declare(ident, new_value)

    @multimethod(_store)
    def _assign(self, old_value):
        pass

    @_assign.d(node.Val)
    def _(self, old_value):
        def inner(value):
            if old_value.value == special.UNIT:
                old_value.value = value
                return value
            else:
                raise TypeError('Cannot reassign initialized val')
        return inner

    @_assign.d(node.Var)
    def _(self, old_value):
        def inner(value):
            old_value.value = value
            return value
        return inner


class Root(_Scope):
    def __init__(self):
        _Scope.__init__(self)


class Scope(_Scope):
    def __init__(self, parent):
        _Scope.__init__(self)

        assert parent is not None, 'Scopes parent cannot be None.'
        self.parent = parent

    def has_key(self, key):
        if key in self.members:
            return True
        else:
            return key in self.parent

    def __getitem__(self, key):
        try:
            return _Scope.__getitem__(self, key)
        except KeyError:
            return self.parent.__getitem__(key)
