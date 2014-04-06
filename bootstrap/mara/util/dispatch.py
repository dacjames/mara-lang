from functools import update_wrapper
from collections import defaultdict

def multimethod(store):

    def generic_decorator(f):

        class Generic(object):
            def __call__(*args):
                return store[f.__name__][
                    tuple(a.__class__ for a in args[1:])
                ](*args)

            def dispatch(self, *clses):
                def dispatch_decorator(handler):
                    store[f.__name__][clses] = handler
                    return f

                return dispatch_decorator

        generic = Generic()
        update_wrapper(generic, f)

        return generic

    return generic_decorator

def method_store():
    return defaultdict(lambda: {})
