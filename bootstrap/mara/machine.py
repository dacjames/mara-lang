
# pylint: disable=R0904
# pylint: disable=R0902

import functools

from collections import defaultdict
import special
from assembler import Assembler

def builtin_comparison(pred):

    @functools.wraps(pred)
    def func(self, left, right):
        return 1 if pred(self, left, right) else 0

    return builtin_binop(func)


def builtin_binop(func):

    @functools.wraps(func)
    def inner(self, dst, left, right):
        lhs = self._get(left)
        rhs = self._get(right)

        value = func(self, lhs, rhs)
        self._set(dst, value)

    return inner


class Machine(object):
    '''
    A simple, register-based virtual machine.
    '''
    def __init__(self, buffered=False, traced=False):
        self._assembler = Assembler()

        self._code = []
        self._regs_buffer = [None] * 4
        self._pc = 0

        self._stack_buffer = []
        self._stack_ptr = -1
        self._frame_ptr = 0

        self._heaplet = [None] * 8
        self._free_ptr = 0
        self._end_ptr = 7

        self._pool = None  # Constant Pool

        self._print_buffer = []

        self._trace = traced

        def _buffered_print(arg):
            self._print_buffer.append(arg)

        def _raw_print(arg):
            print(arg)

        if buffered:
            self._print = _buffered_print
        else:
            self._print = _raw_print

    ##########################################################################
    # Properties
    ##########################################################################

    @property
    def _stack(self):
        '''
        A list copy of the stack.
        '''
        return self._stack_buffer[:self._stack_ptr+1]

    @property
    def _regs(self):
        '''
        A dictionary copy of the registers.
        '''
        return {i: r for i, r in enumerate(self._regs_buffer) if r is not None}

    ##########################################################################
    # Internal Functions
    ##########################################################################

    def _load(self, code, constant_pool=None):
        self._code = self._assembler.assemble(code)
        self._pool = constant_pool

    def _describe(self):
        '''
        The instruction about to be executed.
        '''
        return '{pc}: {instruction}'.format(
            pc=self._pc,
            instruction=' '.join(str(instruction) for instruction in self._code[self._pc])
        )

    def _describe_result(self):
        '''
        State of the machine after executing an instruction.
        '''
        base_stack = []
        stack_fill = None

        for i, elem in enumerate(self._stack):
            if elem is None:
                if stack_fill is None:
                    stack_fill = [i, i]
                else:
                    stack_fill[1] = i
            else:
                if stack_fill is not None:
                    base_stack.append((None, stack_fill))
                    stack_fill = None

                base_stack.append((i, elem))

        stack_view = []
        for i, elem in base_stack:
            fp = 'fp:' if i == self._frame_ptr else ''
            sp = 'sp:' if i == self._stack_ptr else ''
            elem_str = 'NULL[' + '..'.join(str(e) for e in elem) + ']' if i is None else str(elem)
            stack_view.append(fp + sp + elem_str)

        return '{pc}= {{{regs}}} [{stack}]'.format(
            pc=self._pc,
            regs=', '.join('r{0}:{1}'.format(r, v) for r, v in self._regs.items()),
            stack=', '.join(stack_view),
        )

    def _loop(self):
        '''
        Main Interpretor Loop.
        '''
        if len(self._code) == 0:
            return

        end = len(self._code)
        # iterations = 0

        while self._pc < end:
            # if iterations > 100:
            #     print('max iterations')
            #     break

            if self._trace:
                print(self._describe())

            code = self._code[self._pc]
            bytecode = code[0]

            result = getattr(self, bytecode, self.on_error)(*code[1:])

            if self._trace:
                print(self._describe_result())

            if result is special.HALT:
                break
            else:
                self._pc += 1

            # iterations += 1

    def _set(self, reg, value):
        '''
        Set the value in a register.
        '''
        # the closest you can get to realloc in python
        if reg >= len(self._regs_buffer):
            self._regs_buffer += [None] * max(len(self._regs_buffer), reg)

        self._regs_buffer[reg] = value

    def _get(self, reg):
        '''
        Get the value in a register.
        '''
        return self._regs_buffer[reg]

    def _get_nullable(self, reg):
        '''
        Get the value in a register, if it exists, else return None.
        '''
        if reg < len(self._regs_buffer):
            return self._regs_buffer[reg]
        else:
            return None

    def _allocate(self, size):
        '''
        Allocate a new object in the heap.
        '''
        # prepare for not having Python
        length = self._end_ptr - self._free_ptr

        # Do we have space?  Hit fast path.
        if self._free_ptr + size < length:
            # remeber the start of the chunk
            chunk_ptr = self._free_ptr

            # move the free ptr past the chunk
            self._free_ptr += size

            return chunk_ptr

        # Not enough space? Hit slow path.
        else:
            # allocate more heap space.
            new_length = (length * 2)
            new_heap = [None] * new_length
            self._end_ptr = new_length - 1

            # pythonism: locals are faster than self attributes
            old_heap = self._heaplet

            # copy over existing objects
            for i in range(length):
                new_heap[i] = old_heap[i]

            # replace heaps
            self._heaplet = new_heap

            # recurse to hit the fast path
            return self._allocate(size)

    def _flush(self):
        '''
        Flush the print buffer.
        '''
        for line in self._print_buffer:
            print(line)
        self._print_buffer = []

    def _push(self, arg):
        '''
        Push a value onto the stack.
        '''
        self._stack_ptr += 1
        if self._stack_ptr == -1 or self._stack_ptr == len(self._stack_buffer):
            self._stack_buffer.append(arg)
        else:
            self._stack_buffer[self._stack_ptr] = arg

    def _reserve(self, count):
        stack_size = len(self._stack_buffer)
        self._stack_ptr += count

        if self._stack_ptr >= stack_size:
            # + 1 because the sp refers to the top value on the stack,
            # not the next free space.
            growth = self._stack_ptr - stack_size + 1
            self._stack_buffer += [None] * growth

    def _pop(self):
        '''
        Pop a value off the stack.
        '''
        value = self._stack_buffer[self._stack_ptr]
        self._stack_ptr -= 1
        return value

    ##########################################################################
    # Special Purpose
    ##########################################################################

    def halt(self):
        '''
        End execution of the machine.
        '''
        return special.HALT

    def phi(self, result, left, right):
        '''
        Return the value set by the path taken through the code.
        '''
        lhs = self._get_nullable(left)
        rhs = self._get_nullable(right)

        if lhs is not None and rhs is None:
            return self._set(result, lhs)
        elif lhs is None and rhs is not None:
            return self._set(result, rhs)
        else:
            raise TypeError(left, right)

    def noop(self):
        '''
        Do nothing.
        '''
        pass

    def label(self, name):
        '''
        Skip labels.
        '''
        pass

    ##########################################################################
    # Printing
    ##########################################################################

    def print_const(self, arg):
        '''
        Print a constant value.
        '''
        self._print(repr(arg))

    def print_reg(self, arg):
        '''
        Print a description of a register.
        '''
        self._print('r{i}:{v}'.format(
            i=arg,
            v=repr(self._get(arg)),
        ))

    def print_sym(self, reg):
        '''
        Print a symbol referenced by reg.
        '''
        heaplet = self._heaplet

        # get the pointer
        address = self._get(reg)

        # load the symbol length
        length = heaplet[address]

        # lazy load the symbols' characters
        chars = (heaplet[i] for i in range(1, length + 1))

        # convert to a string for printing
        string = ''.join(chars)

        self._print('r{i}:{a}=>{v}'.format(i=reg, a=address, v=repr(string)))

    ##########################################################################
    # Comparisons
    ##########################################################################

    @builtin_comparison
    def lt(self, left, right):
        return left < right

    @builtin_comparison
    def lte(self, left, right):
        return left <= right

    @builtin_comparison
    def gt(self, left, right):
        return left > right

    @builtin_comparison
    def gte(self, left, right):
        return left >= right

    @builtin_comparison
    def eq(self, left, right):
        return left == right

    @builtin_comparison
    def neq(self, left, right):
        return left != right

    ##########################################################################
    # Math
    ##########################################################################

    @builtin_binop
    def add(self, left, right):
        return left + right

    @builtin_binop
    def sub(self, left, right):
        return left - right

    @builtin_binop
    def mul(self, left, right):
        return left * right

    @builtin_binop
    def div(self, left, right):
        return left // right

    @builtin_binop
    def rem(self, left, right):
        return left % right

    ##########################################################################
    # Jumping
    ##########################################################################

    def jump(self, address):
        '''
        Absolute jump to a constant address.
        '''
        # -1 to cancel out loop iteration
        self._pc = (address - 1)

    def jump_ir(self, offset):
        '''
        Jump relatively through a reg offset.
        '''
        offset = self._get(offset)

        # -1 to cancel out loop iteration
        self._pc += (offset - 1)

    def jump_ia(self, address):
        '''
        Jump absolutely to an address store in reg address.
        '''
        address = self._get(address)

        # -1 to cancel out loop iteration
        self._pc = (address - 1)

    ##########################################################################
    # Branching
    ##########################################################################

    def branch_zero(self, pred, address):
        '''
        Branch to address if the value in reg pred is zero.
        '''
        if self._get(pred) == 0:
            self._pc = (address - 1)  # -1 to cancel loop iteration

    def branch_one(self, pred, address):
        '''
        Branch to address if the value in reg pred is not zero.
        '''
        if self._get(pred) == 1:
            self._pc = (address - 1)  # -1 to cancel loop iteration

    def branch_eq(self, left, right, address):
        '''
        Branch to address if the value in reft left is equal to the value in reg ri ght.
        '''
        if self._get(left) == self._get(right):
            self._pc = (address - 1)  # -1 to cancel loop iteration

    ##########################################################################
    # Register Manipulation
    ##########################################################################

    def copy(self, dst, src):
        '''
        Copy the value from register src into register dst.
        '''
        self._set(dst, self._get(src))

    ##########################################################################
    # Function Call and Return
    ##########################################################################

    def call(self, func, *params):
        '''
        Call a function at absolute address func with a variable number of params.
        '''
        # save the return address
        self._push(self._pc)

        # save the frame pointer
        self._push(self._frame_ptr)

        # set the new frame pointer
        self._frame_ptr = self._stack_ptr

        # push the arguments
        for param in params:
            self._push(self._get(param))

        # jump to the function
        self._pc = func

        # cancel out loop increment
        self._pc -= 1

    def ret(self):
        '''
        Return from a function call, cleaning up the stack before leaving.
        '''
        # saved frame_ptr, return address
        fixed_offset = 2

        # get the return address
        ret_addr = self._stack_buffer[self._frame_ptr - 1]

        # reset the stack_ptr
        self._stack_ptr = self._frame_ptr - fixed_offset

        # restore the old frame_ptr
        self._frame_ptr = self._stack_buffer[self._frame_ptr]

        # jump to the return address
        self._pc = ret_addr

    ##########################################################################
    # Stack Manipulation
    ##########################################################################

    def push(self, src):
        '''
        Push a value from the src register onto the stack.
        '''
        self._push(self._get(src))

    def pop(self, dst):
        '''
        Pop a value off the stack into the dst register.
        '''
        self._set(dst, self._pop())

    def peak(self, dst, offset=0):
        '''
        Load a value from the stack.
        '''
        self._set(dst, self._stack_buffer[self._stack_ptr - offset])

    def reserve(self, count):
        '''
        Reserves space for storing count number of variables.
        '''
        self._reserve(count)

    def save(self, *regs):
        '''
        Save the registers onto the stack.
        '''
        for reg in reversed(regs):
            self._push(self._get_nullable(reg))
        # values = [self._get_nullable(r) for r in regs]
        # self._push(values)

    def restore(self, *regs):
        '''
        Restore saved registers from the stack.
        '''
        for reg in regs:
            self._set(reg, self._pop())
        # values = self._pop()
        # for i, reg in enumerate(regs):
        #     self._set(reg, values[i])

    ##########################################################################
    # Allocation
    ##########################################################################

    def new_sym(self, dst, sym):
        '''
        Allocate a new symbol and store the pointer in reg dst.
        '''
        length = len(sym)

        # allocate space for the symbol +1 from the length
        chunk = self._allocate(length + 1)

        # store the symbol length
        self._heaplet[chunk] = length

        # store the symbol characters (+1 for the length)
        for i, char in enumerate(sym):
            self._heaplet[chunk + i + 1] = char

        # store the pointer
        self._set(dst, chunk)

    def new_chunk(self, dst, size):
        '''
        Allocate a new chunk of memory and return the pointer in reg dst.
        '''
        chunk = self._allocate(size)
        self._set(dst, chunk)

    ##########################################################################
    # Load & Store
    ##########################################################################

    def load_v(self, reg, value):
        '''
        Load an embedded value into a register.
        '''
        self._set(reg, value)

    def load_c(self, reg, index):
        '''
        Load a constant at index in the constant pool into register reg.
        '''
        self._set(reg, self._pool[index])

    def load_p(self, dst, index):
        '''
        Load a function parameter in a register.
        '''
        # index start at zero, but frame_ptr points to saved frame_ptr
        offset = index + 1

        # get the value
        value = self._stack_buffer[self._frame_ptr + offset]

        # load the value into a register
        self._set(dst, value)

    def load_d(self, dst, ptr):
        '''
        Directly load memory referenced by reg ptr into reg dst.
        '''
        address = self._get(ptr)
        value = self._heaplet[address]
        self._set(dst, value)

    def load_i(self, dst, ptr, offset):
        '''
        Indirectly load memory referenced by reg ptr plus constant offset into reg dst.
        '''
        address = self._get(ptr) + offset
        value = self._heaplet[address]
        self._set(dst, value)

    def store_p(self, src, index):
        '''
        Store the value in reg src at the parameter index.
        '''
        offset = index + 1

        self._stack_buffer[self._frame_ptr + offset] = self._get(src)

    def store_d(self, src, ptr):
        '''
        Directly store the value in reg src into the memory addressed by reg ptr.
        '''
        address = self._get(ptr)
        value = self._get(src)
        self._heaplet[address] = value

    def store_i(self, src, ptr, offset):
        '''
        Indirectly store the value in reg src into the memory addressed by reg ptr
        plus constant offset.
        '''
        address = self._get(ptr) + offset
        value = self._get(src)
        self._heaplet[address] = value

    def store_c(self, ptr, value):
        '''
        Directly store a constant value in the memory addressed by reg ptr.
        '''
        address = self._get(ptr)
        self._heaplet[address] = value

    def on_error(self, *args):
        print('error: ' + repr(args))
        return special.HALT
