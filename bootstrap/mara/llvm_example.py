#!/usr/bin/env python
from __future__ import print_function

# Import the llvmpy modules.
from llvm import *
from llvm.core import *
from llvm.ee import *

# Create an (empty) module.
mara_module = Module.new('mara_module')

# All the types involved here are "int"s. This type is represented
# by an object of the llvm.core.Type class:
ty_int = Type.int()     # by default 32 bits

OPS = {
    '+': 'add',
    '*': 'mul',
}

def binop (
    name,
    op,
    left_name, left_type,
    right_name, right_type,
    return_type,
):
    function_type = Type.function(return_type, [left_type, right_type])
    function = mara_module.add_function(function_type, name)

    function.args[0].name = left_name
    function.args[1].name = right_name

    block = function.append_basic_block("entry")
    builder = Builder.new(block)

    result = getattr(builder, OPS[op])(function.args[0], function.args[1], "result")
    builder.ret(result)
    return function

add_func = binop(
    name='add',
    op='+',
    left_name='a', left_type=Type.int(),
    right_name='b', right_type=Type.int(),
    return_type=Type.int(),
)

times_func = binop(
    name='times',
    op='*',
    left_name='a', left_type=Type.int(),
    right_name='b', right_type=Type.int(),
    return_type=Type.int(),
)



print(mara_module)

ee = ExecutionEngine.new(mara_module)

arg1 = GenericValue.int(ty_int, 100)
arg2 = GenericValue.int(ty_int, 42)

retval = ee.run_function(add_func, [arg1, arg2])
print("returned", retval.as_int())
