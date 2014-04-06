from functools import update_wrapper, wraps
from collections import defaultdict

def multimethod(store):

    def generic_decorator(f):

        class Generic(object):
            def __init__(self):
                self.__name__ = f.__name__

            def __call__(self, *args):
                return store[f.__name__][
                    tuple(a.__class__ for a in args)
                ](self, *args)

            def dispatch(self, *clses):
                print 'clses', clses
                def dispatch_decorator(handler):
                    store[f.__name__][clses] = handler
                    return handler

                return dispatch_decorator

            d = dispatch

        # generic(0, 1, 2)

        return wraps(f)(Generic())

    return generic_decorator

def method_store():
    return defaultdict(lambda: {})
