from docopt import docopt
import sys


class CLI:
    commands = set()
    options = set()
    actions = {}

    @classmethod
    def usage(cls):
        return '''
    Usage:
        {commands}

    Options:
        {options}
        '''.format(
            commands='\n        '.join(cls.commands),
            options='\n        '.join(cls.options),
        )

    @classmethod
    def validate(cls):
        '''
        validate cmd_line
        by passing no arguments to the generated parser
        and ensuring that a DocOpt exception is through
        '''
        try:
            docopt(CLI.usage(), argv=[])
        except Exception as e:
            pass


def option(option_line):
    CLI.options.add(option_line)
    # CLI.validate()


def cmd(cmd_line):

    CLI.commands.add(sys.argv[0] + ' ' + cmd_line)
    action = cmd_line.split(' ')[0]

    # CLI.validate()

    def cmd_decorator(wrapped):
        CLI.actions[action] = wrapped
        wrapped
    return cmd_decorator


def main():
    # print CLI.usage()
    args = docopt(CLI.usage())

    # print args

    for action, function in CLI.actions.items():
        if args[action]:
            positional = [
                value for arg, value in args.items()
                if arg.startswith('<') and value is not None
            ]
            options = {
                arg[2:]: value
                for arg, value in args.items()
                if arg.startswith('--')
            }

            # print positional
            # print options

            function(*positional, **options)
