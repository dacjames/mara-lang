'''Reflection functions
'''

import types


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
    ) or isinstance(getattr(obj.__class__, attr, None), property)


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
    '''Public attributes(fields and methods) of an object.
    '''
    def pred(attr):
        return _is_instance_field(obj, attr) or _is_instance_method(obj, attr)

    return _public_attrs(obj, pred)


def instance_fields(obj):
    '''Public fields of an object.
    '''
    return _public_attrs(obj, lambda attr: _is_instance_field(obj, attr))


def instance_methods(obj):
    '''Public methods on an object.
    '''
    return _public_attrs(obj, lambda attr: _is_instance_method(obj, attr))
