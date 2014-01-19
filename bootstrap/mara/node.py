
import util

class Node(object):
    def __eq__(self, other):
        '''Universal equality method based on inspecting the "public fields".
        '''
        canary = object()
        for attr in util.instance_fields(self):
            attribute = getattr(self, attr)
            other_attribute = getattr(other, attr, canary)

            if other_attribute is canary or attribute != other_attribute:
                return False
        return True


    def __repr__(self):
        '''Universal representation of the node based on inspecting the name
        and "public fields".
        '''

        fields = [(attr, repr(getattr(self, attr))) for attr in util.instance_fields(self)]
        field_str = ', '.join([
            '{name}={value}'.format(name=name, value=value) for
            (name, value) in fields
        ])
        return '{cls}({fields})'.format(
            cls=self.__class__.__name__,
            fields=field_str,
        )

class Module(Node):
    def __init__(self, name=None, exprs=None):
        self.name = name
        self.exprs = exprs

class Tuple(Node):
    def __init__(self, values=[]):
        self.values = values

