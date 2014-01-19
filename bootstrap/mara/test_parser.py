from parser import parser
import node


def test_parse_bottoms():
    assert (
        parser.parse('module test 10 end') ==
        node.Module(name='test', exprs=[
            node.Int(value='10')
        ])
    )

    assert (
        parser.parse('module test 10.0 end') ==
        node.Module(name='test', exprs=[
            node.Real(value='10.0')
        ])
    )

    assert (
        parser.parse('module test 1e10 end') ==
        node.Module(name='test', exprs=[
            node.Sci(value='1e10')
        ])
    )


