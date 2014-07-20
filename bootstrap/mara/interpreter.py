'''
Mara Dynamic Interpreter
'''

# pylint: disable=W0212

import mara.special as special
import mara.passes as passes
import mara.constant as constant

from machine import Machine
from compiler import Compiler
from parser import Parser


class Interpreter(object):

    def __init__(self, buffered=False, traced=False):
        self.compiler = Compiler()
        self.parser = Parser()
        self.machine = Machine(buffered=buffered, traced=traced)

        self.isbuffered = buffered
        self.istraced = traced

    def evaluate(self, module):
        ast = self.parser.parse(module)

        ast.walk_down(passes.JoinElse())
        ast.walk_down(passes.ModuleFunction(), short_circuit=True)
        ast.walk_down(passes.CollectNames())
        ast.walk_down(passes.CollectLocals())

        pool = constant.ConstantPool()
        ast.walk_down(pool)

        bytecode = self.compiler.compile(ast, pool)
        result = self.compiler.result()

        self.machine._load(bytecode, pool)
        self.machine._loop()

        return self.machine._regs[result]
