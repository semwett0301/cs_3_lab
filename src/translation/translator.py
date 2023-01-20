"""Модуль транслятора"""
import re
import sys

from src.config import Register
from src.translation.isa import Opcode, Operation, Argument, AddrMode, DataOpcodes, BranchOpcodes, RegisterOpcodes, \
    write_code
from src.translation.preprocessor import preprocessing


def add_start_address(commands: list[Operation], start_address: int):
    """Переход на .start в начале программы"""
    result = commands.copy()

    for command in result:
        command.position += 1

    jmp_start_addr = Operation(Opcode.JMP, 1)
    jmp_start_addr.add_argument(Argument(AddrMode.REL, start_address - 1))

    result.insert(0, jmp_start_addr)
    return result


def add_io_variables(commands: list[Operation]) -> list[Operation]:
    """Добавление ячеек под ввод и вывод"""
    for command in commands:
        command.position += 2

    commands.insert(0, Operation(Opcode.DATA, 2))
    commands[0].add_argument(Argument(AddrMode.DATA, 0))

    commands.insert(0, Operation(Opcode.DATA, 1))
    commands[0].add_argument(Argument(AddrMode.DATA, 0))

    return commands


def resolve_variable(command: Operation, variables: dict[str, int]) -> Operation:
    """Вставка значений переменных в команды"""
    if command.opcode in DataOpcodes:
        for arg in command.args:
            print(command.opcode, arg.mode, arg.data)
            if arg.mode in (AddrMode.ABS, AddrMode.REL) and arg.data in variables.keys():
                addr = arg.data

                if arg.mode == AddrMode.ABS:
                    arg.data = variables[addr]
                else:
                    arg.data = variables[addr] - command.position - 1
                assert not isinstance(arg.data, str), 'You use undefined variable'

    return command


def join_text_and_data(text: list[Operation], data: list[Operation], is_text_first: bool, variables: dict[str, int]) -> \
        tuple[list[Operation], int]:
    """Соединение секций text и data"""
    offset: int = 0

    if is_text_first:
        for command in data:
            command.position += len(text)

        for name in variables.keys():
            variables[name] += len(text)

        result = text + data
    else:
        for command in text:
            command.position += len(data)
        result = data + text
        offset = len(data)

    for command in result:
        resolve_variable(command, variables)

    return result, offset


def decode_register(operation: Operation, arg: str) -> Operation:
    """Вставка регистра в качестве аргумента"""
    assert Register(arg[1:].lower()) is not None, 'Register not found'
    assert operation.opcode in RegisterOpcodes, 'You cant use register in branch commands'
    return operation.add_argument(Argument(AddrMode.REG, Register(arg[1:].lower())))


def decode_label(operation: Operation, arg: str, label_value: int | None) -> tuple[Operation, str | int]:
    """Вставка лейбла (его адреса) в качестве аргумента"""
    assert operation.opcode in BranchOpcodes != -1, 'You cant use labels not in branch command'

    if label_value is not None:
        addr: int | str = label_value - operation.position - 1
    else:
        addr = arg

    return operation.add_argument(Argument(AddrMode.REL, addr)), addr


def decode_absolute(operation: Operation, arg: str) -> Operation:
    """Вставка ячейки памяти с абсолютной адресацией в качестве аргумента"""
    assert operation.opcode in DataOpcodes, 'You cant access to memory not in ld and st command'
    address: str | int = arg

    if arg == 'STDIN':
        address = 1
    elif arg == 'STDOUT':
        address = 2

    return operation.add_argument(Argument(AddrMode.ABS, address))


def decode_relative(operation: Operation, arg: str) -> Operation:
    """Вставка ячейки памяти с относительной адресацией в качестве аргумента"""
    assert operation.opcode in DataOpcodes, 'You cant access to memory not in ld and st command'
    assert arg.find(')') == len(arg) - 1, 'You must use ) after variable'
    return operation.add_argument(Argument(AddrMode.REL, arg))


def decode_char(operation: Operation, arg: str) -> Operation:
    """Вставка символа в качестве аргумента"""
    assert arg.split("'") != 3, "You must write chars in single quotes"
    try:
        return operation.add_argument(Argument(AddrMode.DATA, ord(arg[1:-1])))
    except ValueError as char_error:
        raise ValueError("You can't write a string as an argument, only a char") from char_error


def decode_int(operation: Operation, arg: str) -> Operation:
    """Вставка числа в качестве аргумента"""
    try:
        value = int(arg)
        return operation.add_argument(Argument(AddrMode.DATA, value))
    except ValueError as char_error:
        raise ValueError("You must write chars in single quotes") from char_error


