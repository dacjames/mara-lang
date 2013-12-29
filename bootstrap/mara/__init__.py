###########################################################
# Grammar CLI
###########################################################

cli.option('-g --grammar_file=<f> Grammar File.')


@cli.cmd('load [options]')
def load_grammar(grammar_file):
    print grammar(grammar_file)

@cli.cmd('parse [options] <src_file>')
def parse(src_file, grammar_file):
    with open(src_file) as srcf:
        json_data = srcf.read()
    print 'Input'
    print '#=#==#=*=#====#==*==#====#=*=#==#=#'
    print json_data
    print 'Output'
    print '#=#==#=*=#====#==*==#====#=*=#==#=#'
    result = JSON_Transformer().transform(
        grammar(grammar_file).parse(json_data)
    )
    import pprint
    pprint.pprint(result)

if __name__ == '__main__':
    cli.main()
