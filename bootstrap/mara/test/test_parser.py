from .. import parser as parser_module
from .. import node as n

from programs import program_name_resolution

import pytest

# pylint: disable=W0621
# pylint: disable=C0330

xfail = pytest.mark.xfail


def maramodule(name, code):
    return 'module {n} {c} end'.format(n=name, c=code)


@pytest.fixture
def parser():
    return parser_module.Parser()


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


def test_parse_binding(parser):
    given = maramodule('test', '''
        x::y
        X::y
        x::Y
        X::Y
    ''')

    expected = n.Module(name='test', exprs=[
        n.Binding(left=n.ValueId('x'), right=n.ValueId('y')),
        n.Binding(left=n.TypeId('X'), right=n.ValueId('y')),
        n.Binding(left=n.ValueId('x'), right=n.TypeId('Y')),
        n.Binding(left=n.TypeId('X'), right=n.TypeId('Y')),
    ])

    result = parser.parse(given)

    assert expected.exprs[0] == result.exprs[0]
    assert expected.exprs[1] == result.exprs[1]
    assert expected.exprs[2] == result.exprs[2]
    assert expected.exprs[3] == result.exprs[3]
    assert expected == result


def test_parse_function_call(parser):
    given = maramodule('test', '''
        foo(10)
        foo 10
        10.foo
        x.foo
        x.foo 10
        x.foo(3,5)
        foo 10 { 2 + 4}
        x.foo {2 + 4 }
        x.foo 10 { 2 + 4 }
        x.foo(3, 5){2 + 4}
    ''')

    block = n.Block(
        exprs=[n.BinOp(
            func=n.SymbolId('+'),
            args=[n.Int('2'), n.Int('4')],
        )]
    )

    expected = n.Module('test', [
        n.Call(
            func=n.ValueId('foo'),
            arg=n.Tuple([
                n.Int('10'),
            ]),
        ),
        n.Call(
            func=n.ValueId('foo'),
            arg=n.Tuple([
                n.Int('10'),
            ]),
        ),
        n.Call(
            func=n.ValueId('foo'),
            arg=n.Tuple([
                n.Int('10'),
            ]),
        ),
        n.Call(
            func=n.ValueId('foo'),
            arg=n.Tuple([
                n.ValueId('x')
            ]),
        ),
        n.Call(
            func=n.ValueId('foo'),
            arg=n.Tuple(values=[
                n.ValueId('x'),
                n.Int('10'),
            ])
        ),
        n.Call(
            func=n.ValueId('foo'),
            arg=n.Tuple(values=[
                n.ValueId('x'),
                n.Int('3'),
                n.Int('5'),
            ])
        ),
        n.Call(func=n.ValueId('foo'), arg=n.Tuple(values=[n.Int('10')]), block=block),
        n.Call(func=n.ValueId('foo'), arg=n.Tuple(values=[n.ValueId('x')]), block=block),
        n.Call(
            func=n.ValueId('foo'),
            arg=n.Tuple(values=[
                n.ValueId('x'),
                n.Int('10'),
            ]),
            block=block,
        ),
        n.Call(
            func=n.ValueId('foo'),
            arg=n.Tuple(values=[
                n.ValueId('x'),
                n.Int('3'),
                n.Int('5'),
            ]),
            block=block,
        ),
    ])

    result = parser.parse(given)

    assert expected.exprs[0] == result.exprs[0]
    assert expected.exprs[1] == result.exprs[1]
    assert expected.exprs[2] == result.exprs[2]
    assert expected.exprs[3] == result.exprs[3]
    assert expected.exprs[4] == result.exprs[4]
    assert expected.exprs[5] == result.exprs[5]
    assert expected.exprs[6] == result.exprs[6]
    assert expected == result


