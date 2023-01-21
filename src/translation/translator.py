"""Модуль транслятора"""
import re
import sys

from src.machine.config import Register
from src.translation.isa import Opcode, Operation, Argument, AddrMode, \
    write_code, OperationRestrictionConfig, OperationType, OperationRestriction
from src.translation.preprocessor import preprocessing


def decode_register(operation: Operation, arg: str) -> Operation:
    """Вставка регистра в качестве аргумента"""
    assert Register(arg.lower()) is not None, 'Register not found'
    assert operation.is_corr_to_type(OperationType.REGISTER), 'You cant use register in not register commands'
    operation.add_argument(Argument(AddrMode.REG, Register(arg.lower())))
    return operation


def decode_label(operation: Operation, arg: str, labels: dict[str, int]) -> tuple[Operation, str | int]:
    """Вставка лейбла (его адреса) в качестве аргумента"""
    assert operation.is_corr_to_type(OperationType.BRANCH), 'You cant use labels not in branch command'

    if arg in labels:
        addr: int | str = labels[arg] - operation.position - 1
    else:
        addr = arg
    operation.add_argument(Argument(AddrMode.REL, addr))

    return operation, addr


def decode_absolute(operation: Operation, arg: str) -> Operation:
    """Вставка ячейки памяти с абсолютной адресацией в качестве аргумента"""
    assert operation.is_corr_to_type(OperationType.MEM), 'You cant access to memory not in ld and st command'
    address: int

    if arg == 'STDIN':
        address = 1
    elif arg == 'STDOUT':
        address = 2
    else:
        try:
            address = int(arg)
        except ValueError as addr_error:
            raise ValueError("You must use int with absolute address mode") from addr_error

    operation.add_argument(Argument(AddrMode.ABS, address))
    return operation


def decode_relative(operation: Operation, arg: str) -> Operation:
    """Вставка ячейки памяти с относительной адресацией в качестве аргумента"""
    assert operation.is_corr_to_type(OperationType.MEM), 'You cant access to memory not in ld and st command'
    assert arg.find(')') == len(arg) - 1, 'You must use ) after variable'
    operation.add_argument(Argument(AddrMode.REL, arg[:-1]))

    return operation


def decode_char(operation: Operation, arg: str) -> Operation:
    """Вставка символа в качестве аргумента"""
    assert arg.split("'") != 2, "You must write chars in single quotes"
    assert operation.is_corr_to_type(
        OperationType.REGISTER) or operation.opcode == Opcode.DATA, 'You cant use chars in not register commands'

    try:
        operation.add_argument(Argument(AddrMode.DATA, ord(arg[:-1])))
        return operation
    except ValueError as char_error:
        raise ValueError("You can't write a string as an argument, only a char") from char_error


def decode_int(operation: Operation, arg: str) -> Operation:
    """Вставка числа в качестве аргумента"""
    assert operation.is_corr_to_type(
        OperationType.REGISTER) or operation.opcode == Opcode.DATA, 'You cant use numbers in not register commands'

    try:
        value = int(arg)
        operation.add_argument(Argument(AddrMode.DATA, value))
        return operation
    except ValueError as char_error:
        raise ValueError("You must write chars in single quotes") from char_error


def check_correct_amount_of_operands(operation: Operation):
    """Проверяет, корректное ли количество операндов в операции использовано"""
    if operation.opcode in OperationRestrictionConfig:
        restriction: OperationRestriction = OperationRestrictionConfig[operation.opcode]
        argument_types: list[AddrMode] = []

        for arg in operation.args:
            if arg.mode not in argument_types:
                argument_types.append(arg.mode)

        assert restriction.amount.value == len(
            operation.args), 'You are using an operation with an incorrect number of operands'

        if OperationType.MEM in restriction.types or OperationType.REGISTER in restriction.types:
            assert AddrMode.REG in argument_types, 'You should use at least one register in the register and memory commands'

        if OperationType.BRANCH in restriction.types:
            assert AddrMode.REL in argument_types, 'You should use only labels in branch command'


def check_operand_constraints(operation: Operation, arg: str, arg_num: int):
    """Проверяет ограничения, наложенные на отдельные команды"""
    if operation.opcode in (Opcode.INC, Opcode.DEC):
        assert Register(arg[1:].lower()) is not None and arg_num == 0, \
            "You must use INC and DEC only with one argument and only with register"

    if operation.opcode == Opcode.LD:
        if arg_num == 0:
            assert Register(arg[1:].lower()) is not None, \
                "You must use register as the 1st argument in LD"
        else:
            assert arg[0] in ('#', '('), "You must use address or variable as the 2nd argument in LD"

    if operation.opcode == Opcode.ST:
        if arg_num == 1:
            assert Register(arg[1:].lower()) is not None, \
                "You must use register as the 2nd argument in LD"
        else:
            assert arg[0] in ('#', '('), "You must use address or variable as the 1st argument in LD"


