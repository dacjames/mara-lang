import pytest

from ..machine import Machine

# pylint: disable=W0621
# pylint: disable=W0212


class r(int):
    '''
    Just a convenience class to make the bytecode easier to read.
    '''
    pass


@pytest.fixture
def machine():
    return Machine(buffered=True, traced=True)


def test_simple_machine(machine):
    machine._load([
        ['print_const', 0],
        ['print_const', 1],
        ['load_const', r(0), 1],
        ['print_reg', r(0)],
        ['add_rc', r(0), r(0), 1],
        ['add_rr', r(1), r(0), r(0)],
        ['print_reg', r(0)],
        ['print_reg', r(1)],
        ['new_sym', r(2), 'hello, world'],
        ['print_object', r(2)],
        ['add_rc', r(1), r(1), 10],
        ['add_rc', r(1), r(1), -10],
        ['print_reg', r(1)],
        ['branch_gte', r(1), -3],
        ['halt'],
    ])

    machine._loop()

    assert machine._print_buffer == [
        '0',
        '1',
        'r0:1',
        'r0:2',
        'r1:4',
        "r2:0=>'hello, world'",
        'r1:4',
        'r1:-6',
    ]


def test_stack_manipulation(machine):
    machine._load([
        ['load_const', r(0), 0],
        ['push', r(0)],
        ['load_const', r(0), 1],
        ['print_reg', r(0)],
        ['load_stack', r(0)],
        ['print_reg', r(0)],
        ['add_rc', r(0), r(0), 1],
        ['push', r(0)],
        ['add_rc', r(0), r(0), 1],
        ['push', r(0)],
        ['add_rc', r(0), r(0), 1],
        ['push', r(0)],
        ['pop', r(0)],
        ['load_stack', r(1)],
        ['load_stack', r(2), 1],
        ['print_reg', r(1)],
        ['print_reg', r(2)],
        ['halt'],
    ])

    machine._loop()

    assert machine._stack == [0, 1, 2]

    assert machine._print_buffer == [
        'r0:1',
        'r0:0',
        'r1:2',
        'r2:1',
    ]


def test_function_calls(machine):
    machine._load([
        # main { print f(6) }
        ['load_const', r(0), 6],
        ['load_const', r(1), 99],
        ['call', 10, r(0)],
        ['print_reg', r(0)],
        ['print_reg', r(1)],
        ['halt'],
        # g(x, y) { x + y }
        ['load_param', r(1), 0],        # r1 = load x
        ['load_param', r(2), 1],        # r2 = load y
        ['add_rr', r(0), r(1), r(2)],   # r0 = x + y
        ['ret'],
        # f(x) { a = g(x, 10); g(a, a) }
        ['load_param', r(1), 0],        # r1 = load x
        ['load_const', r(2), 10],       # r2 = load 10
        ['call', 6, r(1), r(2)],        # r0 = g(r1, r2)
        ['add_rc', r(1), r(0), 0],      # r1 = r0 + 0
        ['call', 6, r(1), r(1)],        # r0 = call(r1, r1)
        ['ret'],
    ])

    machine._loop()

    assert machine._print_buffer == [
        'r0:32',
        'r1:99',
    ]
