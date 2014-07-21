from util.dispatch import method_store, multimethod
import node


class ConstantPool(object):
    '''
    A pool for holding compile time constants.
    '''

    _store = method_store()

    def __init__(self):
        self._pool = []

        self._add(node.Bool('0'), lambda n: int(n.value))
        self._add(node.Bool('1'), lambda n: int(n.value))

    def __getitem__(self, key):
        return self._pool.__getitem__(key)

    @multimethod(_store)
    def visit(self, n):
        pass

    @visit.d(node.Int)
    def _(self, n):
        self._add(n, lambda n: int(n.value))

    @visit.d(node.Real)
    def _(self, n):
        self._add(n, lambda n: float(n.value))

    @visit.d(node.Bool)
    def _(self, n):
        if n.value == '0':
            n['constant'] = 0
        else:
            n['constant'] = 1

    def _add(self, n, accessor):
        index = len(self._pool)
        value = accessor(n)

        self._pool.append(value)
        n['constant'] = index
