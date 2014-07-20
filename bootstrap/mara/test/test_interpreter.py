'''
Test the Mara Bytecode Compiler
'''

# pylint: disable=W0611
# pylint: disable=W0621
# pylint: disable=W0212


import pytest

from ..interpreter import Interpreter
from ..compiler import CompileError
from .. import special

from test_parser import maramodule


@pytest.fixture
def interpreter():
    return Interpreter(traced=True)


def test_math(interpreter):

    given = maramodule('test', '''
        5 + 2 * 8 / 4 - 5
    ''')

    result = interpreter.evaluate(given)

    assert result == 4


def test_bad(interpreter):

    given = maramodule('test', '''
        3 ^ 4
    ''')

    with pytest.raises(CompileError):
        interpreter.evaluate(given)


def test_if_true(interpreter):

    given = maramodule('test', '''
        if 1 {
            2 * 10
            3 + 5
        }
    ''')

    result = interpreter.evaluate(given)

    assert result == 8


def test_if_false(interpreter):

    given = maramodule('test', '''
        if 0 {
            2 * 10
            3 + 5
        }
    ''')

    result = interpreter.evaluate(given)

    assert result is special.NULL


def test_if_else(interpreter):

    given = maramodule('test', '''
        if 0 {
            2 * 10
            3 + 5
        } else {
            5 - 3
        }
    ''')

    result = interpreter.evaluate(given)

    assert result == 2


def test_variable_resolution_with_constants(interpreter):
    given = maramodule('test', '''
        val x = (5 + 5)
        var y = 2
        x * y
    ''')

    result = interpreter.evaluate(given)

    assert result == 20


def test_define_and_call(interpreter):
    given = maramodule('test', '''
        def add(x, y) {
            x + y
        }

        def add_ten(x) {
            val y = 10
            x + y
        }

        val a = add(1, 2)
        val b = add(3, 4)

        a + b
    ''')

    result = interpreter.evaluate(given)

    assert result == 10


def test_nested_if_inside_function(interpreter):
    given = maramodule('test', '''
        def foo(x) {
            if x + 1 {
                5
            }
            else {

                if 0 { 10 }
                else { 20 }
            }
        }

        foo(-1)
    ''')

    result = interpreter.evaluate(given)

    assert result == 20


def test_variable_assignment(interpreter):
    given = maramodule('test', '''
        def foo() {
            var z = 4
            z = 3
        }

        foo()
    ''')

    result = interpreter.evaluate(given)

    assert result == 3


def test_fib(interpreter):
    given = maramodule('test', '''
        def fib (x) {
            1 if x == 0
            else {
                1 if x == 1
                else {
                    (fib(x - 2)) +
                    (fib(x - 1))
                }
            }
        }

        fib(4)
    ''')

    result = interpreter.evaluate(given)

    assert result == 5


@pytest.mark.skipif(True, reason='slowness')
def test_benchmark(interpreter):
    given = maramodule('test', '''
        def slow_double (x, y) {
            if x == 0 {
                y
            } else {
                slow_double(x - 1, y + 2)
            }
        }

        slow_double(100, 0)
    ''')

    result = interpreter.evaluate(given)

    assert result == 200
