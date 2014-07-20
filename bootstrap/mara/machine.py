
# pylint: disable=R0904
# pylint: disable=R0902

from collections import defaultdict
import special


class Machine(object):
    '''
    A simple, register-based virtual machine.
    '''
    def __init__(self, buffered=False, traced=False):
        self._code = []
        self._regs_buffer = defaultdict(lambda: [None] * 4)
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
        A dictionary copy of the registers for the frame.
        '''
        fp = self._frame_ptr
        frame = self._regs_buffer[fp]

        if self._frame_ptr != 0:
            frame[0] = self._regs_buffer[0][0]

        return {i: r for i, r in enumerate(frame) if r is not None}

    ##########################################################################
    # Internal Functions
    ##########################################################################

    def _load(self, code, constant_pool=None):
        self._code = code
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
        stack_view = []
        for i, elem in enumerate(self._stack):
            fp = 'fp:' if i == self._frame_ptr else ''
            sp = 'sp:' if i == self._stack_ptr else ''
            stack_view.append(fp + sp + str(elem))

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
        Set the value in a register for the current frame.
        '''
        # r0 is sharded by all frames
        if reg == 0:
            fp = 0
        else:
            fp = self._frame_ptr

        # the closest you can get to realloc in python
        if reg >= len(self._regs_buffer[fp]):
            self._regs_buffer[fp] += [None] * max(len(self._regs_buffer), reg)

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
        return special.HALT

    def phi(self, result, left, right):
        '''
        Return the value set by the path taken through the code.
        In the current iteration of the machine, this means the register
        that contains a valid value.
        '''

        left_value = self._get(left)
        right_value = self._get(right)

        if left_value is not None and right_value is None:
            self._set(result, left_value)
            return

        if left_value is None and right_value is not None:
            self._set(result, right_value)
            return

        raise TypeError()

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
    # Jumping
    ##########################################################################

    def jump_r(self, offset):
        '''
        Relative jump a constant offset from the current pc.
        '''
        # -1 to cancel out loop iteration
        self._pc += (offset - 1)

    def jump_a(self, address):
        '''
        Absolute jump to a constant address.
        '''
        # -1 to cancel out loop iteration
        self._pc = (address - 1)

    def jump_rr(self, offset):
        '''
        Jump relatively through a reg offset.
        '''
        offset = self._get(offset)

        # -1 to cancel out loop iteration
        self._pc += (offset - 1)

    def jump_ra(self, address):
        '''
        Jump absolutely to an address store in reg address.
        '''
        address = self._get(address)

        # -1 to cancel out loop iteration
        self._pc = (address - 1)

    ##########################################################################
    # Branching
    ##########################################################################

    def branch_zero(self, pred, jmp_offset):
        '''
        Branch relative if the value in reg pred is zero.
        '''
        if self._get(pred) == 0:
            self._pc += (jmp_offset - 1)  # -1 to cancel loop iteration

    def branch_one(self, pred, jmp_offset):
        '''
        Branch relative if the value in reg pred is not zero.
        '''
        if self._get(pred) == 1:
            self._pc += (jmp_offset - 1)  # -1 to cancel loop iteration

    def branch_eq(self, left, right, jmp_offset):
        '''
        Branch relative if the value in reft left is equal to the value in reg ri ght.
        '''
        if self._get(left) == self._get(right):
            self._pc += (jmp_offset - 1)  # -1 to cancel loop iteration

    def branch_gt(self, left, right, jmp_offset):
        '''
        Branch relative if the value in reg left is greater than the value in reg right.
        '''
        if self._get(left) > self._get(right):
            self._pc += (jmp_offset - 1)  # -1 to cancel loop iteration

    def branch_lt(self, left, right, jmp_offset):
        '''
        Branch relative if the value in reg pred is less than the value in reg right.
        '''
        if self._get(left) < self._get(right):
            self._pc += (jmp_offset - 1)  # -1 to cancel loop iteration

    def branch_gte(self, left, right, jmp_offset):
        '''
        Branch relative if the value in reg pred is
        greater than or equal to the value in reg right.
        '''
        if self._get(left) >= self._get(right):
            self._pc += (jmp_offset - 1)  # -1 to cancel loop iteration

    def branch_lte(self, left, right, jmp_offset):
        '''
        Branch relative if the value in reg pred is
        less than or equal to the value in reg right.
        '''
        if self._get(left) <= self._get(right):
            self._pc += (jmp_offset - 1)  # -1 to cancel loop iteration

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

        # remember new frame_ptr, but don't set it yet to ensure
        # that params are loaded from the correct register frame.
        new_frame_ptr = self._stack_ptr

        # push the arguments
        for param in params:
            self._push(self._get(param))

        # set the new frame pointer
        self._frame_ptr = new_frame_ptr

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
