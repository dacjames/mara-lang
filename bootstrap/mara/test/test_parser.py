from .. import parser as parser_module
from .. import node as n
import pytest

# pylint: disable=W0621
# pylint: disable=C0330

xfail = pytest.mark.xfail

from test_lexer import lex_simple  # pylint: disable=W0611


def maramodule(name, code):
    return 'module {n} {c} end'.format(n=name, c=code)


@pytest.fixture
def parser(lex_simple):
    # pylint:disable=W0612
    # this is dirty hack because we need to trigger a lexer import.
    lex_simple = lex_simple
    return parser_module.build_parser()


def test_parse_literals(parser):
    assert (
        parser.parse(maramodule('test', '''
            10
        ''')) == n.Module(name='test', exprs=[
            n.Int(value='10')
        ])
    )

    assert (
        parser.parse('module test; 10.0 end') ==
        n.Module(name='test', exprs=[
            n.Real(value='10.0')
        ])
    )

    assert (
        parser.parse('module test; 1e10 end') ==
        n.Module(name='test', exprs=[
            n.Sci(value='1e10')
        ])
    )


def test_parse_simple_expr(parser):
    given = 'module; x * 1 end'
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


def test_parse_function_call(parser):
    given = maramodule('test', '''
        foo 10
    ''')

    expected = n.Module('test', [
        n.Call(func=n.ValueId('foo'), arg=n.Int('10'))
    ])

    result = parser.parse(given)
    assert expected == result


def test_exprs_parse_assignment(parser):
    given = maramodule('assignment', '''
        a = 10
    ''')

    expected = n.Module('assignment', [
        n.Assign(name=n.ValueId('a'), value=n.Int('10'), type_=None)
    ])

    result = parser.parse(given)
    assert expected == result

    given = 'module assignment; val a Real = 1.0 end'

    expected = n.Module('assignment', [
        n.Assign(name=n.ValueId('a'), value=n.Int('1.0'), type_=n.TypeId('Real'))
    ])

    result = parser.parse(given)
    assert expected == result


def test_parse_unwrapped_if(parser):
    given = 'module simple; x * 2.0 if x > 0 end'
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
    assert expected.exprs[0].pred == result.exprs[0].pred
    assert expected == result


def test_parse_wrapped_if(parser):
    given = 'module simple; if (x > 0) {x * 2.0} end'
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


def test_parse_else(parser):
    given = maramodule('elses', '''
        if (x > 0) { x * 2.0 }
        else { 10.0 }
        20 else 10
    ''')

    expected = n.Module(
        name='elses',
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
            n.Else(
                expr=None,
                body=n.Block(params=[], exprs=[
                    n.Real('10.0')
                ])
            ),
            n.Else(
                expr=n.Int('20'),
                body=n.Int('10'),
            ),
        ],
    )
    result = parser.parse(given)
    assert result == expected


def test_parse_postfix_while(parser):
    given = maramodule('test', '''
        while (x > 0) {x * 2}
    ''')
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


