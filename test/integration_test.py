"""
Интеграционные тесты для процессора и транслятора
"""
import contextlib
import os
import unittest
from src.machine import machine
from src.translation import translator


class IntegrationTest(unittest.TestCase):
    """
    Unit-тесты для процессора
    """

    input = "resources/input.txt"

    def run_machine(self, code: str, output: str) -> str:
        """Выполнение транслятора и процессора с заданными параметрами"""
        translator.main([code, output])
        return machine.main([output, self.input])

    def test_prob5(self):
        """Тест prob5"""
        output = self.run_machine("resources/source/prob5.asm", "resources/result/prob5.json")
        self.assertEqual(output, '232792560')

    def test_cat(self):
        """Тест cat"""
        output = self.run_machine("resources/source/cat.asm", "resources/result/prob5.json")
        self.assertEqual(output,
                         '68(D) 111(o) 33(!) 59(;) 44(,) 10(\n) 64(@) 49(1) ')

    def test_hello(self):
        """Тест hello"""
        output = self.run_machine("resources/source/hello.asm", "resources/result/hello.json")
        self.assertEqual(output,
                         '104(h) 101(e) 108(l) 108(l) 111(o) 44(,) 32( ) 119(w) 111(o) 114(r) 108(l) 100(d) 33(!) ')

    def test_cat_trace(self):
        """Тест журнала на примере cat"""
        with self.assertLogs('', level='DEBUG') as logs:
            self.run_machine("resources/source/cat.asm", "resources/result/prob5.json")

        file = open("tmp.txt", "w")
        for line in logs.output:
            file.write(line)

        file = open("tmp.txt", "r")
        current_logs: list[str] = []

        for log in file.read().split('\n'):
            current_logs.append(str(log))
            print(log)

        file.close()
        os.remove("tmp.txt")

        expect_logs = [
            'DEBUG:root:TICK: 0, PC: 2, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 0, MEM_BUS: 0, Z: False, P: False, STEP_COUNTER: 0 -DEBUG:root:TICK: 1, PC: 2, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 0, MEM_BUS: 0, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 2, OPCODE: jmp, ARGS: [(\'relative\', 1)]',
            'DEBUG:root:TICK: 2, PC: 2, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 0, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 2, OPCODE: jmp, ARGS: [(\'relative\', 1)]',
            'DEBUG:root:TICK: 3, PC: 3, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 0, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 2, OPCODE: jmp, ARGS: [(\'relative\', 1)]',
            'DEBUG:root:TICK: 4, PC: 3, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 0, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 5, PC: 3, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 6, PC: 4, ADDR_BUS: 0, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 7, PC: 4, ADDR_BUS: 0, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 8, PC: 5, ADDR_BUS: 1, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 9, PC: 5, ADDR_BUS: 1, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 10, PC: 5, ADDR_BUS: 1, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 11, PC: 3, ADDR_BUS: 1, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 12, PC: 3, ADDR_BUS: 1, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 13, PC: 3, ADDR_BUS: 0, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 14, PC: 4, ADDR_BUS: 0, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 15, PC: 4, ADDR_BUS: 0, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 16, PC: 5, ADDR_BUS: 1, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 17, PC: 5, ADDR_BUS: 1, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 18, PC: 5, ADDR_BUS: 1, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 19, PC: 3, ADDR_BUS: 1, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 20, PC: 3, ADDR_BUS: 1, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 21, PC: 3, ADDR_BUS: 0, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 22, PC: 4, ADDR_BUS: 0, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 23, PC: 4, ADDR_BUS: 0, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 24, PC: 5, ADDR_BUS: 1, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 25, PC: 5, ADDR_BUS: 1, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 26, PC: 5, ADDR_BUS: 1, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 27, PC: 3, ADDR_BUS: 1, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 28, PC: 3, ADDR_BUS: 1, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 29, PC: 3, ADDR_BUS: 0, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 30, PC: 4, ADDR_BUS: 0, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 31, PC: 4, ADDR_BUS: 0, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 32, PC: 5, ADDR_BUS: 1, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 33, PC: 5, ADDR_BUS: 1, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 34, PC: 5, ADDR_BUS: 1, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 35, PC: 3, ADDR_BUS: 1, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 36, PC: 3, ADDR_BUS: 1, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 37, PC: 3, ADDR_BUS: 0, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 38, PC: 4, ADDR_BUS: 0, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 39, PC: 4, ADDR_BUS: 0, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 40, PC: 5, ADDR_BUS: 1, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 41, PC: 5, ADDR_BUS: 1, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 42, PC: 5, ADDR_BUS: 1, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 43, PC: 3, ADDR_BUS: 1, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 44, PC: 3, ADDR_BUS: 1, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 45, PC: 3, ADDR_BUS: 0, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 46, PC: 4, ADDR_BUS: 0, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 47, PC: 4, ADDR_BUS: 0, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 48, PC: 5, ADDR_BUS: 1, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 49, PC: 5, ADDR_BUS: 1, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 50, PC: 5, ADDR_BUS: 1, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 51, PC: 3, ADDR_BUS: 1, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 52, PC: 3, ADDR_BUS: 1, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 53, PC: 3, ADDR_BUS: 0, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 54, PC: 4, ADDR_BUS: 0, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 55, PC: 4, ADDR_BUS: 0, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 56, PC: 5, ADDR_BUS: 1, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 57, PC: 5, ADDR_BUS: 1, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 58, PC: 5, ADDR_BUS: 1, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 59, PC: 3, ADDR_BUS: 1, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 60, PC: 3, ADDR_BUS: 1, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 61, PC: 3, ADDR_BUS: 0, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 62, PC: 4, ADDR_BUS: 0, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'DEBUG:root:TICK: 63, PC: 4, ADDR_BUS: 0, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 64, PC: 5, ADDR_BUS: 1, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 4, OPCODE: st, ARGS: [(\'absolute\', 1), (\'register\', <Register.R2: \'r2\'>)]',
            'DEBUG:root:TICK: 65, PC: 5, ADDR_BUS: 1, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 66, PC: 5, ADDR_BUS: 1, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 1 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 67, PC: 3, ADDR_BUS: 1, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 2 ',
            'CELL_NUMBER: 5, OPCODE: jmp, ARGS: [(\'relative\', -2)]',
            'DEBUG:root:TICK: 68, PC: 3, ADDR_BUS: 1, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 0 ',
            'CELL_NUMBER: 3, OPCODE: ld, ARGS: [(\'register\', <Register.R2: \'r2\'>), (\'absolute\', 0)]',
            'WARNING:root:Input buffer came to the end'
        ]

        self.assertEqual(current_logs, expect_logs)
