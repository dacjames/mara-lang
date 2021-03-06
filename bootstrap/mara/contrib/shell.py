USAGE = '''
Usage:
    mara
    mara <code-file>                    [options]
    mara status                         [options]
    mara compile <code-file>            [options]
    mara eval <code-block>              [options]
    mara exec <shell-commands>          [options]
    mara install <module-path>          [options]
    mara search <query>                 [options]
    mara build [<command> [<module>]]   [options]

Options:
    -h, --help                      Display this docstring
    -l, --log-level                 Logging level (debug | info | warn | error)
    -v, --verbose                   Print more error messages
    -q, --quiet                     Shut up and don't ask questions
    -p, --pretty                    Pretty print any output

    -f, --file      [<file>]        Write/Load file
    -s, --string    [<string>]      Write/Read string
    -j, --json      [<object>]      Write/Read utf8 encoded json
    -b, --bytecode  [<msgpack>]     Write/Read binary msgpack
'''

COMMANDS = [
    'status', 'compile', 'eval', 'exec',
    'install', 'search', 'build',
]

EXAMPLE = '''
    mara status --json
    ==>
    {
      "module": "root/parent/example",
      "version": "0.1.1"
    }

    mara eval '10 ^ 2' ==> 100

    mara install 'git://github.com/mara/example' --quiet
    mara install 'file://~/Downloads/example.{tar.gz,zip}'
    mara install 'https://mara.io/example.{tar.gz, zip, git}'

    echo 'build\n install\n' > /tmp/example.mars
    mara exec --file /tmp/example.mars

    mara
    mara :> def myadd(a Int64, b Int64) {a + b}
        ==> myadd(a, b)
    mara :> myadd(3, 5)
        ==> 8
    mara :> myadd_func = myadd.compile
        ... compiling myadd
        ==> myadd_func(a, b)
    mara :> myadd_func(3, 5)
    mara :> using '/mara/lib/reflection'
        ==> module '/mara/lib/reflection'
    mara :> myadd_func.reflect.body
        ==> add(a Int64, b Int64)
    mara :> myadd_func.reflect.signature
        ==> myadd(a Int64, b Int64) -> Int64

'''

from docopt import docopt

if __name__ == '__main__':
    args = docopt(USAGE)





