import pytest

from .. import evaluate

from .test_parser import maramodule

from .test_lexer import lex_simple
from .test_parser import parser


@pytest.fixture
def evaluator():
    return evaluate.Eval()


def test_eval_numbers(evaluator, lex_simple, parser):
    given = maramodule('numbers', '''
        5 + 2 * 2^2 / 2 - 5
    ''')

    expected = 4.0
    ast = parser.parse(given)
    result = evaluator.visit(ast)

    assert expected == result


def test_simple_control_flow(evaluator, lex_simple, parser):
    given = maramodule('control_flow', '''
        if 1 < 2 {
            10
        } else {
            20
        }
    ''')

    expected = 10

    ast = parser.parse(given)
    result = evaluator.visit(ast)

    assert expected == result


def test_values_and_variables(evaluator, lex_simple, parser):
    given = maramodule('val_and_var', u'''
        val x 10
        val y { 20 }
        val z ()
        z = 30

        val t { x + y + z }

        var a 1
        var b { 2 }
        var c ()
        c = 3

        val u (a + b + c)

        a = 101
        b = 102
        c = 103

        val v ()
        v = a + b + c +
            t + u
    ''')

    expected = (
        101 + 102 + 103 +
        (10 + 20 + 30) + (1 + 2 + 3)
    )

    ast = parser.parse(given)
    result = evaluator.visit(ast)

    assert expected == result


def test_nested_variables(evaluator, lex_simple, parser):
    given = maramodule('test_nested_variables', '''
        val x { 10 }
        var y 3

        while y > 0 {
            val x ()
            x = 20
            y = y - 1
        }

        x + y
    ''')

    expected = 10

    ast = parser.parse(given)
    result = evaluator.visit(ast)

    assert expected == result