def test_function_call_if_regression(parser):
    given = maramodule('test', '''
        def bool (x) {
            if x == 0 { true }
            else { false }
        }

        if bool(1) {
            42
        } else {
            99
        }
    ''')

    expected = n.Module(name='test', exprs=[
        n.Def(
            name=n.ValueId(value='bool'),
            param=n.Tuple(values=[n.Param(name=n.ValueId(value='x'), type_=n.InferType())]),
            body=n.Block(exprs=[
                n.If(
                    pred=n.BinOp(args=[n.ValueId(value='x'), n.Int(value='0')], func=n.SymbolId(value='==')),
                    if_body=n.Block(exprs=[n.Bool(value='1')]),
                    else_body=n.Unit(),
                ),
                n.Else(
                    body=n.Block(exprs=[n.Bool(value='0')]),
                    expr=None,
                )
            ]),
            return_type=n.InferType()
        ),
        n.If(
            pred=n.Call(
                arg=n.Tuple(values=[n.Int(value='1')]),
                func=n.ValueId(value='bool'),
            ),
            if_body=n.Block(exprs=[n.Int(value='42')]),
            else_body=n.Block(exprs=[n.Int(value='99')]),
        ),
    ])

    result = parser.parse(given)

    assert expected == result


def test_exprs_parse_assignment(parser):
    given = maramodule('assignment', '''
        a = 10
    ''')

    expected = n.Module('assignment', [
        n.Assign(name=n.ValueId('a'), value=n.Int('10'))
    ])

    result = parser.parse(given)
    assert expected == result

    given = 'module assignment; val a Real = 1.0 end'

    expected = n.Module('assignment', [
        n.Val(name=n.ValueId('a'), value=n.Real('1.0'), type_=n.TypeId('Real'))
    ])

    result = parser.parse(given)
    assert expected == result


