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
