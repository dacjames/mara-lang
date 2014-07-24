'''
A simple assembler that resolves labels.
'''

from util.dispatch import method_store, multimethod

class Assembler(object):
    _store = method_store()

    def __init__(self):
        self._labels = {}

    def assemble(self, bytecode):
        newcode = []

        for i, code in enumerate(bytecode):
            op = code[0]
            if op == 'label':
                name = code[1]
                # +1 because labels refer to the next bytecode
                self._labels[name] = i + 1

        for code in bytecode:
            op = code[0]
            args = code[1:]

            func = getattr(self, op, self.default)
            result = func(op, *args)

            newcode.append(result)

        print newcode
        return newcode

    def jump(self, op, label):
        address = self._labels[label]

        return (op, address)

    def branch_zero(self, op, pred, label):
        address = self._labels[label]

        return (op, pred, address)

    def branch_one(self, op, pred, label):
        address = self._labels[label]

        return (op, pred, address)

    def branch_eq(self, op, left, right, label):
        address = self._labels[label]

        return (op, left, right, address)

    def default(self, *args):

        return tuple(args)
