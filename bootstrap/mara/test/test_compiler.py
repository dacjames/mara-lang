'''
Test the Mara Bytecode Compiler
'''

# pylint: disable=W0611
# pylint: disable=W0621
# pylint: disable=W0212


import pytest

from ..compiler import Compiler, CompileError
from ..machine import NULL

from test_lexer import lex_simple
from test_parser import parser, maramodule
from test_machine import machine


@pytest.fixture
def compiler():
    return Compiler()


def test_math(parser, compiler, machine):

    given = maramodule('test', '''
        5 + 2 * 8 / 4 - 5
    ''')

    ast = parser.parse(given)
    bytecode = compiler.compile(ast)
    result = compiler.result()

    assert isinstance(bytecode, list)

    machine._load(bytecode)
    machine._loop()

    assert machine._regs[result] == 4


def test_bad(parser, compiler):

    given = maramodule('test', '''
        3 ^ 4
    ''')
    ast = parser.parse(given)

    with pytest.raises(CompileError):
        compiler.compile(ast)


def test_if_true(parser, compiler, machine):

    given = maramodule('test', '''
        if 1 {
            2 * 10
            3 + 5
        }
    ''')

    ast = parser.parse(given)
    bytecode = compiler.compile(ast)
    result = compiler.result()

    machine._load(bytecode)
    machine._loop()

    assert machine._regs[result] == 8


def test_if_false(parser, compiler, machine):

    given = maramodule('test', '''
        if 0 {
            2 * 10
            3 + 5
        }
    ''')

    ast = parser.parse(given)
    bytecode = compiler.compile(ast)
    result = compiler.result()

    machine._load(bytecode)
    machine._loop()

    assert machine._regs[result] is NULL
