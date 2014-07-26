import os
import os.path

import pytest

def _locate_program(name):
    directory = os.path.dirname(__file__)
    program_path = os.path.join(directory, name)
    return program_path

def _read_program(name):
    program = _locate_program(name)
    with open(program, 'r') as f:
        return f.read()

@pytest.fixture
def program_name_resolution():
    return _read_program('name_resolution.mara')
