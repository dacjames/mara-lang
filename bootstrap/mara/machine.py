
# pylint: disable=R0904
# pylint: disable=R0902

halt_canary = object()


class Register(int):
    pass


class Machine(object):
    def __init__(self, buffered=False, traced=False):
        self._code = []
        self._regs = []
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

    ##########################################################################
    # Internal Functions
    ##########################################################################

    def _load(self, code):
        self._code = code

    def _describe(self):
        return '{pc}: {instruction}'.format(
            pc=self._pc,
            instruction=' '.join(map(str, self._code[self._pc]))
        )

    def _describe_result(self):
        return '{pc}= {regs} {stack}'.format(
            pc=self._pc,
            regs=tuple([r for r in self._regs if r is not None]),
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
        if reg < len(self._regs):
            self._regs[reg] = value
        else:
            self._regs.append(value)

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
            v=repr(self._regs[arg]),
        ))

    def print_object(self, reg):
        address = self._regs[reg]
        value = self._heaplet[address]
        self._print('r{i}:{a}=>{v}'.format(i=reg, a=address, v=repr(value)))

    def halt(self):
        return halt_canary

    def load_const(self, reg, value):
        self._set(reg, value)

    def add_cc(self, dst, left, right):
        self._set(dst, left + right)

    def add_rc(self, dst, left, right):
        self._set(dst, self._regs[left] + right)

    def add_rr(self, dst, left, right):
        self._set(dst, self._regs[left] + self._regs[right])

    def new_str(self, dst, value):
        self._set(dst, self._allocate(value))

    def branch_zero(self, pred, jmp_offset):
        if self._regs[pred] == 0:
            self._pc += jmp_offset

    def branch_nonzero(self, pred, jmp_offset):
        if self._regs[pred] != 0:
            self._pc += jmp_offset

    def branch_gt(self, pred, jmp_offset):
        if self._regs[pred] > 0:
            self._pc += jmp_offset

    def branch_lt(self, pred, jmp_offset):
        if self._regs[pred] < 0:
            self._pc += jmp_offset

    def branch_gte(self, pred, jmp_offset):
        if self._regs[pred] >= 0:
            self._pc += jmp_offset

    def branch_lte(self, pred, jmp_offset):
        if self._regs[pred] <= 0:
            self._pc += jmp_offset

    def call(self, func, *params):
        '''Call a function at address func with a variable number of params
        '''
        # push arguments
        for param in params:
            self._push(self._regs[param])

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
        self._stack_ptr = self._frame_ptr - fixed_offset - param_offset - 1

        # restore the old frame_ptr
        self._frame_ptr = self._stack_buffer[self._frame_ptr]

        # jump to the return address
        self._pc = ret_addr

    def load_param(self, dst, index):
        # saved frame_ptr, return address
        fixed_offset = 2

        # number of paramters
        num_params = self._stack_buffer[self._frame_ptr - fixed_offset]

        # compute the negative offset
        offset = fixed_offset + num_params - index

        # load the value into a register
        self._set(dst, self._stack_buffer[self._frame_ptr - offset])

    def push(self, src):
        '''Push a value from the src register onto the stack.
        '''
        self._push(self._regs[src])

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
