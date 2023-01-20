"""Модуль описания системы команд (содержит функции кодирования и декодирования команд"""
import json

from enum import Enum
from src.config import Register


class Opcode(str, Enum):
    """Коды операций"""

    DATA = 'data'
    HLT = 'hlt'

    LD = 'ld'
    ST = 'st'

    ADD = 'add'
    SUB = 'sub'
    MUL = 'mul'
    MOD = 'mod'
    DIV = 'div'
    CMP = 'cmp'
    MOV = 'mov'

    INC = 'inc'
    DEC = 'dec'

    JMP = 'jmp'
    JE = 'je'
    JNE = 'jne'
    JG = 'jg'


class AmountOperandType(int, Enum):
    """Количество операндов, которые должны бытьу команды"""
    TWO = 2,
    ONE = 1,
    NONE = 0


class OperationType(str, Enum):
    """Вид операции"""
    MEM = 'mem',
    BRANCH = 'branch',
    REGISTER = 'register'


class OperationRestriction:
    """Все ограничения конкретной операции"""

    def __init__(self, amount: AmountOperandType):
        self.amount = amount
        self.types: list[OperationType] = []

    def add_operation_type(self, *operation_types: OperationType) -> object:
        for current_type in operation_types:
            self.types.append(current_type)
        return self


# Конфигурация ограничений операций
no_op_restriction = OperationRestriction(AmountOperandType.NONE)

branch_op_restriction = OperationRestriction(AmountOperandType.ONE)
branch_op_restriction.add_operation_type(OperationType.BRANCH)

inc_dec_op_restriction = OperationRestriction(AmountOperandType.ONE)
inc_dec_op_restriction.add_operation_type(OperationType.REGISTER)

data_op_restriction = OperationRestriction(AmountOperandType.TWO)
data_op_restriction.add_operation_type(OperationType.REGISTER, OperationType.MEM)

reg_op_restriction = OperationRestriction(AmountOperandType.TWO)
reg_op_restriction.add_operation_type(OperationType.REGISTER)

# Сбор ограничений для каждой операции
OperationRestrictionConfig: dict[Opcode, OperationRestriction] = {
    Opcode.DATA: no_op_restriction,
    Opcode.HLT: no_op_restriction,

    Opcode.JMP: branch_op_restriction,
    Opcode.JE: branch_op_restriction,
    Opcode.JNE: branch_op_restriction,
    Opcode.JG: branch_op_restriction,

    Opcode.INC: inc_dec_op_restriction,
    Opcode.DEC: inc_dec_op_restriction,

    Opcode.LD: data_op_restriction,
    Opcode.ST: data_op_restriction,

    Opcode.ADD: reg_op_restriction,
    Opcode.SUB: reg_op_restriction,
    Opcode.MOV: reg_op_restriction,
    Opcode.MOD: reg_op_restriction,
    Opcode.DIV: reg_op_restriction,
    Opcode.MUL: reg_op_restriction,
    Opcode.CMP: reg_op_restriction,
}


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
        """Функция добавления аргументов к команде (операции)"""
        self.args.append(arg)

    def is_corr_to_type(self, operation_type: OperationType) -> bool:
        return operation_type in OperationRestrictionConfig[self.opcode].types


class Encoder(json.JSONEncoder):
    """Класс-энкодер для записи и чтения из JSON"""

    def default(self, o):
        if isinstance(o, (Argument, Operation)):
            return o.__dict__
        return json.JSONEncoder.default(self, o)


def write_code(filename: str, code: list[Operation]) -> None:
    """Функция кодирования и записи команд"""
    print(json.dumps(code, indent=4, cls=Encoder))
    with open(filename, "w", encoding="utf-8") as file:
        file.write(json.dumps(code, indent=4, cls=Encoder))


def read_code(filename: str) -> object:
    """Функция декодирования и чтения команд"""

    with open(filename, encoding="utf-8") as file:
        code = json.loads(file.read())  # type: ignore

    for instr in code:
        instr['opcode'] = Opcode(instr['opcode'])
        for arg in instr['args']:
            arg = Argument(AddrMode(arg['mode']), arg['data'])

    return code
