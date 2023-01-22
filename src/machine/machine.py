import logging
import sys
from enum import Enum

from src.machine.config import ReservedVariable, Register, resolve_overflow, AMOUNT_OF_MEMORY, RegFile, Alu, \
    AluOperations, RegLatchSignals, opcode2operation
from src.translation.isa import read_code, Opcode, Argument, AddrMode, Operation



class DataPath:
    """Класс, эмулирующий тракт данных, предоставляющий интерфейс для CU"""

    def __init__(self):
        self.memory: list[Operation] = []
        self.reg_file: RegFile = RegFile()
        self.pc: int = 0
        self.addr_reg: int = 0

        self.data_alu: Alu = Alu()
        self.data_alu_bus: int = 0

        self.addr_alu: Alu = Alu()
        self.addr_alu_bus: int = 0

        self.mem_bus: int = 0

        self._zero_flag: bool = False
        self._positive_flag: bool = False

        self.input_buffer: list[int] = []
        self.output_buffer: list[int] = []

    def update_memory(self, memory: list[Operation], input_buffer: list[int]):
        """Обновление состояния памяти (в т.ч буферов ввода и вывода)"""
        self.memory = memory
        self.input_buffer = input_buffer
        self.output_buffer = []

    def set_regs_args(self, sel_out: Register = Register.R1, sel_arg_1: Register = Register.R1,
                      sel_arg_2: Register = Register.R1):
        """Метод для выбора набора регистров из регистрового файла для инструкции (3 параметра)"""
        assert (sel_arg_1, sel_arg_2,
                sel_out) in self.reg_file.registers, 'You trying latch register that register file doesnt have'

        self.reg_file.operand_2 = sel_arg_2
        self.reg_file.operand_1 = sel_arg_1
        self.reg_file.out = sel_out

    def set_data_alu_args(self, argument: int | None = None):
        """Метод для эмуляции ввода данных в АЛУ, связанного с регистровым файлом"""
        self.data_alu.left = self.reg_file.registers[self.reg_file.argument_1]
        if argument is not None:
            self.data_alu.right = argument
        else:
            self.data_alu.right = self.reg_file.registers[self.reg_file.argument_2]

    def set_addr_alu_args(self, argument: int):
        """Метод для эмуляции ввода данных в АЛУ, связанного счетчиком команд"""
        self.addr_alu.left = self.pc
        self.addr_alu.right = argument

    def execute_data_alu(self, instruction: AluOperations):
        """Эмуляция исполнения команд в АЛУ, связанного с регистровым файлом"""
        res = resolve_overflow(self.data_alu.operations[instruction](self.data_alu.left, self.data_alu.right))

        self.data_alu_bus = res
        self._zero_flag = (res == 0)
        self._positive_flag = (res > 0)

    def execute_addr_alu(self, instruction: AluOperations):
        """Эмуляция исполнения команд в АЛУ, связанного с счетчиком команд"""
        res = resolve_overflow(self.addr_alu.operations[instruction](self.addr_alu.left, self.addr_alu.right))
        self.addr_alu_bus = res

    def __get_addr_argument(self, operand: int | None) -> int:
        """Получение корректного аргумента адреса - вспомогательная функция"""
        if operand is not None:
            result = resolve_overflow(operand)
        else:
            result = self.addr_alu_bus

        assert result < AMOUNT_OF_MEMORY, 'Out of memory bounds'
        return result

    def latch_pc(self, operand: int | None = None):
        """Установка значений PC"""
        self.pc = self.__get_addr_argument(operand)

    def latch_addr_register(self, operand: int | None = None):
        """Установка значений адресного регистра"""
        self.addr_reg = self.__get_addr_argument(operand)

    def latch_register(self, sel_reg: RegLatchSignals, argument: int | None = None):
        """Установка значения в выбранный регистр"""
        if sel_reg is RegLatchSignals.ARG:
            assert argument is not None, 'You must set the argument if you want to latch its in register'
            source: int = argument
        elif sel_reg is RegLatchSignals.REG:
            source = self.reg_file[self.reg_file.argument_1]
        elif sel_reg is RegLatchSignals.ALU:
            source = self.data_alu_bus
        else:
            source = self.mem_bus

        self.reg_file[self.reg_file.out] = source

    def __rw_restrictions(self):
        """Ограничения на записываемые / читаемые значения - вспомогательная функция"""
        assert self.memory[
                   self.addr_reg].opcode == Opcode.DATA, "You are trying to get access to the instruction in read/write operations"
        assert len(self.memory[self.addr_reg].args) and self.memory[self.addr_reg].args[
            0].mode == AddrMode.DATA, "You must have 1 data arguments in data cells"

    def read(self):
        """Чтение из памяти (вкл. ввод)"""
        if self.addr_reg == ReservedVariable.STDIN.value:
            self.mem_bus = self.input_buffer.pop()
        else:
            self.__rw_restrictions()
            self.mem_bus = self.memory[self.addr_reg].args[0].data

    def write(self):
        """Запись в память (вкл. вывод)"""
        write_data = self.reg_file.registers[self.reg_file.argument_2]

        if self.addr_reg == ReservedVariable.STDOUT.value:
            self.output_buffer.append(write_data)
        else:
            self.__rw_restrictions()
            self.memory[self.addr_reg].args[0].data = write_data

    def get_zero_flag(self) -> bool:
        """Метод для получения Zero флага"""
        return self._zero_flag

    def get_positive_flag(self) -> bool:
        """Метод получения Positive флага"""
        return self._positive_flag


