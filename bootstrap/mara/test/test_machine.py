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
        ['load_v', r(0), 1],
        ['print_reg', r(0)],
        ['load_v', r(42), 1],
        ['add', r(0), r(0), r(42)],
        ['add', r(1), r(0), r(0)],
        ['print_reg', r(0)],
        ['print_reg', r(1)],
        ['new_sym', r(2), 'hello, world'],
        ['print_sym', r(2)],
        ['load_v', r(42), 10],
        ['add', r(1), r(1), r(42)],
        ['load_v', r(42), -10],
        ['add', r(1), r(1), r(42)],
        ['print_reg', r(1)],
        ['load_v', r(3), 0],
        ['branch_gte', r(1), r(3), -3],
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


def test_jumps(machine):
    machine._load([
        ['jump_r', 8],          # jump to a
        ['load_v', r(0), 0],    # label x
        ['jump_r', 7],          # jump to b
        ['load_v', r(1), 1],    # label y
        ['jump_r', 7],          # jump to c
        ['load_v', r(2), 2],    # label z
        ['jump_r', 7],          # jump to end
        ['jump_r', 0],          # better never get here!
        ['jump_a', 1],          # label a, jump to x
        ['load_v', r(3), 3],    # label b
        ['jump_ra', r(3)],      # jump to y
        ['load_v', r(4), -7],   # label c
        ['jump_rr', r(4)],      # jump to z
        ['print_reg', r(0)],    # label end
        ['print_reg', r(1)],
        ['print_reg', r(2)],
        ['halt'],
    ])

    machine._loop()

    assert machine._print_buffer == [
        'r0:0',
        'r1:1',
        'r2:2',
    ]


def test_branches(machine):
    machine._load([
        ['load_v', r(0), 0],
        ['load_v', r(1), 1],
        ['load_v', r(2), 0],
        ['branch_lt', r(1), r(0), 22],    # branch to error
        ['branch_lt', r(2), r(0), 21],    # branch to error
        ['branch_lt', r(0), r(1), 22],    # branch to good
        ['branch_lte', r(1), r(0), 19],   # branch to error
        ['branch_lte', r(0), r(2), 1],
        ['branch_lte', r(0), r(1), 19],   # branch to good
        ['branch_gt', r(0), r(1), 16],    # branch to error
        ['branch_gt', r(0), r(2), 15],    # branch to error
        ['branch_gt', r(1), r(0), 16],    # branch to good
        ['branch_gte', r(0), r(1), 13],   # branch to error
        ['branch_gte', r(0), r(2), 1],
        ['branch_gte', r(1), r(0), 13],   # branch to good
        ['branch_zero', r(1), 10],
        ['branch_zero', r(0), 11],
        ['branch_one', r(0), 8],
        ['branch_one', r(1), 9],
        ['jump_r', 6],                    # jump to success
        ['jump_a', 6],                    # jump to lte test
        ['jump_a', 9],                    # jump to gt test
        ['jump_a', 12],                   # jump to gte test
        ['jump_a', 15],                   # jump to zero test
        ['jump_a', 17],                   # jump to one test
        ['load_v', r(99), 0],             # failure
        ['jump_r', 2],
        ['load_v', r(99), 1],             # success
        ['print_reg', r(99)],
    ])

    machine._loop()

    assert machine._print_buffer == [
        'r99:1'
    ]