def parse_data(data: str) -> list:
    """Превращение секции data в структуру"""
    result = []
    variables: dict[str, int] = {}
    addr_counter = 0

    for line in data.split('\n'):
        current_command = Operation(Opcode.DATA, addr_counter)

        var_description = line.split(':')
        assert len(var_description) == 2, 'You must write : only after name of variable'

        name, value = var_description[0], re.sub(r'\s+', '', var_description[1])
        assert name[0][-1] != ' ', 'You must write : only after variable name'
        assert name not in variables, 'Redefining a variable'

        if value[0] == "'":
            current_command = decode_char(current_command, value[1:])
        else:
            current_command = decode_int(current_command, value)

        variables[name] = addr_counter

        result.append(current_command)

        addr_counter += 1

    return [result, variables]


def resolve_labels(operations: list[Operation], labels: dict[str, int],
                   unresolved_labels: dict[str, list[tuple[int, int]]]) -> list[Operation]:
    """Вставляет адреса необнаруженных меток"""
    for label_name, params in unresolved_labels.items():
        assert label_name in labels, 'You use undefined label'

        for operation_position, argument_number in params:
            operation = operations[operation_position - 1]
            operation.args[argument_number].data = labels[label_name] - operation.position - 1

    return operations


def parse_text(text: str) -> tuple[list[Operation], int]:
    """Превращение секции text в структуру"""
    assert (text.find('.start:') != -1), 'Must have .start'

    labels: dict[str, int] = {}
    unresolved_labels: dict[str, list[tuple[int, int]]] = {}
    start_addr: int = -1

    addr_counter: int = 0

    result: list[Operation] = []

    for instr in text.split('\n'):

        decoding = instr.split(' ')

        if decoding[0][0] == '.':
            current_label = decoding[0]

            assert len(decoding) == 1, 'Label should be located on a separate line '
            assert current_label[-1] == ':' and current_label.find(':'), 'Label should be and with : and contain only 1'

            current_label = decoding[0][1:-1]
            if current_label == 'start':
                start_addr = addr_counter
            labels[current_label] = addr_counter
        else:
            assert Opcode(decoding[0].lower()) is not None, 'There is no such command'

            current_operation = Operation(Opcode(decoding[0].lower()), addr_counter)
            arg_counter = 0
            for arg in decoding[1:]:
                if arg[0] == '%':
                    current_operation = decode_register(current_operation, arg)
                elif arg[0] == '.':
                    current_operation, current_label = decode_label(current_operation, arg[1:], labels[arg[1:]])
                    if isinstance(current_label, str):
                        if current_label not in unresolved_labels:
                            unresolved_labels[current_label] = []
                        unresolved_labels[current_label].append((addr_counter, arg_counter))
                elif arg[0] == '#':
                    current_operation = decode_absolute(current_operation, arg[1:])
                elif arg[0] == '(':
                    current_operation = decode_relative(current_operation, arg[1:])
                elif arg[0] == "'":
                    current_operation = decode_char(current_operation, arg[1:])
                else:
                    current_operation = decode_int(current_operation, arg)

                arg_counter += 1

            result.append(current_operation)

            addr_counter += 1

    result = resolve_labels(result, labels, unresolved_labels)
    return result, start_addr


def translate(source: str) -> list[Operation]:
    """Функция запуска транслятора."""

    code = preprocessing(source)
    data = []
    variables = {}

    text_i = code.find('section .text')

    if text_i == -1:
        raise Exception('You have to write the section text')

    text_start, text_stop = text_i + len('section .text') + 1, None

    data_i = code.find('section .data')

    if data_i == -1:
        text_stop = len(code)
    else:
        data_start, data_stop = data_i + len('section .data') + 1, None

        if data_i < text_i:
            data_stop = text_i - 1
            text_stop = len(code)
        else:
            text_stop = data_i - 1
            data_stop = len(code)
        data, variables = parse_data(code[data_start:data_stop])

    text, start_addr = parse_text(code[text_start:text_stop])

    joined_program, offset = join_text_and_data(text, data, data_i > text_i, variables)
    result = add_start_address(add_io_variables(joined_program), start_addr + offset)

    return result


def main(args):
    assert len(args) == 2, \
        "Wrong arguments: translation.py <asm_file> <target>"
    source = args[0]

    with open(source, "rt", encoding="utf-8") as file:
        code = file.read()

    result = translate(code)

    write_code(args[1], result)


if __name__ == '__main__':
    sys.path.append('.')
    main(sys.argv[1:])
