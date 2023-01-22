import logging
import sys
from enum import Enum

from src.machine.config import ReservedVariable
from src.translation.isa import read_code, Opcode, Argument, AddrMode, Operation



def simulation(code, limit, input_buffer):
    control_unit = ControlUnit(code, input_buffer)
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
    cell_counter = len(memory)

    # Добавляем специальные переменные (если они должны находиться раньше кода)
    max_reserved_address: int | None = None

    for var in list(ReservedVariable):
        if cell_counter > ReservedVariable[var].value > max_reserved_address:
            max_reserved_address = ReservedVariable[var].value

    if max_reserved_address is not None:
        add_reserved_variables(memory, max_reserved_address)
        cell_counter += max_reserved_address + 1

    # "Доаллоцируем" память - 1024 ячейки (включают зарезервированные переменные, находящиеся после кода)
    num = 1024
    assert cell_counter < num, "Not enough memory!"
    while cell_counter < num:
        operation: Operation = Operation(Opcode.DATA, cell_counter)
        operation.add_argument(Argument(AddrMode.DATA, 0))
        memory.append(operation)
        cell_counter += 1

    output, instr_counter, ticks = simulation(memory, 1000000, input_token)

    print("Output:")
    print(output)
    print("instr_counter:", instr_counter, "ticks:", ticks)
    return output


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    main(sys.argv[1:])
