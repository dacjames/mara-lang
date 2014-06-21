from functools import wraps
from collections import defaultdict


def multimethod(store):

    def generic_decorator(f):

        @wraps(f)
        def generic(*args):
            return store[f.__name__][
                tuple(a.__class__ for a in args[1:])
            ](*args)

        def dispatch(*clses):

            def dispatch_decorator(handler):
                handler.__name__ = '_'.join(
                    [f.__name__] +
                    [c.__name__ for c in clses]
                )
                store[f.__name__][clses] = handler
                return handler

            return dispatch_decorator

        generic.d = generic.dispatch = dispatch

        return generic

    return generic_decorator


def method_store():
    return defaultdict(lambda: {})
