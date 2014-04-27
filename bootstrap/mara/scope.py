#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Scope Objects
'''

from util.dispatch import method_store, multimethod
from util.reflection import deriving

import node


class ScopeBox(deriving('show', 'eq')):
    def __init__(self, value):
        self.value = value


class ValBox(ScopeBox):
    pass


class VarBox(ScopeBox):
    pass


class _Scope(deriving('show', 'eq')):
    _store = method_store()

    def __init__(self):
        self.members = {}

    def __getitem__(self, key):
        return self.members.__getitem__(key)

    def __setitem__(self, key, value):
        return self.members.__setitem__(key, value)

    def __delitem__(self, key):
        return self.members.__delitem__(key)

    def __contains__(self, key):
        return self.has_key(key)

    def keys(self):
        return self.members.keys()

    def values(self):
        return self.members.values()

    def items(self):
        return self.members.items()

    def has_key(self, key):
        return self.members.has_key(key)

    def get(self, key, default=None):
        return self.members.get(key, default)

    def clear(self):
        return self.members.clear()

    def setdefault(self, default):
        return self.members.setdefault(default)

    def iterkeys(self):
        return self.members.iterkeys()

    def itervalues(self):
        return self.members.itervalues()

    def iteritems(self):
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

    def declare(self, ident, boxed):
        assert isinstance(boxed, ScopeBox), 'method Scope::declare expected a boxed value.'

        if ident in self.members:
            raise TypeError('Cannot re-declare variable: ' + ident)
        else:
            self.members[ident] = boxed

        return boxed

    def assign(self, ident, unboxed):
        if ident in self:
            box = self[ident]
            return self._assign(box)(unboxed)
        else:
            self.declare(ident, ValBox(unboxed))

    @multimethod(_store)
    def _assign(self, box):
        pass

    @_assign.d(ValBox)
    def _(self, box):
        def inner(value):
            if box.value == ():
                box.value = value
                return value
            else:
                raise TypeError('Cannot reassign initialized val')
        return inner

    @_assign.d(VarBox)
    def _(self, box):
        def inner(value):
            box.value = value
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
        if self.members.has_key(key):
            return True
        else:
            return self.parent.has_key(key)

    def __getitem__(self, key):
        try:
            return self.members.__getitem__(key)
        except KeyError:
            return self.parent.__getitem__(key)


