"""Конфигурация работы CU и DataPath"""

from enum import Enum

from src.translation.isa import Opcode, Register


class ReservedVariable(int, Enum):
    """Адреса зарезервированных переменных"""
    STDIN = 0
    STDOUT = 1


# Длина машинного слова
WORD_LENGTH: int = 64

# Количество ячеек памяти
AMOUNT_OF_MEMORY = 1024


class AluOperations(Enum):
    """Список операций АЛУ"""
    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3
    MOD = 4


# Соотношение операций команд и операций АЛУ, связанного с регистровым файлом
opcode2operation = {
    Opcode.ADD: AluOperations.ADD,
    Opcode.SUB: AluOperations.SUB,
    Opcode.MUL: AluOperations.MUL,
    Opcode.DIV: AluOperations.DIV,
    Opcode.MOD: AluOperations.MOD,
    Opcode.CMP: AluOperations.SUB,
    Opcode.INC: AluOperations.ADD,
    Opcode.DEC: AluOperations.ADD
}


class RegLatchSignals(Enum):
    """Список управляющих сигналов для latch_reg"""
    ALU = 0
    ARG = 1
    MEM = 2
    REG = 3


class Alu:
    """Арифметико-логическое устройство с двумя входами данных и сигналом операции."""

    def __init__(self):
        self.left: int = 0
        self.right: int = 0
        self.operations: dict = {
            AluOperations.DIV: lambda left, right: left / right,
            AluOperations.MOD: lambda left, right: left % right,
            AluOperations.ADD: lambda left, right: left + right,
            AluOperations.SUB: lambda left, right: left - right,
            AluOperations.MUL: lambda left, right: left * right,
        }


class RegFile:
    """Класс эмулирующий регистровый файл"""

    def __init__(self):
        self.registers = {
            Register.R1: 0,
            Register.R2: 0,
            Register.R3: 0,
            Register.R4: 0,
            Register.R5: 0
        }
        self.argument_1: Register = Register.R1
        self.argument_2: Register = Register.R1
        self.out: Register = Register.R1


def resolve_overflow(arg: int) -> int:
    """Отвечает за соблюдение машинного слова"""
    while arg > 2 ** WORD_LENGTH:
        arg = -2 ** WORD_LENGTH + (arg - 2 ** WORD_LENGTH)
    while arg < -2 ** WORD_LENGTH:
        arg = 2 ** WORD_LENGTH - (arg + 2 ** WORD_LENGTH)

    return arg
