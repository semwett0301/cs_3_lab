"""Конфигурация работы CU и DataPath"""

from enum import Enum


class Register(str, Enum):
    """Список поддерживаемых регистров"""
    R1 = 'r1'
    R2 = 'r2'
    R3 = 'r3'
    R4 = 'r4'
    R5 = 'r5'


class ReservedVariable(int, Enum):
    """Адреса зарезервированных переменных"""
    STDIN = 0
    STDOUT = 1


# Длина машинного слова
WORD_LENGTH: int = 64

# Количество ячеек памяти
AMOUNT_OF_MEMORY = 1024


def resolve_overflow(arg: int) -> int:
    """Отвечает за соблюдение машинного слова"""
    while arg > 9223372036854775807:
        arg = -9223372036854775808 + (arg - 9223372036854775808)
    while arg < -9223372036854775808:
        arg = 9223372036854775808 - (arg + 9223372036854775808)

    return arg
