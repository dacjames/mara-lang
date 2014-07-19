'''
Define some special purpose singletons.
'''


class SpecialValue(object):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)

    def __repr__(self):
        return str(self.name)

NULL = SpecialValue('NULL')
UNIT = SpecialValue('UNIT')
HALT = SpecialValue('HALT')
