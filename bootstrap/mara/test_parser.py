from parser import parser
import node as n


def test_parse_literals():
    assert (
        parser.parse('module test 10 end') ==
        n.Module(name='test', exprs=[
            n.Int(value='10')
        ])
    )

    assert (
        parser.parse('module test 10.0 end') ==
        n.Module(name='test', exprs=[
            n.Real(value='10.0')
        ])
    )

    assert (
        parser.parse('module test 1e10 end') ==
        n.Module(name='test', exprs=[
            n.Sci(value='1e10')
        ])
    )

def test_parse_simple_expr():
    given = 'module x * 1 end'
    output = n.Module(
        name='_anon_module_0',
        exprs=[
            n.BinOp(
                func=n.SymbolId('*'),
                args=[
                    n.ValueId('x'),
                    n.Int('1'),
                ],
            ),
        ],
    )
    assert parser.parse(given) == output

def test_parse_unwrapped_if():
    given = 'module simple if x > 0 x * 2.0 end'
    output = n.Module(
        name='simple',
        exprs=[
            n.If(
                pred=n.BinOp(
                    func=n.SymbolId('>'),
                    args=[
                        n.ValueId('x'),
                        n.Int(value='0'),
                    ]
                ),
                body=n.BinOp(
                    func=n.SymbolId('*'),
                    args=[
                        n.ValueId('x'),
                        n.Real(value='2.0')
                    ]
                ),
            ),
        ],
    )
    assert parser.parse(given) == output

def test_parse_wrapped_if():
    given = 'module simple if (x > 0){x * 2.0} end'
    output = n.Module(
        name='simple',
        exprs=[
            n.If(
                pred=n.BinOp(
                    func=n.SymbolId('>'),
                    args=[
                        n.ValueId('x'),
                        n.Int(value='0'),
                    ]
                ),
                body=n.Block(
                    exprs=[
                        n.BinOp(
                            func=n.SymbolId('*'),
                            args=[
                                n.ValueId('x'),
                                n.Real(value='2.0')
                            ]
                        ),
                    ]
                ),
            ),
        ],
    )
    assert parser.parse(given) == output
