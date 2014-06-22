
# pylint: disable=R0904
# pylint: disable=R0902

from collections import defaultdict


halt_canary = object()


class Register(int):
    pass


class Machine(object):
    def __init__(self, buffered=False, traced=False):
        self._code = []
        self._regs_buffer = defaultdict(lambda: [])
        self._pc = 0

        self._stack_buffer = []
        self._stack_ptr = -1
        self._frame_ptr = 0

        self._heaplet = []
        self._heap_ptr = -1

        self._root_scope = {}

        self._buffer = []

        self._trace = traced

        def _buffered_print(arg):
            self._buffer.append(arg)

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
        return self._stack_buffer[:self._stack_ptr+1]

    @property
    def _regs(self):
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
        return '{pc}: {instruction}'.format(
            pc=self._pc,
            instruction=' '.join(str(instruction) for instruction in self._code[self._pc])
        )

    def _describe_result(self):
        return '{pc}= {{{regs}}} {stack}'.format(
            pc=self._pc,
            regs=', '.join('r{0}:{1}'.format(r, v) for r, v in self._regs.items()),
            stack=list(reversed(self._stack)),
        )

    def _loop(self):
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

            if result is halt_canary:
                break
            else:
                self._pc += 1

            # iterations += 1

    def _set(self, reg, value):

        # r0 is sharded by all frames
        if reg == 0:
            fp = 0
        else:
            fp = self._frame_ptr

        if reg >= len(self._regs_buffer[fp]):
            self._regs_buffer[fp] += ([None] * max(len(self._regs_buffer), 8))
        self._regs_buffer[fp][reg] = value

    def _get(self, reg):

        # r0 is sharded by all frames
        if reg == 0:
            fp = 0
        else:
            fp = self._frame_ptr

        return self._regs_buffer[fp][reg]

    def _allocate(self, obj):
        index = len(self._heaplet)
        self._heaplet.append(obj)
        return index

    def _flush(self):
        for line in self._buffer:
            print(line)
        self._buffer = []

    def _push(self, arg):
        self._stack_ptr += 1
        if self._stack_ptr == len(self._stack_buffer):
            self._stack_buffer.append(arg)
        else:
            self._stack_buffer[self._stack_ptr] = arg

    def _pop(self):
        value = self._stack_buffer[self._stack_ptr]
        self._stack_ptr -= 1
        return value

    ##########################################################################
    # Op Codes
    ##########################################################################

    def print_const(self, arg):
        self._print(repr(arg))

    def print_reg(self, arg):
        self._print('r{i}:{v}'.format(
            i=arg,
            v=repr(self._get(arg)),
        ))

    def print_object(self, reg):
        address = self._get(reg)
        value = self._heaplet[address]
        self._print('r{i}:{a}=>{v}'.format(i=reg, a=address, v=repr(value)))

    def halt(self):
        return halt_canary

    def load_const(self, reg, value):
        self._set(reg, value)

    def add_cc(self, dst, left, right):
        self._set(dst, left + right)

    def add_rc(self, dst, left, right):
        self._set(dst, self._get(left) + right)

    def add_rr(self, dst, left, right):
        self._set(dst, self._get(left) + self._get(right))

    def new_str(self, dst, value):
        self._set(dst, self._allocate(value))

    def branch_zero(self, pred, jmp_offset):
        if self._get(pred) == 0:
            self._pc += jmp_offset

    def branch_nonzero(self, pred, jmp_offset):
        if self._get(pred) != 0:
            self._pc += jmp_offset

    def branch_gt(self, pred, jmp_offset):
        if self._get(pred) > 0:
            self._pc += jmp_offset

    def branch_lt(self, pred, jmp_offset):
        if self._get(pred) < 0:
            self._pc += jmp_offset

    def branch_gte(self, pred, jmp_offset):
        if self._get(pred) >= 0:
            self._pc += jmp_offset

    def branch_lte(self, pred, jmp_offset):
        if self._get(pred) <= 0:
            self._pc += jmp_offset

    def call(self, func, *params):
        '''Call a function at address func with a variable number of params
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

    def load_param(self, dst, index):
        # saved frame_ptr, return address, num_params
        fixed_offset = 3

        # compute the negative offset
        offset = fixed_offset + index

        # load the value into a register
        self._set(dst, self._stack_buffer[self._frame_ptr - offset])

    def push(self, src):
        '''Push a value from the src register onto the stack.
        '''
        self._push(self._get(src))

    def pop(self, dst):
        '''Pop a value off the stack into the dst register.
        '''
        self._set(dst, self._pop())

    def load_stack(self, dst, offset=0):
        '''Load a value from the stack
        '''
        self._set(dst, self._stack_buffer[self._stack_ptr - offset])

    def on_error(self, *args):
        print('error: ' + repr(args))
        return halt_canary
