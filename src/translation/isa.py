"""Модуль описания системы команд"""
"""Содержит методы кодирования и декодирования команд"""

from enum import Enum
from src.config import Register

import json


class Opcode(str, Enum):
    """Коды операций"""

    DATA = 'data'
    NOP = 'nop'
    HLT = 'hlt'

    LD = 'ld'
    ST = 'st'

    ADD = 'add'
    SUB = 'sub'
    MUL = 'mul'
    MOD = 'mod'
    DIV = 'div'
    CMP = 'cmp'

    INC = 'inc'
    DEC = 'dec'

    MOV = 'mov'
    XOR = 'xor'

    JMP = 'jmp'
    JE = 'je'
    JNE = 'jne'
    JG = 'jg'


# Коды операций, которым разрешен доступ к памяти
DataOpcodes = (
    Opcode.LD, Opcode.ST
)

# Коды операций, которым разрешена адресация по лейблам
BranchOpcodes = (
    Opcode.JG, Opcode.JMP, Opcode.JE, Opcode.JNE
)

# Коды операций, которым разрешена работа с регистрами
RegisterOpcodes = (
    Opcode.ADD, Opcode.DEC, Opcode.INC, Opcode.DIV, Opcode.SUB, Opcode.MUL, Opcode.MOD, Opcode.MOV, Opcode.XOR,
    Opcode.CMP, Opcode.LD, Opcode.ST
)


class AddrMode(str, Enum):
    """Режимы адресации"""
    ABS = 'absolute'
    REL = 'relative'
    DATA = 'data'
    REG = 'register'


class Argument:
    """Аргуемент операции"""

    def __init__(self, mode: AddrMode, data: int | Register | str):
        self.data = data
        self.mode = mode


class Operation:
    """Полное описание инструкции."""

    def __init__(self, opcode: Opcode, position: int):
        self.opcode = opcode
        self.position = position
        self.args: list[Argument] = []

    def add_argument(self, arg: Argument):
        self.args.append(arg)


class Encoder(json.JSONEncoder):
    """Класс-энкодер для записи и чтения из JSON"""

    def default(self, o):
        if isinstance(o, (Argument, Operation)):
            return o.__dict__
        return json.JSONEncoder.default(self, o)


def write_code(filename: str, code: list[Operation]) -> None:
    print(json.dumps(code, indent=4, cls=Encoder))
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(code, indent=4, cls=Encoder))


def read_code(filename: str) -> object:
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())  # type: ignore

    for instr in code:
        instr['opcode'] = Opcode(instr['opcode'])
        for arg in instr['args']:
            arg = Argument(AddrMode(arg['mode']), arg['data'])

    return code
