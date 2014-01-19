def int_parse(tok):
    if tok.type == 'INTD': # Decimal
        value = int(tok.value)

    elif tok.type == 'INTX': # Hexidecimal
        value = int(tok.value, 16)

    elif tok.type == 'INTP': # Pretty Decimal
        value = int(tok.value.replace('_', ''))

    else:
        raise ParseError(
            'Int(Tok(type={0}, value={1})) not understood.'.format(
                tok.type, tok.value
            )
        )