def resolve_labels(operations: list[Operation], labels: dict[str, int],
                   unresolved_labels: dict[str, list[tuple[int, int]]]) -> list[Operation]:
    """Вставляет адреса необнаруженных меток"""
    for label_name, params in unresolved_labels.items():
        assert label_name in labels, 'You use undefined label'

        for operation_position, argument_number in params:
            operation = operations[operation_position]
            operation.args[argument_number].data = labels[label_name] - operation.position - 1

    return operations


def add_start_address(operations: list[Operation], start_address: int):
    """Переход на .start в начале программы"""
    for command in operations:
        command.position += 1

    jmp_start_addr = Operation(Opcode.JMP, 0)
    jmp_start_addr.add_argument(Argument(AddrMode.REL, start_address))

    operations.insert(0, jmp_start_addr)
    return operations


# def add_io_variables(operations: list[Operation]) -> tuple[list[Operation], int]:
#     """Добавление ячеек под ввод и вывод"""
#     for command in operations:
#         command.position += 2
#
#     operations.insert(0, Operation(Opcode.DATA, 1))
#     operations[0].add_argument(Argument(AddrMode.DATA, 0))
#
#     operations.insert(0, Operation(Opcode.DATA, 0))
#     operations[0].add_argument(Argument(AddrMode.DATA, 0))
#
#     return operations, 2


def resolve_variable(operation: Operation, variables: dict[str, int]) -> Operation:
    """Вставка значений переменных в команды"""
    if operation.is_corr_to_type(OperationType.MEM):
        for arg in operation.args:
            if arg.mode is AddrMode.REL and isinstance(arg.data, str) and arg.data in variables:
                arg.data = variables[arg.data] - operation.position - 1
                assert not isinstance(arg.data, str), 'You use undefined variable'

    return operation


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


def parse_data(data: str) -> list:
    """Превращение секции data в структуру"""
    result = []
    variables: dict[str, int] = {}
    addr_counter = 0

    for line in data.split('\n'):
        current_operation = Operation(Opcode.DATA, addr_counter)

        var_description = line.split(':')
        assert len(var_description) == 2, 'You must write : only after name of variable'

        name, value = var_description[0], re.sub(r'\s+', '', var_description[1])
        assert name[0][-1] != ' ', 'You must write : only after variable name'
        assert name not in variables, 'Redefining a variable'

        if value[0] == "'":
            current_operation = decode_char(current_operation, value[1:])
        else:
            current_operation = decode_int(current_operation, value)

        variables[name] = addr_counter

        result.append(current_operation)

        addr_counter += 1

    return [result, variables]


def parse_text(text: str) -> tuple[list[Operation], int]:
    """Превращение секцию text в структуру"""
    assert (text.find('.start:') != -1), 'Must have .start'

    labels: dict[str, int] = {}
    unresolved_labels: dict[str, list[tuple[int, int]]] = {}
    start_addr: int = -1

    addr_counter: int = 0

    result: list[Operation] = []

    for instr in text.split('\n'):

        decoding = instr.split(' ')

        if decoding[0][0] == '.':  # Запись нового лейбла
            current_label = decoding[0]

            assert len(decoding) == 1, 'Label should be located on a separate line '
            assert current_label[-1] == ':' and current_label.find(':'), 'Label should be and with : and contain only 1'

            current_label = decoding[0][1:-1]
            if current_label == 'start':
                start_addr = addr_counter
            labels[current_label] = addr_counter
        else:  # Декодирование операнда
            assert Opcode(decoding[0].lower()) is not None, 'There is no such command'

            current_operation = Operation(Opcode(decoding[0].lower()), addr_counter)
            arg_counter = 0
            for arg in decoding[1:]:
                # Проверка ограничений конкретных команд
                check_operand_constraints(current_operation, arg, arg_counter)

                if arg[0] == '%':
                    current_operation = decode_register(current_operation, arg[1:])
                elif arg[0] == '.':
                    current_operation, label = decode_label(current_operation, arg[1:], labels)
                    if isinstance(label, str):
                        if label not in unresolved_labels:
                            unresolved_labels[label] = []
                        unresolved_labels[label].append((addr_counter, arg_counter))
                elif arg[0] == '#':
                    current_operation = decode_absolute(current_operation, arg[1:])
                elif arg[0] == '(':
                    current_operation = decode_relative(current_operation, arg[1:])
                elif arg[0] == "'":
                    current_operation = decode_char(current_operation, arg[1:])
                else:
                    current_operation = decode_int(current_operation, arg)

                arg_counter += 1

            # Проверка корректности команды и ее сохранение
            check_correct_amount_of_operands(current_operation)
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

    joined_program, data_offset = join_text_and_data(text, data, data_i > text_i, variables)
    # joined_program_with_io, io_offset = add_io_variables(joined_program)
    result = add_start_address(joined_program, start_addr + data_offset)

    return result


def main(args):
    """Главная функция модуля"""
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
