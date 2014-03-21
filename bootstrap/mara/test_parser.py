import parser as parser_module
import node as n
import pytest

xfail = pytest.mark.xfail


def maramodule(code):
    return 'module test {c} end'.format(c=code)


@pytest.fixture
def parser():
    return parser_module.build_parser()


def test_parse_literals(parser):
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


def test_parse_simple_expr(parser):
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


def test_exprs_parse_assignment(parser):
    given = 'module assignment a = 10 end'

    output = n.Module('assignment', [
        n.Assign(name=n.ValueId('a'), value=n.Int('10'), type_=None)
    ])

    assert parser.parse(given) == output

    given = 'module assignment a Real = 1.0 end'

    output = n.Module('assignment', [
        n.Assign(name=n.ValueId('a'), value=n.Int('1.0'), type_=n.TypeId('Real'))
    ])

    assert parser.parse(given) == output


def test_parse_unwrapped_if(parser):
    given = 'module simple (x * 2.0) if (x > 0) end'
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


def test_parse_wrapped_if(parser):
    given = 'module simple if (x > 0) {x * 2.0} end'
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


def test_parse_postfix_while(parser):
    given = maramodule('while (x > 0) {x * 2}')
    output = n.Module(
        name='test',
        exprs=[
            n.While(
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
                                n.Real(value='2')
                            ]
                        ),
                    ]
                ),
            )
        ]
    )

    assert parser.parse(given) == output


@xfail
def test_exprs_and_blocks():
    given = '''module blocks
                    block = {
                        x = 10
                        y = x   +
                            10  *
                            8   \
                            .commit()
                        _z = x + y; z = 2 * _x
                    }
                end
                '''
    output = n.Module(
        name='simple',
        exprs=[
            n.Assign(
                name='block',
                value=n.Block(
                    params=[],
                    exprs=[],
                ),
            )
        ],
    )
    assert parser.parse(given) == output
