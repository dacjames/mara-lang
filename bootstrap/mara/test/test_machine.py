import pytest

from ..machine import Machine, Register

# pylint: disable=W0621
# pylint: disable=W0212

r = Register


@pytest.fixture
def machine():
    return Machine(buffered=True)


def test_machine(machine):
    machine._load([
        ['print_const', 0],
        ['print_const', 1],
        ['load_const', r(0), 1],
        ['print_reg', r(0)],
        ['add_rc', r(0), r(0), 1],
        ['add_rr', r(1), r(0), r(0)],
        ['print_reg', r(0)],
        ['print_reg', r(1)],
        ['new_str', r(2), 'hello, world'],
        ['print_object', r(2)],
        ['add_rc', r(1), r(1), 10],
        ['add_rc', r(1), r(1), -10],
        ['print_reg', r(1)],
        ['branch_gte', r(1), -3],
        ['halt'],
    ])

    machine._loop()

    assert machine.buffer == [
        '0',
        '1',
        'r0:1',
        'r0:2',
        'r1:4',
        "r2:0=>'hello, world'",
        'r1:4',
        'r1:-6',
    ]
