"""
Unit-тесты для транслятора
"""

import unittest

from src.translation import isa, translator


class ValidationTest(unittest.TestCase):
    """Unit-тесты для транслятора"""

    def simple_test_assert(self, input_file, output):
        """Тест валидации через assert"""
        with self.assertRaises(AssertionError):
            translator.main([input_file, output])

    def simple_test_type_error(self, input_file, output):
        """Тест валидации через TypeError"""
        with self.assertRaises(TypeError):
            translator.main([input_file, output])

    def test_label(self):
        """Тест неправильного label"""
        self.simple_test_assert("resources/incorrect/label.asm", "resources/incorrect/label.json")

    def test_start(self):
        """Тест на наличие метки старт"""
        self.simple_test_assert("resources/incorrect/start.asm", "resources/incorrect/start.json")

    def test_variable(self):
        """Тест неправильного значения или названия перменной"""
        self.simple_test_type_error("resources/incorrect/variable.asm", "resources/incorrect/variable.json")

    def test_operand_variable(self):
        """Тест операнда переменной"""
        self.simple_test_assert("resources/incorrect/operand_variable.asm", "resources/incorrect/operand_variable.json")
        self.simple_test_assert("resources/incorrect/unkown_variable.asm", "resources/incorrect/unkown_variable.json")

    def test_operand_char(self):
        """Тест операнда символа"""
        self.simple_test_type_error("resources/incorrect/operand_char.asm", "resources/incorrect/operand_char.json")

    def test_operand_num(self):
        """Тест операнда числа"""
        self.simple_test_type_error("resources/incorrect/operand_num.asm", "resources/incorrect/operand_num.json")

