from src.translation.isa import *
from src.translation.preprocessor import *


def add_start_address(commands: list[Command], start_address: int):
    result = commands.copy()

    for command in result:
        command.position += 1

    jmp_start_addr = Command(Opcode.JMP, 1)
    jmp_start_addr.add_argument(Argument(AddrMode.REL, start_address - 1))

    result.insert(0, jmp_start_addr)
    return result


def join_text_and_data(text: list[Command], data: list[Command], isTextFirst: bool, start_addr: int):
    if isTextFirst:
        for command in data:
            command.position += len(text)
        return text + data, start_addr

    for command in text:
        command.position += len(data)
    return data + text, start_addr + len(data)


def parse_data(data: str) -> list:
    result = []
    variables: dict[str, int] = {}
    addr_counter = 1

    for line in data.split('\n'):
        current_command = Command(Opcode.DATA, addr_counter)

        var_description = line.split(':')
        assert len(var_description) == 2, 'You must write : only after name of variable'

        name = var_description[0]
        assert name[0][-1] != ' ', 'You must write : only after variable name'

        value = re.sub(r'\s+', '', var_description[1])

        assert name not in variables.keys(), 'Redefining a variable'
        variables[name] = addr_counter

        if value[0] == "'":
            value = value[1:]
            assert value.find("'") == len(value) - 1, "You should close char with single quot"
            value = value[:-1]
            current_command.add_argument(Argument(AddrMode.DATA, value))
        else:
            try:
                current_command.add_argument(Argument(AddrMode.DATA, int(value)))
            except ValueError:
                raise ValueError("You must write chars in single quotes")

        result.append(current_command)

        addr_counter += 1

    return result


def parse_text(text: str) -> list:
    assert (text.find('.start:') != -1), 'Must have .start'

    labels: dict[str, int] = {}
    unresolved_labels: dict[str, list[list[int]]] = {}
    start_addr = 0

    addr_counter = 1

    result: list[Command] = []

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
            current_command = Command(opcode, addr_counter)
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

    for label in unresolved_labels.keys():
        for info in unresolved_labels[label]:
            command = result[info[0] - 1]

            command.args[info[1]].data = labels[label] - command.position - 1

    return [result, start_addr]


def translate(source):
    """Функция запуска транслятора."""

    code = preprocessing(source)
    text = []
    data = []

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
        data = parse_data(code[data_start:data_stop])

    text, start_addr = parse_text(code[text_start:text_stop])

    joined_program, start_addr = join_text_and_data(text, data, data_i > text_i, start_addr)
    result = add_start_address(joined_program, start_addr)

    return result


def main(args):
    assert len(args) == 2, \
        "Wrong arguments: translation.py <asm_file> <target>"
    source, target = args

    with open(source, "rt", encoding="utf-8") as file:
        source = file.read()

    result = translate(source)

    write_code(args[1], result)


if __name__ == '__main__':
    sys.path.append('')
    main(sys.argv[1:])
