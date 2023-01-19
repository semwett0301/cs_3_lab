import json
from enum import Enum


class Register(str, Enum):
    r1 = 'r1'
    r2 = 'r2'
    r3 = 'r3'
    r4 = 'r4'
    r5 = 'r5'


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


DataOpcodes = (
    Opcode.LD, Opcode.ST
)

BranchOpcodes = (
    Opcode.JG, Opcode.JMP, Opcode.JE, Opcode.JNE
)

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
    def __init__(self, mode: AddrMode, data: int | Register | str):
        self.data = data
        self.mode = mode


class Command:
    """Полное описание инструкции."""

    def __init__(self, opcode: Opcode, position: int):
        self.opcode = opcode
        self.position = position
        self.args = []

    def addArgument(self, arg: Argument):
        self.args.append(arg)


class Encoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Command) or isinstance(obj, Argument):
            return obj.__dict__
        return json.JSONEncoder.default(self, obj)


def write_code(filename: str, code: list[Command]) -> None:
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(code, indent=4, cls=Encoder))


def read_code(filename: str) -> object:
    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())

    for instr in code:
        instr['opcode'] = Opcode(instr['opcode'])
        if 'term' in instr:
            instr['term'] = Command(instr['term'][0], instr['term'][1],
                                    AddrMode(instr['term'][2]), instr['term'][3])

    return code