def test_parse_booleans(parser):
    given = maramodule('test', '''
        true
        false
    ''')

    expected = n.Module(
        name='test',
        exprs=[
            n.Bool('1'),
            n.Bool('0'),
        ]
    )

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
                if_body=n.BinOp(
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
                if_body=n.Block(
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


def test_parse_simple_control_flow(parser):
    given = maramodule('control_flow', '''
        if 1 < 2 {

            10

        } else {
            20
        }
    ''')

    expected = n.Module(
        name='control_flow',
        exprs=[
            n.If(
                pred=n.BinOp(
                    func=n.SymbolId('<'),
                    args=[
                        n.Int('1'),
                        n.Int('2'),
                    ]
                ),
                if_body=n.Block(
                    exprs=[
                        n.Int('10')
                    ]
                ),
                else_body=n.Block(
                    exprs=[
                        n.Int('20')
                    ]
                ),
            ),
        ]
    )

    result = parser.parse(given)

    print(result.exprs[0])

    assert expected.exprs[0] == result.exprs[0]

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
                if_body=n.Block(
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
                body=n.Block(exprs=[
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
        (x + 2) while (x < 0)
        (x + 2) if (x < 0)
        (x + 2) else (x < 0)

    ''')
    expected = n.Module(
        name='test',
        exprs=[
            n.While(
                pred=n.BinOp(
                    func=n.SymbolId('<'),
                    args=[
                        n.ValueId('x'),
                        n.Int(value='0'),
                    ]
                ),
                body=n.BinOp(
                    func=n.SymbolId('+'),
                    args=[
                        n.ValueId('x'),
                        n.Int(value='2')
                    ]
                ),
            ),
            n.If(
                pred=n.BinOp(
                    func=n.SymbolId('<'),
                    args=[
                        n.ValueId('x'),
                        n.Int(value='0'),
                    ]
                ),
                if_body=n.BinOp(
                    func=n.SymbolId('+'),
                    args=[
                        n.ValueId('x'),
                        n.Int(value='2')
                    ]
                ),
            ),
            n.Else(
                expr=n.BinOp(
                    func=n.SymbolId('+'),
                    args=[
                        n.ValueId('x'),
                        n.Int(value='2'),
                    ]
                ),
                body=n.BinOp(
                    func=n.SymbolId('<'),
                    args=[
                        n.ValueId('x'),
                        n.Int(value='0'),
                    ]
                ),
            ),
        ]
    )

    result = parser.parse(given)
    print expected.exprs[2]
    print result.exprs[2]

    assert expected.exprs[0] == result.exprs[0]
    assert expected.exprs[1] == result.exprs[1]
    assert expected.exprs[2] == result.exprs[2]
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
                    exprs=[
                        n.Assign(name=n.ValueId('x'), value=n.Int('10')),
                        n.Assign(name=n.ValueId('y'), value=n.ValueId('x')),
                        n.Assign(name=n.ValueId('z'), value=n.Int('5')),
                        n.Assign(name=n.ValueId('t'),
                            value=n.BinOp(
                                func=n.SymbolId('+'),
                                args=[n.Int('10'), n.Int('5')]
                            )
                        ),
                        n.Assign(name=n.ValueId('t'),
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
            n.Var(name=n.ValueId('x'), value=n.Int('10'), type_=n.InferType()),
            n.Val(name=n.ValueId('y'), value=n.Int('20'), type_=n.InferType()),
        ],
    )

    result = parser.parse(given)

    assert expected.exprs[0] == result.exprs[0]
    assert expected.exprs[1] == result.exprs[1]
    assert expected == result


def test_definitions(parser):
    given = maramodule('test', '''
        def foo ()
        def foo () Int
        def foo() {}
        def foo(x Int) { 3 + 5 }
        def foo(
            x,
            y
        ) {
            3 +
            5
        }
        def bar(x, y Real) Float { 1000 * 0.9 }

        def Int::foo ()
        def Int::foo () {}
    ''')

    expected = n.Module(
        name='test',
        exprs=[
            n.Def(
                name=n.ValueId('foo'),
                param=n.Tuple([]),
                body=n.Unit(),
            ),
            n.Def(
                name=n.ValueId('foo'),
                param=n.Tuple([]),
                body=n.Unit(),
                return_type=n.TypeId('Int'),
            ),
            n.Def(
                name=n.ValueId('foo'),
                param=n.Tuple([]),
                body=n.Block([]),
            ),
            n.Def(
                name=n.ValueId('foo'),
                param=n.Tuple(values=[
                    n.Param(name=n.ValueId('x'), type_=n.TypeId('Int'))
                ]),
                body=n.Block(exprs=[
                    n.BinOp(func=n.SymbolId('+'), args=[
                        n.Int('3'),
                        n.Int('5'),
                    ])
                ])
            ),
            n.Def(
                name=n.ValueId('foo'),
                param=n.Tuple(values=[
                    n.Param(name=n.ValueId('x')),
                    n.Param(name=n.ValueId('y')),
                ]),
                body=n.Block(exprs=[
                    n.BinOp(func=n.SymbolId('+'), args=[
                        n.Int('3'),
                        n.Int('5'),
                    ])
                ])
            ),
            n.Def(
                name=n.ValueId('bar'),
                param=n.Tuple(values=[
                    n.Param(name=n.ValueId('x')),
                    n.Param(name=n.ValueId('y'), type_=n.TypeId('Real')),
                ]),
                return_type=n.TypeId('Float'),
                body=n.Block(exprs=[
                    n.BinOp(func=n.SymbolId('*'), args=[
                        n.Int('1000'),
                        n.Real('0.9'),
                    ]),
                ])
            ),
            n.Def(
                name=n.Binding(left=n.TypeId('Int'), right=n.ValueId('foo')),
                param=n.Tuple([]),
                body=n.Unit(),
            ),
            n.Def(
                name=n.Binding(left=n.TypeId('Int'), right=n.ValueId('foo')),
                param=n.Tuple([]),
                body=n.Block([]),
            ),
        ],
    )

    result = parser.parse(given)

    assert expected.exprs[0].name == result.exprs[0].name
    assert expected.exprs[0].param == result.exprs[0].param
    assert expected.exprs[0] == result.exprs[0]

    assert expected.exprs[1].name == result.exprs[1].name
    assert expected.exprs[1].param == result.exprs[1].param
    assert expected.exprs[1].body == result.exprs[1].body
    assert expected.exprs[1].return_type == result.exprs[1].return_type

    assert expected == result


def test_parse_tuples(parser):
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

    stream = parser.simple_stream(given)
    result = parser.parse(given)

    assert expected == result


def test_parse_lists(parser):

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

    stream = parser.simple_stream(given)  # pylint:disable=W0612
    result = parser.parse(given)

    assert expected == result


def test_parse_kvs(parser):
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

    stream = parser.simple_stream(given)  # pylint:disable=W0612
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


def test_parse_specifications(parser):
    given = maramodule('test', '''
        proto Compare {
            def foo () {}
            def bar () {}
        }

        proto Compare (T Any) {
            def foo () T {}
            def bar (t T) {}
        }

        trait Qua {
            def foo () {}
            def bar () {}
        }

        trait Qua (T Any) {
            def foo () T {}
            def bar (t T) {}
        }

        object Qua {
            val x Int
            val y Int
        }

        object Qua (T Num) {
            val x T
            val y T
        }
    ''')

    expected = n.Module(name='test',
        exprs=[
            n.Proto(
                name=n.TypeId(value='Compare'),
                body=n.Block(exprs=[
                    n.Def(
                        name=n.ValueId(value='foo'),
                        param=n.Tuple(values=[]),
                        body=n.Block(exprs=[]),
                        return_type=n.InferType()
                    ),
                    n.Def(
                        name=n.ValueId(value='bar'),
                        param=n.Tuple(values=[]),
                        body=n.Block(exprs=[]),
                        return_type=n.InferType()
                    ),
                ]),
                param=n.Tuple(values=[])
            ),
            n.Proto(
                name=n.TypeId(value='Compare'),
                body=n.Block(exprs=[
                    n.Def(
                        body=n.Block(exprs=[]),
                        name=n.ValueId(value='foo'),
                        param=n.Tuple(values=[]),
                        return_type=n.TypeId(value='T')
                    ),
                    n.Def(
                        name=n.ValueId(value='bar'),
                        body=n.Block(exprs=[]),
                        param=n.Tuple(values=[
                            n.Param(
                                name=n.ValueId(value='t'),
                                type_=n.TypeId(value='T')
                            ),
                        ]),
                        return_type=n.InferType())
                ]),
                param=n.Tuple(values=[
                    n.Param(
                        name=n.TypeId(value='T'),
                        type_=n.TypeId(value='Any')
                    ),
                ]),
            ),
            n.Trait(
                name=n.TypeId(value='Qua'),
                body=n.Block(exprs=[
                    n.Def(
                        name=n.ValueId(value='foo'),
                        param=n.Tuple(values=[]),
                        body=n.Block(exprs=[]),
                        return_type=n.InferType()
                    ),
                    n.Def(
                        name=n.ValueId(value='bar'),
                        param=n.Tuple(values=[]),
                        body=n.Block(exprs=[]),
                        return_type=n.InferType()
                    ),
                ]),
                param=n.Tuple(values=[])
            ),
            n.Trait(
                name=n.TypeId(value='Qua'),
                body=n.Block(exprs=[
                    n.Def(
                        body=n.Block(exprs=[]),
                        name=n.ValueId(value='foo'),
                        param=n.Tuple(values=[]),
                        return_type=n.TypeId(value='T')
                    ),
                    n.Def(
                        name=n.ValueId(value='bar'),
                        body=n.Block(exprs=[]),
                        param=n.Tuple(values=[
                            n.Param(
                                name=n.ValueId(value='t'),
                                type_=n.TypeId(value='T')
                            ),
                        ]),
                        return_type=n.InferType())
                ]),
                param=n.Tuple(values=[
                    n.Param(
                        name=n.TypeId(value='T'),
                        type_=n.TypeId(value='Any')
                    ),
                ]),
            ),
            n.Object(
                name=n.TypeId(value='Qua'),
                body=n.Block(exprs=[
                    n.Val(
                        name=n.ValueId(value='x'),
                        value=n.Unit(),
                        type_=n.TypeId('Int'),
                    ),
                    n.Val(
                        name=n.ValueId(value='y'),
                        value=n.Unit(),
                        type_=n.TypeId('Int'),
                    ),
                ]),
                param=n.Tuple(values=[])
            ),
            n.Object(
                name=n.TypeId(value='Qua'),
                body=n.Block(exprs=[
                    n.Val(
                        name=n.ValueId(value='x'),
                        value=n.Unit(),
                        type_=n.TypeId('T'),
                    ),
                    n.Val(
                        name=n.ValueId(value='y'),
                        value=n.Unit(),
                        type_=n.TypeId('T'),
                    ),
                ]),
                param=n.Tuple(values=[
                    n.Param(
                        name=n.TypeId(value='T'),
                        type_=n.TypeId(value='Num')
                    ),
                ]),
            )
        ],
    )

    result = parser.parse(given)

    assert expected == result


def test_name_resolution_program(parser, program_name_resolution):
    ast = parser.parse(program_name_resolution)

    assert ast is not None
