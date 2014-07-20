from interpreter import Interpreter
import cProfile


def maramodule(name, code):
    return 'module {n} {c} end'.format(n=name, c=code)


def program():
    interpreter = Interpreter()

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

        fib(20)
    ''')

    result = interpreter.evaluate(given)

    return result

cProfile.run('program()', sort='cumulative')