def test_exprs_and_blocks(parser):
    given = '''module blocks
                    block = {
                        x = 10
                        y = x
                        z =
                          5
                        t = 10 +
                            5
                        t = 10 \
                            + 5
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
                        n.Assign(name=n.ValueId('z'), value=n.Int('5'), type_=None),
                        n.Assign(name=n.ValueId('t'), type_=None,
                            value=n.BinOp(
                                func=n.SymbolId('+'),
                                args=[n.Int('10'), n.Int('5')]
                            )
                        ),
                        n.Assign(name=n.ValueId('t'), type_=None,
                            value=n.BinOp(
                                func=n.SymbolId('+'),
                                args=[n.Int('10'), n.Int('5')]
                            )
                        ),


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
    )  # noqa

    result = parser.parse(given)

    assert result.name == expected.name
    assert result.exprs[0].name == expected.exprs[0].name
    assert result.exprs[0].value.exprs[0] == expected.exprs[0].value.exprs[0]
    assert result.exprs[0].value.exprs[1] == expected.exprs[0].value.exprs[1]
    assert result.exprs[0].value.exprs[2] == expected.exprs[0].value.exprs[2]
    assert expected == result


def test_declarations(parser):
    given = '''module declarations
               var x = 10
               val y = 20
               end'''

    expected = n.Module(
        name='declarations',
        exprs=[
            n.Var(name=n.ValueId('x'), value=n.Int('10'), type_=None),
            n.Val(name=n.ValueId('y'), value=n.Int('20'), type_=None),
        ],
    )

    result = parser.parse(given)

    assert expected.exprs[0] == result.exprs[0]
    assert expected.exprs[1] == result.exprs[1]
    assert expected == result


def test_parse_tuples(parser, lex_simple):
    given = maramodule('tuples', '''
        x = ()
        x = (1,)
        x = (1, 2, 3)
    ''')

    expected = n.Module(
        name='tuples',
        exprs=[
            n.Assign(
                name=n.ValueId('x'),
                value=n.Tuple(values=[]),
            ),
            n.Assign(
                name=n.ValueId('x'),
                value=n.Tuple(values=[
                    n.Int('1'),
                ]),
            ),
            n.Assign(
                name=n.ValueId('x'),
                value=n.Tuple(values=[
                    n.Int('1'),
                    n.Int('2'),
                    n.Int('3'),
                ]),
            ),
        ]
    )

    stream = list(lex_simple(given))  # pylint:disable=W0612
    result = parser.parse(given)

    assert expected == result


def test_parse_lists(parser, lex_simple):

    given = maramodule('lists', '''
        x = []
        x = [1, ]
        x = [1, 2, 3]
        [
            (1),
            2,
            3,
        ]
    ''')

    expected = n.Module(
        name='lists',
        exprs=[
            n.Assign(
                name=n.ValueId('x'),
                value=n.List(values=[]),
            ),
            n.Assign(
                name=n.ValueId('x'),
                value=n.List(values=[
                    n.Int('1'),
                ]),
            ),
            n.Assign(
                name=n.ValueId('x'),
                value=n.List(values=[
                    n.Int('1'),
                    n.Int('2'),
                    n.Int('3'),
                ]),
            ),
            n.List(values=[
                n.Int('1'),
                n.Int('2'),
                n.Int('3'),
            ]),
        ]
    )

    stream = list(lex_simple(given))  # pylint:disable=W0612
    result = parser.parse(given)

    assert expected == result


def test_parse_kvs(parser, lex_simple):
    given = maramodule('kvs', '''
        x : 10
        y :
            20
        [x: 10, y: 20]
        [x: 10,
         y:
            20
        ]
    ''')

    expected = n.Module(
        name='kvs',
        exprs=[
            n.KV(key=n.ValueId('x'), value=n.Int('10')),
            n.KV(key=n.ValueId('y'), value=n.Int('20')),
            n.List(values=[
                n.KV(key=n.ValueId('x'), value=n.Int('10')),
                n.KV(key=n.ValueId('y'), value=n.Int('20')),
            ]),
            n.List(values=[
                n.KV(key=n.ValueId('x'), value=n.Int('10')),
                n.KV(key=n.ValueId('y'), value=n.Int('20')),
            ]),
        ]
    )

    stream = list(lex_simple(given))  # pylint:disable=W0612
    result = parser.parse(given)
    assert expected == result


def test_parse_comments(parser):
    given = maramodule('comments', '''
    # asdf
    ## asdf
    ###
    asdf
    qwerty
    ###
    ''')

    expected = n.Module(name='comments', exprs=[
        n.TempComment(' asdf'),
        n.DocComment(' asdf'),
        n.BlockComment('''
    asdf
    qwerty
    '''),
    ])

    result = parser.parse(given)
    assert expected == result


@pytest.mark.xfail
def test_always_fail():
    raise Exception
