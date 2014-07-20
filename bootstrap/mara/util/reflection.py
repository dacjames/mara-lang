'''Reflection functions
'''

import types

##############################################################################
# Deriving
##############################################################################


class _Derived(object):
    '''Base class for dynamically generated "Derived" class

    (Currently Empty)
    '''
    pass


def _derived__eq__(self, other):
    '''Universal equality method based on inspecting the "public fields".
    '''
    canary = object()
    for attr in instance_fields(self):

        attribute = getattr(self, attr)
        other_attribute = getattr(other, attr, canary)
        equal = (other_attribute is not canary and attribute == other_attribute)

        if not equal:
            return False
    return self.__class__ == other.__class__


def _derived__ne__(self, other):
    '''Universal not equal method implimented as not(self == other).
    '''
    return not(self == other)


def _derived__repr__(self):
    '''Universal repr method

    Based on inspecting the name and "public fields".
    '''
    fields = [
        (attr, repr(getattr(self, attr)))
        for attr in instance_fields(self)
    ]

    field_str = ', '.join([
        '{name}={value}'.format(name=name, value=value) for
        (name, value) in fields
    ])
    return '{cls}({fields})'.format(
        cls=self.__class__.__name__,
        fields=field_str,
    )


def _derived__str__(self):
    '''Universal str str method

    Based on inspecting the name and "public fields".
    '''
    fields = [
        (attr, str(getattr(self, attr)))
        for attr in instance_fields(self)
    ]

    field_str = ', '.join([
        '{name}={value}'.format(name=name, value=value) for
        (name, value) in fields
    ])

    return '{cls}({fields})'.format(
        cls=self.__class__.__name__,
        fields=field_str,
    )


def _derived__dictstr__(self):
    items = sorted(self.members.items())
    field_str = ', '.join([
        '{k}: {v}'.format(k=key, v=value)
        for key, value in items
    ])

    return "{cls}({{{f}}})".format(cls=self.__class__.__name__, f=field_str)


def _derived__dictrepr__(self):
    items = sorted(self.members.items())
    field_str = ', '.join([
        '{k}: {v}'.format(k=repr(key), v=repr(value))
        for key, value in items
    ])

    return "{cls}({{{f}}})".format(cls=self.__class__.__name__, f=field_str)


def _derived__dicteq__(self, other):
    try:
        return sorted(self.iteritems()) == sorted(other.iteritems())
    except AttributeError:
        return False


def _deriving(*method_ids):
    '''Generates a deriving class containing the given method identifiers.
    '''
    g = globals()
    methods = {}

    for method_id in method_ids:
        method = g.get('_derived' + method_id)

        if method is not None:
            method_name = _derivable_names.get(method_id, method_id)
            methods[method_name] = method
        else:
            raise TypeError('derivable base method "{m}" not found'.format(
                m=method_id
            ))

    cls_name = '_' + ''.join(['Deriving'] + list(method_ids))
    cls_bases = (_Derived,)
    cls = type(cls_name, cls_bases, methods)

    return cls


_derivable_ids = {'__repr__', '__eq__'}


_derivable_names = {
    '__dictstr__': '__str__',
    '__dictrepr__': '__repr__',
    '__dicteq__': '__eq__',
}

_derivable_mapping = {
    'show': ['__repr__', '__str__'],
    'eq': ['__eq__', '__ne__'],
    'members_dict': ['__dicteq__', '__dictrepr__', '__dictstr__'],
}


def deriving(*method_names):
    '''Derive useful builtin methods.

    Supports:
        - 'eq' : equality based on "public" attrs
        - 'show' : repr and str methods based on "public" attrs
    '''

    method_ids = []
    for name in method_names:

        if name in _derivable_ids:
            method_ids.append(name)

        elif name in _derivable_mapping:
            method_ids += _derivable_mapping[name]

        else:
            raise TypeError('derivable trait "{m}" not found'.format(
                m=name
            ))

    return _deriving(*method_ids)


##############################################################################
# Reflection Functions
##############################################################################


def _public_attrs(obj, pred=lambda attr: True):
    '''Public attributes of an object, fields and methods,
    filtered by a predicate.
    '''
    return sorted([
        attr for attr in dir(obj)
        if not attr.startswith('_') and pred(attr)
    ])


def _is_instance_method(obj, attr):
    attribute = getattr(obj, attr)
    return (
        isinstance(attribute, types.MethodType) and
        attribute.im_class is obj.__class__
    )


def _is_instance_field(obj, attr):
    attribute = getattr(obj, attr, None)
    return (
        not isinstance(attribute, types.MethodType) and
        getattr(obj.__class__, attr, None) is None
    )


def _is_instance_property(obj, attr):
    attribute = getattr(obj, attr, None)

    return (
        isinstance(getattr(obj.__class__, attr, None), property)
    )


def class_attrs(obj):
    '''Public attributes(fields and methods) of an object's class.
    '''
    def pred(attr):
        return (
            (_is_instance_field(obj.__class__, attr) or
             _is_instance_method(obj.__class__, attr)) and
            not isinstance(getattr(obj.__class__, attr, None), property)
        )

    return _public_attrs(obj.__class__, pred)


def class_fields(obj):
    '''Public fields of an object's class.
    '''
    def pred(attr):
        return (
            _is_instance_field(obj.__class__, attr) and
            not isinstance(getattr(obj.__class__, attr, None), property)
        )
    return _public_attrs(obj.__class__, pred)


def class_methods(obj):
    '''Public methods on an object's class.
    '''
    def pred(attr):
        return (
            _is_instance_method(obj.__class__, attr) and
            not isinstance(getattr(obj.__class__, attr, None), property)
        )
    return _public_attrs(obj.__class__, pred)


def instance_attrs(obj):
    '''Public attributes(fields, properties, and methods) of an object.
    '''
    def pred(attr):
        return (
            _is_instance_field(obj, attr) or
            _is_instance_method(obj, attr) or
            _is_instance_property(obj, attr)
        )

    return _public_attrs(obj, pred)


def instance_members(obj):
    '''Public members (fields and properties) of an object.
    '''
    def pred(attr):
        return (
            _is_instance_field(obj, attr) or
            _is_instance_property(obj, attr)
        )

    return _public_attrs(obj, pred)


def instance_fields(obj):
    '''Public fields of an object.
    '''
    return _public_attrs(obj, lambda attr: _is_instance_field(obj, attr))


def instance_methods(obj):
    '''Public methods on an object.
    '''
    return _public_attrs(obj, lambda attr: _is_instance_method(obj, attr))


def instance_properties(obj):
    '''Public properties of an object.
    '''
    return _public_attrs(obj, lambda attr: _is_instance_property(obj, attr))

##############################################################################
##############################################################################
