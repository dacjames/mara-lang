halt_canary = object()


class Register(int):
    pass


class Machine(object):
    def __init__(self, buffered=False):
        self.code = []
        self.regs = []
        self.instruction_ptr = 0

        self.stack = []
        self.stack_ptr = 0
        self.frame_ptr = 0

        self.heaplet = []
        self.heap_ptr = 0

        self.root_scope = {}

        self.buffer = []

        def _buffered_print(arg):
            self.buffer.append(arg)

        def _raw_print(arg):
            print(arg)

        if buffered:
            self._print = _buffered_print
        else:
            self._print = _raw_print

    def _load(self, code):
        self.code = code

    def _loop(self):
        if len(self.code) == 0:
            return

        end = len(self.code)

        while self.instruction_ptr < end:
            code = self.code[self.instruction_ptr]
            bytecode = code[0]

            result = getattr(self, bytecode, self.on_error)(*code[1:])
            if result is halt_canary:
                break
            else:
                self.instruction_ptr += 1

    def _set(self, reg, value):
        if reg < len(self.regs):
            self.regs[reg] = value
        else:
            self.regs.append(value)

    def _allocate(self, obj):
        index = len(self.heaplet)
        self.heaplet.append(obj)
        return index

    def _flush(self):
        for line in buffer:
            print line
        self.buffer = []

    def print_const(self, arg):
        self._print(repr(arg))

    def print_reg(self, arg):
        self._print('r{i}:{v}'.format(
            i=arg,
            v=repr(self.regs[arg]),
        ))

    def print_object(self, reg):
        address = self.regs[reg]
        value = self.heaplet[address]
        self._print('r{i}:{a}=>{v}'.format(i=reg, a=address, v=repr(value)))

    def halt(self):
        return halt_canary

    def load_const(self, reg, value):
        self._set(reg, value)

    def add_cc(self, dst, left, right):
        self._set(dst, left + right)

    def add_rc(self, dst, left, right):
        self._set(dst, self.regs[left] + right)

    def add_rr(self, dst, left, right):
        self._set(dst, self.regs[left] + self.regs[right])

    def new_str(self, dst, value):
        self._set(dst, self._allocate(value))

    def branch_zero(self, pred, jmp_offset):
        if self.regs[pred] == 0:
            self.instruction_ptr += jmp_offset

    def branch_nonzero(self, pred, jmp_offset):
        if self.regs[pred] != 0:
            self.instruction_ptr += jmp_offset

    def branch_gt(self, pred, jmp_offset):
        if self.regs[pred] > 0:
            self.instruction_ptr += jmp_offset

    def branch_lt(self, pred, jmp_offset):
        if self.regs[pred] < 0:
            self.instruction_ptr += jmp_offset

    def branch_gte(self, pred, jmp_offset):
        if self.regs[pred] >= 0:
            self.instruction_ptr += jmp_offset

    def branch_lte(self, pred, jmp_offset):
        if self.regs[pred] <= 0:
            self.instruction_ptr += jmp_offset

    def on_error(self, *args):
        print 'dafuq: ' + repr(args)
        return halt_canary
