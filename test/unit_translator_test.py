"""
Unit-тесты для транслятора
"""

import unittest

from src.translation import isa, translator


class TranslatorTest(unittest.TestCase):
    """Unit-тесты для транслятора"""

    def simple_test(self, input_file, output, correct):
        """Тест траслятора"""
        translator.main([input_file, output])

        result_code = isa.read_code(output)
        correct_code = isa.read_code(correct)

        self.assertEqual(len(result_code), len(correct_code))

        for idx, operation in enumerate(result_code):
            self.assertEqual(operation.opcode, correct_code[idx].opcode)
            self.assertEqual(operation.position, correct_code[idx].position)
            for arg_idx, arg in enumerate(operation.args):
                self.assertEqual(arg.mode, correct_code[idx].args[arg_idx].mode)
                self.assertEqual(arg.data, correct_code[idx].args[arg_idx].data)

    def test_cat(self):
        """Тест cat"""
        self.simple_test("resources/source/cat.asm", "resources/result/cat.json",
                         "resources/correct/cat.json")

    def test_prob5(self):
        """Тест prob5"""
        self.simple_test("resources/source/prob5.asm", "resources/result/prob5.json",
                         "resources/correct/prob5.json")

    def test_hello_world(self):
        """Тест hello"""
        self.simple_test("resources/source/hello.asm", "resources/result/hello.json",
                         "resources/correct/hello.json")
