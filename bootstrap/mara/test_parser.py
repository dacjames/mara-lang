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
    expected = n.Module(
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
    result = parser.parse(given)
    assert expected == result


def test_exprs_parse_assignment(parser):
    given = 'module assignment a = 10 end'

    expected = n.Module('assignment', [
        n.Assign(name=n.ValueId('a'), value=n.Int('10'), type_=None)
    ])

    result = parser.parse(given)
    assert expected == result

    given = 'module assignment a Real = 1.0 end'

    expected = n.Module('assignment', [
        n.Assign(name=n.ValueId('a'), value=n.Int('1.0'), type_=n.TypeId('Real'))
    ])

    result = parser.parse(given)
    assert expected == result


def test_parse_unwrapped_if(parser):
    given = 'module simple (x * 2.0) if (x > 0) end'
    expected = n.Module(
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
    result = parser.parse(given)
    assert expected == result


def test_parse_wrapped_if(parser):
    given = 'module simple if (x > 0) {x * 2.0} end'
    expected = n.Module(
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
                    params=[],
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
    result = parser.parse(given)
    assert expected == result


def test_parse_postfix_while(parser):
    given = maramodule('while (x > 0) {x * 2}')
    expected = n.Module(
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
                    params=[],
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

    result = parser.parse(given)
    assert expected == result


@xfail
def test_exprs_and_blocks(parser):
    given = '''module blocks
                    block = {
                        x = 10
                        y = x
                    }
                    empty = {}
                end'''
    expected = n.Module(
        name='blocks',
        exprs=[
            n.Assign(
                name=n.ValueId('block'),
                value=n.Block(
                    params=[],
                    exprs=[
                        n.Assign(name=n.ValueId('x'), value=n.Int('10'), type_=None),
                        n.Assign(name=n.ValueId('y'), value=n.ValueId('x'), type_=None),
                    ],
                ),
            ),
            n.Assign(
                name=n.ValueId('empty'),
                value=n.Block(
                    params=[],
                    exprs=[],
                ),
            ),
        ],
    )

    result = parser.parse(given)


    print result
    print '---'
    print expected


    assert result.name == expected.name
    assert result.exprs[0].name == expected.exprs[0].name
    assert result.exprs[0].value.exprs[0] == expected.exprs[0].value.exprs[0]
    assert result.exprs[0].value.exprs[1] == expected.exprs[0].value.exprs[1]
    assert  expected == result