class ControlUnit:
    """Блок управления процессора. Выполняет декодирование инструкций и
       управляет состоянием процессора, включая обработку данных (DataPath).
       """

    def __init__(self):
        self.data_path: DataPath | None = None
        self.current_operation: Operation | None = None
        self.program: list[Operation] = []
        self.step_counter: int = 0
        self._tick: int = 0
        self.output_buffer: list[int] = []

    def set_program(self, program: list[Operation], input_buffer: list[int]):
        """Ввод программы в процессор"""
        cell_counter: int = len(program)
        prog_addr: int = 0

        # Добавляем специальные переменные (если они должны находиться раньше кода)
        max_reserved_address: int | None = None

        for var in list(ReservedVariable):
            if cell_counter > ReservedVariable[var].value > max_reserved_address:
                max_reserved_address = ReservedVariable[var].value

        if max_reserved_address is not None:
            add_reserved_variables(program, max_reserved_address)
            cell_counter += max_reserved_address + 1
            prog_addr += max_reserved_address + 1

        # "Доаллоцируем" память - 1024 ячейки (включают зарезервированные переменные, находящиеся после кода)
        assert cell_counter < AMOUNT_OF_MEMORY, "Not enough memory!"
        while cell_counter < AMOUNT_OF_MEMORY:
            operation: Operation = Operation(Opcode.DATA, cell_counter)
            operation.add_argument(Argument(AddrMode.DATA, 0))
            program.append(operation)
            cell_counter += 1

        if self.data_path is None:
            self.data_path = DataPath()
        self.data_path.update_memory(program, input_buffer)
        self.data_path.latch_pc(prog_addr)

    def tick(self):
        """Счётчик тактов процессора. Вызывается при переходе на следующий такт."""
        self._tick += 1

    def current_tick(self):
        """Получить номер текущего такта"""
        return self._tick

    def latch_step_counter(self, sel_next: bool):
        if sel_next:
            self.step_counter += 1
        else:
            self.step_counter = 0

    def latch_inc_program_counter(self):
        """Увеличивает счетчик команд на 1 - переходит к следующей инструкции"""
        self.data_path.latch_pc(self.data_path.pc + 1)

    def __calc_relative_addr(self, offset: int):
        """Вычисление относительного адреса - вспомогательная функция"""
        self.data_path.set_addr_alu_args(offset)
        self.data_path.execute_addr_alu(AluOperations.ADD)
        self.latch_step_counter(sel_next=True)

    def __load_common_part(self, goal: Register, arg: int | None, offset: int = 0):
        """Общая часть операции загрузки - вспомогательная функция"""
        if self.step_counter == 1 + offset:
            self.data_path.latch_addr_register(arg)
            self.latch_step_counter(sel_next=True)
        elif self.step_counter == 2 + offset:
            self.data_path.read()
            self.latch_step_counter(sel_next=True)
        elif self.step_counter == 3 + offset:
            self.data_path.set_regs_args(sel_out=goal)
            self.data_path.latch_register(RegLatchSignals.MEM)
            self.latch_step_counter(sel_next=False)

    def __stoan_common_part(self, goal: int | None, arg: Register, offset: int):
        if self.step_counter == 1 + offset:
            self.data_path.latch_addr_register(goal)
            self.latch_step_counter(sel_next=True)
        elif self.step_counter == 2 + offset:
            self.data_path.set_regs_args(sel_arg_2=arg)
            self.data_path.write()
            self.latch_step_counter(sel_next=False)

    def decode_and_execute_instruction(self):
        """Прочитать и исполнить инструкцию (в потактовом режиме)"""
        self.tick()

        if self.current_operation is None or self.step_counter == 0:
            self.current_operation = self.data_path.memory[self.data_path.pc]
            self.latch_step_counter(sel_next=True)
        else:
            opcode = self.current_operation.opcode
            if opcode is Opcode.HLT:
                raise StopIteration

            if opcode in (Opcode.JMP, Opcode.JE, Opcode.JNE, Opcode.JG):
                arg = self.current_operation.args[0]

                if self.step_counter == 1:
                    self.__calc_relative_addr(arg.data)
                else:
                    zero = self.data_path.get_zero_flag()
                    positive = self.data_path.get_positive_flag()

                    if opcode == Opcode.JMP \
                            or opcode == Opcode.JE and zero \
                            or opcode == Opcode.JNE and not zero \
                            or opcode == Opcode.JG and positive:
                        self.data_path.latch_pc()

                    self.latch_step_counter(sel_next=False)

            if opcode in (Opcode.INC, Opcode.DEC):
                if self.step_counter == 1:
                    reg: Register = self.current_operation.args[0].data
                    self.data_path.set_regs_args(sel_out=reg, sel_arg_1=reg)

                    if opcode == Opcode.INC:
                        self.data_path.set_data_alu_args(1)
                    else:
                        self.data_path.set_data_alu_args(-1)

                    self.data_path.execute_data_alu(opcode2operation[opcode])
                    self.latch_step_counter(sel_next=True)
                else:
                    self.data_path.latch_register(RegLatchSignals.ALU)
                    self.latch_step_counter(sel_next=False)

            if opcode in (Opcode.ADD, Opcode.SUB, Opcode.DIV, Opcode.MOD, Opcode.MUL):
                if self.step_counter == 1:
                    first_arg, second_arg, third_arg = self.current_operation.args

                    if third_arg.mode == AddrMode.REG:
                        self.data_path.set_regs_args(sel_out=first_arg.data, sel_arg_1=second_arg.data,
                                                     sel_arg_2=third_arg.data)
                        self.data_path.set_data_alu_args()
                    else:
                        self.data_path.set_regs_args(sel_out=first_arg.data, sel_arg_1=second_arg.data)
                        self.data_path.set_data_alu_args(third_arg)

                    self.data_path.execute_data_alu(opcode2operation[opcode])
                    self.latch_step_counter(sel_next=True)
                else:
                    self.data_path.latch_register(RegLatchSignals.ALU)
                    self.latch_step_counter(sel_next=False)

            if opcode is Opcode.CMP:
                first_arg, second_arg = self.current_operation.args

                if second_arg.mode == AddrMode.REG:
                    self.data_path.set_regs_args(sel_arg_1=first_arg.data, sel_arg_2=second_arg.data)
                    self.data_path.set_data_alu_args()
                else:
                    self.data_path.set_regs_args(sel_arg_1=first_arg.data)
                    self.data_path.set_data_alu_args(second_arg)

                self.data_path.execute_data_alu(opcode2operation[opcode])
                self.latch_step_counter(sel_next=False)

            if opcode is Opcode.MOV:
                first_arg, second_arg = self.current_operation.args
                if second_arg.mode == AddrMode.REG:
                    if self.step_counter == 1:
                        self.data_path.set_regs_args(sel_out=first_arg.data, sel_arg_1=second_arg.data)
                        self.latch_step_counter(sel_next=True)
                    else:
                        self.data_path.latch_register(RegLatchSignals.REG)
                        self.latch_step_counter(sel_next=False)
                else:
                    if self.step_counter == 1:
                        self.data_path.set_regs_args(sel_out=first_arg.data)
                        self.latch_step_counter(sel_next=True)
                    else:
                        self.data_path.latch_register(RegLatchSignals.ARG, second_arg.data)
                        self.latch_step_counter(sel_next=False)

            if opcode is Opcode.LD:
                first_arg, second_arg = self.current_operation.args

                if second_arg.mode == AddrMode.ABS:
                    self.__load_common_part(first_arg.data, second_arg.data, 0)
                else:
                    if self.step_counter == 1:
                        self.__calc_relative_addr(second_arg.data)
                        self.latch_step_counter(sel_next=True)
                    self.__load_common_part(first_arg.data, None, 1)

            if opcode is Opcode.ST:
                first_arg, second_arg = self.current_operation.args
                if first_arg.mode == AddrMode.ABS:
                    self.__stoan_common_part(first_arg.data, second_arg.data, 0)
                else:
                    if self.step_counter == 1:
                        self.__calc_relative_addr(first_arg.data)
                        self.latch_step_counter(sel_next=True)
                    self.__stoan_common_part(None, second_arg.data, 1)

    def __repr__(self):
        state = "TICK: {}, PC: {}, ADDR_REG: {}, R1: {}, R2: {}, R3: {}, R4: {}, R5: {}, D_ALU_BUD: {}, A_ALU_BUD: {}, MEM_BUS: {}, Z: {}, P: {}, STEP_COUNTER: {}".format(
            self._tick,
            self.data_path.pc,
            self.data_path.addr_reg,
            self.data_path.reg_file.registers[Register.R1],
            self.data_path.reg_file.registers[Register.R2],
            self.data_path.reg_file.registers[Register.R3],
            self.data_path.reg_file.registers[Register.R4],
            self.data_path.reg_file.registers[Register.R5],
            self.data_path.data_alu_bus,
            self.data_path.addr_alu_bus,
            self.data_path.mem_bus,
            self.data_path.get_zero_flag(),
            self.data_path.get_positive_flag(),
            self.step_counter
        )

        if self.current_operation is not None:
            operation = self.current_operation
            opcode = operation.opcode

            cell_num = operation.position
            action = "{} {}".format(cell_num, opcode)
        else:
            action = "-"

        return "{} {}".format(state, action)