def test_stack_manipulation(machine):
    machine._load([
        ['load_v', r(0), 0],
        ['push', r(0)],
        ['load_v', r(0), 1],
        ['print_reg', r(0)],
        ['peak', r(0)],
        ['print_reg', r(0)],
        ['load_v', r(42), 1],
        ['add', r(0), r(0), r(42)],
        ['push', r(0)],
        ['load_v', r(42), 1],
        ['add', r(0), r(0), r(42)],
        ['push', r(0)],
        ['load_v', r(42), 1],
        ['add', r(0), r(0), r(42)],
        ['push', r(0)],
        ['pop', r(0)],
        ['peak', r(1)],
        ['peak', r(2), 1],
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


def test_int_math(machine):
    machine._load([
        ['load_v', r(0), 10],
        ['load_v', r(1), 20],
        ['load_v', r(2), 33],
        ['load_v', r(42), 2],
        ['add', r(4), r(0), r(42)],
        ['print_reg', r(4)],
        ['add', r(4), r(0), r(1)],
        ['print_reg', r(4)],
        ['load_v', r(42), 20],
        ['sub', r(4), r(0), r(42)],
        ['print_reg', r(4)],
        ['sub', r(4), r(2), r(1)],
        ['print_reg', r(4)],
        ['load_v', r(42), 2],
        ['mul', r(4), r(0), r(42)],
        ['print_reg', r(4)],
        ['mul', r(4), r(0), r(2)],
        ['print_reg', r(4)],
        ['load_v', r(42), 2],
        ['div', r(4), r(0), r(42)],
        ['print_reg', r(4)],
        ['load_v', r(42), 20],
        ['div', r(4), r(0), r(42)],
        ['print_reg', r(4)],
        ['div', r(4), r(2), r(0)],
        ['print_reg', r(4)],
        ['div', r(4), r(1), r(0)],
        ['print_reg', r(4)],
        ['load_v', r(42), 3],
        ['rem', r(4), r(0), r(42)],
        ['print_reg', r(4)],
        ['rem', r(4), r(2), r(0)],
        ['print_reg', r(4)],
        ['halt'],
    ])

    machine._loop()

    assert machine._print_buffer == [
        'r4:12',
        'r4:30',
        'r4:-10',
        'r4:13',
        'r4:20',
        'r4:330',
        'r4:5',
        'r4:0',
        'r4:3',
        'r4:2',
        'r4:1',
        'r4:3',
    ]

def test_comparisons(machine):

    machine._load([
        ['load_v', r(0), 0],
        ['load_v', r(1), 1],
        ['lt', r(3), r(0), r(1)],
        ['lt', r(13), r(1), r(1)],
        ['lt', r(23), r(1), r(0)],
        ['lte', r(4), r(0), r(1)],
        ['lte', r(14), r(1), r(1)],
        ['lte', r(24), r(1), r(0)],
        ['gt', r(5), r(0), r(1)],
        ['gt', r(15), r(1), r(1)],
        ['gt', r(25), r(1), r(0)],
        ['gte', r(6), r(0), r(1)],
        ['gte', r(16), r(1), r(1)],
        ['gte', r(26), r(1), r(0)],
        ['eq', r(7), r(0), r(1)],
        ['eq', r(17), r(1), r(1)],
        ['eq', r(27), r(1), r(0)],
        ['neq', r(8), r(0), r(1)],
        ['neq', r(18), r(1), r(1)],
        ['neq', r(28), r(1), r(0)],
        ['print_reg', r(3)],
        ['print_reg', r(13)],
        ['print_reg', r(23)],
        ['print_reg', r(4)],
        ['print_reg', r(14)],
        ['print_reg', r(24)],
        ['print_reg', r(5)],
        ['print_reg', r(15)],
        ['print_reg', r(25)],
        ['print_reg', r(6)],
        ['print_reg', r(16)],
        ['print_reg', r(26)],
        ['print_reg', r(7)],
        ['print_reg', r(17)],
        ['print_reg', r(27)],
        ['print_reg', r(8)],
        ['print_reg', r(18)],
        ['print_reg', r(28)],

        ['halt'],
    ])

    machine._loop()

    assert machine._print_buffer == [
        'r3:1', 'r13:0', 'r23:0',
        'r4:1', 'r14:1', 'r24:0',
        'r5:0', 'r15:0', 'r25:1',
        'r6:0', 'r16:1', 'r26:1',
        'r7:0', 'r17:1', 'r27:0',
        'r8:1', 'r18:0', 'r28:1',
    ]




def test_function_calls(machine):
    machine._load([
        # main { print f(6) }
        ['load_v', r(0), 6],
        ['load_v', r(1), 99],
        ['call', 10, r(0)],
        ['print_reg', r(0)],
        ['print_reg', r(1)],
        ['halt'],
        # g(x, y) { x + y }
        ['load_p', r(11), 0],               # r11 = load x
        ['load_p', r(12), 1],               # r12 = load y
        ['add', r(0), r(11), r(12)],     # r0 = x + y
        ['ret'],
        # f(x) { a = g(x, 10); g(a, a) }
        ['load_p', r(21), 0],               # r1 = load x
        ['load_v', r(22), 10],              # r2 = load 10
        ['call', 6, r(21), r(22)],          # r0 = g(r21, r22)
        ['copy', r(21), r(0)],              # r1 = r0
        ['call', 6, r(21), r(21)],          # r0 = g(r21, r21)
        ['ret'],
    ])

    machine._loop()

    assert machine._print_buffer == [
        'r0:32',
        'r1:99',
    ]


def test_heap(machine):
    machine._load([
        ['new_chunk', r(0), 8],
        ['load_v', r(42), 1],
        ['add', r(1), r(0), r(42)],
        ['load_v', r(42), 2],
        ['add', r(2), r(0), r(42)],
        ['load_v', r(42), 3],
        ['add', r(3), r(0), r(42)],
        ['store_c', r(0), 4],
        ['store_c', r(1), 5],

        ['load_v', r(20), 6],
        ['store_d', r(20), r(2)],
        ['load_v', r(20), 7],
        ['store_d', r(20), r(3)],

        ['load_v', r(20), 8],
        ['store_i', r(20), r(0), 4],
        ['load_v', r(20), 9],
        ['store_i', r(20), r(0), 5],
        ['load_v', r(20), 10],
        ['store_i', r(20), r(0), 6],
        ['load_v', r(20), 11],
        ['store_i', r(20), r(0), 7],

        ['load_d', r(4), r(0)],
        ['load_d', r(5), r(1)],
        ['load_d', r(6), r(2)],
        ['load_d', r(7), r(3)],
        ['load_i', r(8), r(0), 4],
        ['load_i', r(9), r(0), 5],
        ['load_i', r(10), r(0), 6],
        ['load_i', r(11), r(0), 7],
    ] + [
        ['print_reg', r(n)] for n in range(12)
    ] + [
        ['halt'],
    ])

    machine._loop()

    assert machine._print_buffer == [
        'r0:0',
        'r1:1',
        'r2:2',
        'r3:3',
        'r4:4',
        'r5:5',
        'r6:6',
        'r7:7',
        'r8:8',
        'r9:9',
        'r10:10',
        'r11:11',
    ]


def test_copy(machine):
    machine._load([
        ['load_v', r(1), 10],
        ['copy', r(2), r(1)],
        ['print_reg', r(1)],
        ['print_reg', r(2)],
    ])

    machine._loop()

    assert machine._print_buffer == [
        'r1:10',
        'r2:10',
    ]
