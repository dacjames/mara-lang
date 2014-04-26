#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Scope Objects
'''

import node

class _Scope(node.Node):
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

    def child(self):
        return Scope(parent=self)

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


