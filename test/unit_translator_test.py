"""
Unit-тесты для транслятора
"""

import unittest

from src.translation import isa, translator


class TranslatorTest(unittest.TestCase):
    """Unit-тесты для транслятора"""

    def simple_test(self, input_file, output, correct):
        translator.main([input_file, output])

        result_code = isa.read_code(output)
        correct_code = isa.read_code(correct)

        self.assertEqual(result_code, correct_code)

    def test_cat(self):
        self.simple_test("resources/source/cat.asm", "resources/result/cat.json",
                         "resources/correct/cat.json")

    def test_prob5(self):
        self.simple_test("resources/source/prob5.asm", "resources/result/prob5.json",
                         "resources/correct/prob5.json")

    def test_hello_world(self):
        self.simple_test("resources/source/hello.asm", "resources/result/hello.json",
                         "resources/correct/hello.json")