def simulation(code: list[Operation], limit: int, input_buffer: list[int]):
    control_unit = ControlUnit()
    control_unit.set_program(code, input_buffer)
    instr_counter = 0

    logging.debug('%s', control_unit)
    try:
        while True:
            assert limit > instr_counter, "too long execution, increase limit!"
            control_unit.decode_and_execute_instruction()
            if control_unit.step_counter == 0:
                instr_counter += 1
            logging.debug('%s', control_unit)
    except StopIteration:
        pass
    output = ''
    for c in control_unit.output_buffer:
        output += str(c)
        if c in range(0x110000):
            output += '(' + chr(c) + ')'
    logging.info('output: %s', output)
    return output, instr_counter, control_unit.current_tick()


def add_reserved_variables(operations: list[Operation], max_reserved_address: int) -> list[Operation]:
    """Добавление зарезервированных ячеек до кода"""
    for operation in operations:
        operation.position += max_reserved_address + 1

    for pos in range(max_reserved_address):
        operation = Operation(Opcode.DATA, pos)
        operation.add_argument(Argument(AddrMode.DATA, 0))

        operations.insert(pos, operation)

    return operations


def main(args):
    """Главная функция модуля"""
    assert len(args) == 2, "Wrong arguments: machine.py <code_file> <input_file>"
    code_file, input_file = args

    input_token = []
    memory: list[Operation] = read_code(code_file)
    with open(input_file, encoding="utf-8") as file:
        input_text = file.read()
        for char in input_text:
            input_token.append(ord(char))

    input_token.append(0)

    output, instr_counter, ticks = simulation(memory, 1000, input_token)

    print("Output:")
    print(output)
    print("instr_counter:", instr_counter, "ticks:", ticks)
    return output


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
