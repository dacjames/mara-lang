import logging
import readline
import subprocess
import traceback

import special
import interpreter

LOG_FILENAME = '/tmp/completer.log'
logging.basicConfig(
    filename=LOG_FILENAME,
    level=logging.DEBUG,
)

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
            logging.debug('%s matches: %s', repr(text), self.matches)
        else:
            self.matches = self.options[:]
            logging.debug('(empty input) matches: %s', self.matches)

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
        
        logging.debug('complete(%s, %s) => %s', 
                      repr(text), state, repr(response))
        
        return response


class MaraShell(object):
    def __init__(self):
        self._completer = MaraCompleter()

        readline.set_completer(self._completer)
        readline.parse_and_bind('tab: complete')

        self._interpreter = interpreter.Interpreter()

        self._position = 0

    def _shell_out(self, cmd):
        output = subprocess.check_output(cmd)
        return output

    def read(self, line):
        return line.strip()

    def eval(self, src):

        if src in ['exit()', '.exit']:
            return special.HALT

        if src.startswith('!'):
            cmd = src[1:]
            return self._shell_out(cmd)


        module = 'module main_{0}\n{1}\nend'.format(self._position, src)
        try:
            data = self._interpreter.evaluate(module)
        except:
            traceback.print_exc()
            data = None

        return data

    def print_(self, data):
        print data

        return data 

    def loop(self):
        line = ''

        while True:
            try:
                line = raw_input('~=> ')
                src = self.read(line)
                data = self.eval(src)
                
            except EOFError:
                data = special.HALT

            result = self.print_(data)
            if result is special.HALT:
                break

            self._position += 1


if __name__ == '__main__':
    shell = MaraShell()
    shell.loop()
