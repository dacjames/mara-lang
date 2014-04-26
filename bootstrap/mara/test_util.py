import string
import random

import util


def _random_prefixes():
    prefixes = {
        None: 10
    }
    for _ in range(100):
        length = random.choice(range(1,20))
        prefix = ''.join([random.choice(string.letters) for _ in range(length)])
        count = random.choice(range(10, 100))
        prefixes[prefix] = count
    return prefixes


def test_unique_ids():
    prefixes = _random_prefixes()
    ids = []
    for prefix, count in prefixes.items():
        ids.append(util.unique_id(prefix))

    assert sorted(ids) == sorted(list(set(ids)))


def test_anonymous_names():
    prefixes = _random_prefixes()
    names = []
    for prefix, count in prefixes.items():
        names.append(util.anonymous_name(kind=prefix))

    for name in names:
        assert '_anon_' in name

    assert sorted(names) == sorted(list(set(names)))


class AttrTest(object):
    class_field0 = 'class_field'
    class_field1 = 0

    @classmethod
    def class_method0(cls):
        pass

    @classmethod
    def class_method1(cls):
        pass

    @property
    def property0(self):
        return 'property0'

    @property
    def property1(self):
        return 'property1'

    def __init__(self):
        self.instance_field0 = 'instance_field'
        self.instance_field1 = 0

    def instance_method0(self):
        pass

    def instance_method1(self):
        pass


def test_public_attrs_field_methods():


    test = AttrTest()

    instance_fields = ['instance_field0', 'instance_field1', 'property0', 'property1']
    instance_methods = ['instance_method0', 'instance_method1']
    instance_attrs = ['instance_field0', 'instance_field1', 'instance_method0', 'instance_method1', 'property0', 'property1']

    assert util.instance_fields(test) == instance_fields
    assert util.instance_methods(test) == instance_methods
    assert util.instance_attrs(test) == instance_attrs

    class_fields = ['class_field0', 'class_field1']
    class_methods = ['class_method0', 'class_method1']

    assert util.class_fields(test) == class_fields
    assert util.class_methods(test) == class_methods
    assert util.class_attrs(test) ==  class_fields + class_methods

def test_mutlimethods():

    from util.dispatch import method_store, multimethod

    class Eval(object):
        store = method_store()

        def dummy(self):
            return True

        @multimethod(store)
        def visit(self, a):
            pass

        @visit.dispatch(int)
        def _(self, a):
            assert self.dummy()
            return 'Int', a

        @multimethod(store)
        def multi(self, a, b):
            pass

        @multi.dispatch(int, float)
        def _(self, a, b):
            assert self.dummy()
            return 'Int', 'Real', a, b

        @multi.dispatch(float, float)
        def _(self, a, b):
            assert self.dummy()
            return 'Real', 'Real', a, b

    eval_ = Eval()

    assert eval_.visit.__name__ == 'visit'

    assert eval_.visit(10) == ('Int', 10)
    assert eval_.multi(10, 10.0) == ('Int', 'Real', 10, 10.0)
    assert eval_.multi(10.0, 10.0) == ('Real', 'Real', 10, 10.0)

def test_deriving():
    from util.reflection import deriving

    class EqAble(deriving('eq')):
        def __init__(self, x):
            self.x = x
            self.y = 0

    class ShowAble(deriving('show')):
        def __init__(self, x):
            self.x = x
            self.y = 'a'

    class EqShowAble(deriving('eq', 'show')):
        def __init__(self, x):
            self.x = x
            self.y = {}

    eq0 = EqAble(0)
    eq1 = EqAble(0)
    eq2 = EqAble(1)

    show = ShowAble(1)

    eq_show0 = EqShowAble(0)
    eq_show1 = EqShowAble(0)
    eq_show2 = EqShowAble(1)

    assert repr(show) == "ShowAble(x=1, y='a')"
    assert str(show) == "ShowAble(x=1, y=a)"
    assert eq0 == eq1
    assert eq2 != eq1

    assert repr(eq_show0) == 'EqShowAble(x=0, y={})'
    assert repr(eq_show1) == 'EqShowAble(x=0, y={})'
    assert repr(eq_show2) == 'EqShowAble(x=1, y={})'

    assert eq_show0 == eq_show1
    assert eq_show2 != eq_show1
