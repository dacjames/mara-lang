
# pylint: disable=R0904
# pylint: disable=R0902

from collections import defaultdict


HALT = object()


class Machine(object):
    '''
    A simple, register-based virtual machine.
    '''
    def __init__(self, buffered=False, traced=False):
        self._code = []
        self._regs_buffer = defaultdict(lambda: [])
        self._pc = 0

        self._stack_buffer = []
        self._stack_ptr = -1
        self._frame_ptr = 0

        self._heaplet = []

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
        A dictionary copy of the registers for the frame.
        '''
        fp = self._frame_ptr

        if self._frame_ptr == 0:
            frame = self._regs_buffer[fp]
        else:
            frame = [self._regs_buffer[0][0]] + self._regs_buffer[fp]

        return {i: r for i, r in enumerate(frame) if r is not None}

    ##########################################################################
    # Internal Functions
    ##########################################################################

    def _load(self, code):
        self._code = code

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
        return '{pc}= {{{regs}}} {stack}'.format(
            pc=self._pc,
            regs=', '.join('r{0}:{1}'.format(r, v) for r, v in self._regs.items()),
            stack=list(reversed(self._stack)),
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

            if result is HALT:
                break
            else:
                self._pc += 1

            # iterations += 1

    def _set(self, reg, value):
        '''
        Set the value in a register for the current frame.
        '''

        # r0 is sharded by all frames
        if reg == 0:
            fp = 0
        else:
            fp = self._frame_ptr

        # the closest you can get to realloc in python
        if reg >= len(self._regs_buffer[fp]):
            self._regs_buffer[fp] += ([None] * max(len(self._regs_buffer), 8))

        self._regs_buffer[fp][reg] = value

    def _get(self, reg):
        '''
        Get the value in a regester for the current frame.
        '''
        # r0 is sharded by all frames
        if reg == 0:
            fp = 0
        else:
            fp = self._frame_ptr

        return self._regs_buffer[fp][reg]

    def _allocate(self, obj):
        '''
        Allocate a new object in the heap.
        '''
        index = len(self._heaplet)
        self._heaplet.append(obj)
        return index

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
        if self._stack_ptr == len(self._stack_buffer):
            self._stack_buffer.append(arg)
        else:
            self._stack_buffer[self._stack_ptr] = arg

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
        return HALT

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

    def print_object(self, reg):
        '''
        Print an object referenced by reg.
        '''
        address = self._get(reg)
        value = self._heaplet[address]
        self._print('r{i}:{a}=>{v}'.format(i=reg, a=address, v=repr(value)))

    ##########################################################################
    # Math
    ##########################################################################

    def add_rc(self, dst, left, right):
        '''
        Add the value in reg left to the constant right and store the result in dst.
        '''
        self._set(dst, self._get(left) + right)

    def add_rr(self, dst, left, right):
        '''
        Add the value in reg left to the value in reg right and store the result in dst.
        '''
        self._set(dst, self._get(left) + self._get(right))

    def sub_rc(self, dst, left, right):
        '''
        Subtract the constant right from the value in reg left and store the result in dst.
        '''
        self._set(dst, self._get(left) - right)

    def sub_rr(self, dst, left, right):
        '''
        Subtract the the value in reg right from the value in reg left and store the result in dst.
        '''
        self._set(dst, self._get(left) - self._get(right))

    def mul_rc(self, dst, left, right):
        '''
        Multiply the the value in reg left by the constant right and store the result in dst.
        '''
        self._set(dst, self._get(left) * right)

    def mul_rr(self, dst, left, right):
        '''
        Multiply the the value in reg left by the value in reg right and store the result in dst.
        '''
        self._set(dst, self._get(left) * self._get(right))

    def div_rc(self, dst, left, right):
        '''
        Divide the the value in reg left by the constant left and store the result in dst.
        Truncates to an integer result.
        '''
        self._set(dst, self._get(left) // right)

    def div_rr(self, dst, left, right):
        '''
        Divide the the value in reg left from the value in reg right and store the result in dst.
        Truncates to an integer result.
        '''
        self._set(dst, self._get(left) // self._get(right))

    def rem_rc(self, dst, left, right):
        '''
        Compute the remainder of the the value in reg left divided bv the constant left
        and store the result in dst.
        '''
        self._set(dst, self._get(left) % right)

    def rem_rr(self, dst, left, right):
        '''
        Compute the remainder of value in reg left divided by the value in reg right
        and store the result in dst.
        '''
        self._set(dst, self._get(left) % self._get(right))

    ##########################################################################
    # Branching
    ##########################################################################

    def branch_zero(self, pred, jmp_offset):
        '''
        Branch relative if the value in reg pred is zero.
        '''
        if self._get(pred) == 0:
            self._pc += jmp_offset

    def branch_nonzero(self, pred, jmp_offset):
        '''
        Branch relative if the value in reg pred is not zero.
        '''
        if self._get(pred) != 0:
            self._pc += jmp_offset

    def branch_gt(self, left, right, jmp_offset):
        '''
        Branch relative if the value in reg left is greater than the value in reg right.
        '''
        if self._get(left) > self._get(right):
            self._pc += jmp_offset

    def branch_lt(self, left, right, jmp_offset):
        '''
        Branch relative if the value in reg pred is less than the value in reg right.
        '''
        if self._get(left) < self._get(right):
            self._pc += jmp_offset

    def branch_gte(self, left, right, jmp_offset):
        '''
        Branch relative if the value in reg pred is
        greater than or equal to the value in reg right.
        '''
        if self._get(left) >= self._get(right):
            self._pc += jmp_offset

    def branch_lte(self, left, right, jmp_offset):
        '''
        Branch relative if the value in reg pred is
        less than or equal to the value in reg right.
        '''
        if self._get(left) <= self._get(right):
            self._pc += jmp_offset

    ##########################################################################
    # Function Call and Return
    ##########################################################################

    def call(self, func, *params):
        '''
        Call a function at absolute address func with a variable number of params.
        '''
        # push arguments
        for param in params:
            self._push(self._get(param))

        # store the number of params
        # this is a stopgap until we have function type information
        self._push(len(params))

        # save the return address
        self._push(self._pc)

        # save the frame pointer
        self._push(self._frame_ptr)

        # set the new frame pointer
        self._frame_ptr = self._stack_ptr

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

        # number of parameters
        param_offset = self._stack_buffer[self._frame_ptr - fixed_offset]

        # resest the stack_ptr, -1 for the param count
        self._stack_ptr = self._frame_ptr - fixed_offset - 1 - param_offset

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

    ##########################################################################
    # Allocation
    ##########################################################################

    def new_sym(self, dst, value):
        '''
        Allocate a new symbol and store the pointer in reg dst.
        '''
        self._set(dst, self._allocate(value))

    def new_chunk(self, dst, size):
        '''
        Allocate a new chunk of memory and return the pointer in reg dst.
        '''
        chunk = [None] * size
        self._set(dst, self._allocate(chunk))

    ##########################################################################
    # Loading
    ##########################################################################

    def load_const(self, reg, value):
        '''
        Load a constant number into a register.
        '''
        self._set(reg, value)

    def load_param(self, dst, index):
        '''
        Load a function parameter in a register.
        '''
        # saved frame_ptr, return address, num_params
        fixed_offset = 3

        # compute the negative offset
        offset = fixed_offset + index

        # load the value into a register
        self._set(dst, self._stack_buffer[self._frame_ptr - offset])

    def on_error(self, *args):
        print('error: ' + repr(args))
        return HALT
