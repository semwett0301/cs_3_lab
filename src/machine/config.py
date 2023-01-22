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


