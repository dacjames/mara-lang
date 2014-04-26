import pytest

import evaluate

from test_parser import maramodule

from test_lexer import lex_simple
from test_parser import parser

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

