def int_parse(tok):
    # Decimal
    if tok.type == 'INTD':
        value = int(tok.value)

    # Hexidecimal
    elif tok.type == 'INTX':
        value = int(tok.value, 16)

    # Pretty Decimal
    elif tok.type == 'INTP':
        value = int(tok.value.replace('_', ''))

    else:
        raise ParseError(
            'Int(Tok(type={0}, value={1})) not understood.'.format(
                tok.type, tok.value
            )
        )


def test_lex_value_identifiers():
    given = '''module
        hello _goodbye
        pizza_sauce num0
        ____pZ0x9 _0
        - + * /
        < > <= => ==
        ~! ~>> ~<<
        ??? !!!
        && ||
        &&= +=
    end'''
    output = list(lex_simple(given))
    assert output == [
        ('MODULE', 'module'),
        ('VID', 'hello'),
        ('VID', '_goodbye'), ('NL', '\n'),
        ('VID', 'pizza_sauce'),
        ('VID', 'num0'), ('NL', '\n'),
        ('VID', '____pZ0x9'),
        ('VID', '_0'),

        ('SID', '<'),
        ('SID', '>'),
        ('SID', '<='),
        ('SID', '=>'),
        ('SID', '=='),
        ('SID', '~!'),
        ('SID', '~>>'),
        ('SID', '~<<'),
        ('SID', '???'),
        ('SID', '!!!'),
        ('SID', '&&'),
        ('SID', '||'),
        ('SID', '&&='),
        ('SID', '+='),
        ('END', 'end'),
    ]

def test_parse_wrapped_if():
    n = None
    given = 'module simple if(x>0){x*2.0} end'
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
