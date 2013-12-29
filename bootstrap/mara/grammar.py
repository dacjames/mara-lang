'''Mara's Grammar
'''

import json

from util import lib, cli

from plyplus import Grammar, STransformer

###########################################################
# Grammar
###########################################################

class MaraTransformer(STransformer):
    """Transforms JSON AST into Python native objects."""
    number  = lambda self, node: float(node.tail[0])
    string  = lambda self, node: node.tail[0][1:-1]
    boolean = lambda self, node: True if node.tail[0] in ['true'] else False
    null    = lambda self, node: None
    array   = lambda self, node: node.tail
    pair    = lambda self, node: { node.tail[0] : node.tail[1] }
    def object(self, node):
        result = {}
        for i in node.tail:
            result.update( i )
        return result


def load_grammar(grammar_file):
    with open(grammar_file) as f:
        g = Grammar(f.read())
    return g


def transform(grammar, src_str):
    transformer = MaraTransformer()
    result = transformer.transform(grammar.parse(src_str))
    return result

###########################################################
# Grammar CLI
###########################################################

cli.option('-g --grammar_file=<f> Grammar File.')


@cli.cmd('load [options]')
def load_cmd(grammar_file):
    print grammar(grammar_file)

@cli.cmd('parse [options] <src_file>')
def parse_cmd(src_file, grammar_file):
    with open(src_file) as srcf:
        src_str = srcf.read()
    print 'Input'
    print '#=#==#=*=#====#==*==#====#=*=#==#=#'
    print src_str

    print 'Output'
    print '#=#==#=*=#====#==*==#====#=*=#==#=#'
    result = transform(load_grammar(grammar_file), src_str)
    import pprint
    pprint.pprint(result)

if __name__ == '__main__':
    cli.main()


