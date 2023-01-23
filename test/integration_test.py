"""
Интеграционные тесты для процессора и транслятора
"""

import unittest
import src.machine.machine as machine
import src.translation.translator as translator





class IntegrationTest(unittest.TestCase):
    """
    Unit-тесты для процессора
    """

    input = "resources/input.txt"

    def run_machine(self, code: str, output: str) -> str:
        translator.main([code, output])
        return machine.main([output, self.input])

    def test_prob5(self):
        output = self.run_machine("resources/source/prob5.asm", "resources/result/prob5.json")
        self.assertEqual(output, '232792560')

    def test_cat(self):
        output = self.run_machine("resources/source/cat.asm", "resources/result/prob5.json")
        self.assertEqual(output,
                         '68(D) 111(o) 33(!) 59(;) 44(,) 10(\n) 64(@) 49(1) ')

    def test_hello(self):
        output = self.run_machine("resources/source/hello.asm", "resources/result/hello.json")
        self.assertEqual(output,
                         '104(h) 101(e) 108(l) 108(l) 111(o) 44(,) 32( ) 119(w) 111(o) 114(r) 108(l) 100(d) 33(!) ')
