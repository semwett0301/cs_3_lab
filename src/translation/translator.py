"""Модуль транслятора"""

import sys

from src.config import Register
from src.translation.isa import Opcode, Operation, Argument, AddrMode, DataOpcodes, BranchOpcodes, RegisterOpcodes, \
    write_code
from src.translation.preprocessor import preprocessing


def add_start_address(commands: list[Operation], start_address: int):
    result = commands.copy()

    for command in result:
        command.position += 1

    jmp_start_addr = Operation(Opcode.JMP, 1)
    jmp_start_addr.add_argument(Argument(AddrMode.REL, start_address - 1))

    result.insert(0, jmp_start_addr)
    return result


def add_io_variables(commands: list[Operation]) -> list[Operation]:
    for command in commands:
        command.position += 2

    commands.insert(0, Operation(Opcode.DATA, 2))
    commands[0].add_argument(Argument(AddrMode.DATA, 0))

    commands.insert(0, Operation(Opcode.DATA, 1))
    commands[0].add_argument(Argument(AddrMode.DATA, 0))

    return commands


def resolve_variable(command: Operation, variables: dict[str, int]) -> Operation:
    if command.opcode in DataOpcodes:
        for arg in command.args:
            print(command.opcode, arg.mode, arg.data)
            if arg.mode in (AddrMode.ABS, AddrMode.REL) and arg.data in variables.keys():
                if arg.mode == AddrMode.ABS:
                    arg.data = variables[arg.data]
                else:
                    arg.data = variables[arg.data] - command.position - 1
                assert not isinstance(arg.data, str), 'You use undefined variable'

    return command


def join_text_and_data(text: list[Operation], data: list[Operation], is_text_first: bool, variables: dict[str, int]) -> \
        tuple[list[Operation], int]:
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
    result = []
    variables: dict[str, int] = {}
    addr_counter = 1

    for line in data.split('\n'):
        current_command = Operation(Opcode.DATA, addr_counter)

        var_description = line.split(':')
        assert len(var_description) == 2, 'You must write : only after name of variable'

        name, value = var_description[0], re.sub(r'\s+', '', var_description[1])
        assert name[0][-1] != ' ', 'You must write : only after variable name'
        assert name not in variables.keys(), 'Redefining a variable'

        if value[0] == "'":
            value = value[1:]
            assert value.find("'") == len(value) - 1, "You should close char with single quot"
            value = value[:-1]
            current_command.add_argument(Argument(AddrMode.DATA, value))
        else:
            try:
                current_command.add_argument(Argument(AddrMode.DATA, int(value)))
            except ValueError as e:
                raise ValueError("You must write chars in single quotes") from e

        variables[name] = addr_counter

        result.append(current_command)

        addr_counter += 1

    return [result, variables]


def parse_text(text: str) -> tuple[list[Operation], int]:
    assert (text.find('.start:') != -1), 'Must have .start'

    labels: dict[str, int] = {}
    unresolved_labels: dict[str, list[tuple[int, int]]] = {}
    start_addr = 0

    addr_counter = 1

    result: list[Operation] = []

    for instr in text.split('\n'):

        decoding = instr.split(' ')

        if decoding[0][0] == '.':
            label = decoding[0]

            assert len(decoding) == 1, 'Label should be located on a separate line '
            assert label[-1] == ':' and label.find(':'), 'Label should be and with : and contain only 1'

            label = decoding[0][1:-1]
            if label == 'start':
                start_addr = addr_counter
            labels[label] = addr_counter
        else:
            assert Opcode(decoding[0].lower()) is not None, 'There is no such command'

            opcode = Opcode(decoding[0].lower())
            current_command = Operation(opcode, addr_counter)
            arg_counter = 0
            for arg in decoding[1:]:
                if arg[0] == '%':
                    assert Register(arg[1:].lower()) is not None, 'Register not found'
                    assert opcode in RegisterOpcodes, 'You cant use register in branch commands'
                    current_command.add_argument(Argument(AddrMode.REG, Register(arg[1:].lower())))
                elif arg[0] == '.':
                    assert opcode in BranchOpcodes != -1, 'You cant use labels not in branch command'
                    addr = 0

                    if arg[1:] in labels.keys():
                        addr = labels[arg[1:]] - addr_counter - 1
                    else:
                        label = arg[1:]
                        if label not in unresolved_labels.keys():
                            unresolved_labels[label] = []
                        unresolved_labels[label].append([addr_counter, arg_counter])

                    current_command.add_argument(Argument(AddrMode.REL, addr))
                elif arg[0] == '#':
                    assert opcode in DataOpcodes, 'You cant access to memory not in ld and st command'
                    variable = arg[1:]
                    address: str | int = variable

                    if variable == 'STDIN':
                        address = 1
                    elif variable == 'STDOUT':
                        address = 2
                    elif variable == 'STDERR':
                        address = 3

                    current_command.add_argument(Argument(AddrMode.ABS, address))
                elif arg[0] == '(':
                    assert opcode in DataOpcodes, 'You cant access to memory not in ld and st command'
                    assert arg.find(')') == len(arg) - 1, 'You must use ) after variable'
                    current_command.add_argument(Argument(AddrMode.REL, arg[1:-1]))
                elif arg[0] == "'":
                    assert arg.split("'") != 3, "You must write chars in single quotes"
                    current_command.add_argument(Argument(AddrMode.DATA, arg[1:-1]))
                else:
                    try:
                        value = int(arg)
                        current_command.add_argument(Argument(AddrMode.DATA, value))
                    except ValueError:
                        raise ValueError("You must write chars in single quotes")

                arg_counter += 1

            result.append(current_command)

            addr_counter += 1

    for label in unresolved_labels.items():
        for command_position, argument_number in label:
            command = result[command_position - 1]

            command.args[argument_number].data = label - command.position - 1

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
    source = args

    with open(source, "rt", encoding="utf-8") as file:
        source = file.read()

    result = translate(source)

    write_code(args[1], result)


if __name__ == '__main__':
    sys.path.append('.')
    main(sys.argv[1:])
