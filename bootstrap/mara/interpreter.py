'''
Mara Dynamic Interpreter
'''

# pylint: disable=W0212
import readline
import subprocess
import traceback
import os

import mara.special as special
import mara.passes as passes
import mara.constant as constant

from machine import Machine
from compiler import Compiler
from parser import Parser


class MaraCompleter(object):
    def __init__(self):
        self.options = sorted([
            'import',
            'export',
        ])

        self.matches = []

    def build(self, text):

        if text:
            self.matches = [
                s
                for s in self.options
                if s.startswith(text)
            ]
            # logging.debug('%s matches: %s', repr(text), self.matches)
        else:
            self.matches = self.options[:]
            # logging.debug('(empty input) matches: %s', self.matches)

    def __call__(self, text, state):
        response = None

        if state == 0:
            # This is the first time for this text, so build a match list.
            self.build(text)

        # Return the state'th item from the match list,
        # if we have that many.
        try:
            response = self.matches[state]
        except IndexError:
            response = None

        # logging.debug('complete(%s, %s) => %s',
        #               repr(text), state, repr(response))

        return response


class Interpreter(object):

    def __init__(self, buffered=False, traced=False, shell=False, history=True):
        self.compiler = Compiler()
        self.parser = Parser()
        self.machine = Machine(buffered=buffered, traced=traced)
        self.completer = MaraCompleter()

        if shell:
            self.mara_dir = os.path.join(os.path.expanduser("~"), '.mara')
            if not os.path.exists(self.mara_dir):
                os.mkdir(self.mara_dir)

        if history:
            self.history_filename = os.path.join(self.mara_dir, "history.txt")

        self.isbuffered = buffered
        self.istraced = traced
        self.position = 0

        self.init_readline()

    def init_readline(self):
        readline.set_completer(self.completer)
        readline.parse_and_bind('tab: complete')

        if getattr(self, 'history_filename', None):
            try:
                readline.read_history_file(self.history_filename)
            except IOError:
                pass

    def on_exit(self):
        readline.write_history_file(self.history_filename)

    def eval_mara(self, line, type_check=False):
        module = 'module main_{0}\n{1}\nend'.format(self.position, line)

        ast = self.parser.parse(module)

        ast.walk_down(passes.JoinElse())
        ast.walk_down(passes.ModuleFunction(), short_circuit=True)
        ast.walk_down(passes.CollectNames())
        ast.walk_down(passes.CollectLocals())

        if type_check:
            ast.walk_up(passes.TypeCheck())

        pool = constant.ConstantPool()
        ast.walk_down(pool)

        bytecode = self.compiler.compile(ast, pool)

        result = self.compiler.result()

        if self.istraced:
            for i, code in enumerate(bytecode):
                print '{0}:\t{1}'.format(i, code)

        start = self.machine._load(bytecode, pool)
        self.machine._loop(start)

        return self.machine._regs[result]

    def eval_shell(self, line):
        cmd = line[1:]
        output = subprocess.check_output(cmd)
        return output

    def read(self):
        line = raw_input('~=> ')
        stripped = line.strip()

        return stripped

    def eval(self, line):
        if line in ['exit()', '.exit']:
            return special.HALT

        if line.startswith('!'):
            return self.eval_shell(line)

        try:
            data = self.eval_mara(line)
        except:
            traceback.print_exc()
            data = None

        return data

    def print_(self, data):
        print data

        return data

    def loop(self):

        while True:
            try:
                line = self.read()
                data = self.eval(line)

            except EOFError:
                data = special.HALT

            result = self.print_(data)

            if result is special.HALT:
                self.on_exit()
                break

            self.position += 1
