"""
Unit-тесты для процессора
"""
import unittest

from src.machine.machine import ControlUnit
from src.translation.isa import Operation, read_code, Opcode, Register


class MachineTest(unittest.TestCase):
    """Unit-тесты для процессора"""

    input = "resources/input.txt"
    cu = ControlUnit()

    def set_program_and_run(self, code: list[Operation]):
        """Запуск тестовой программы"""
        self.cu.set_program(code, [])
        try:
            while True:
                self.cu.decode_and_execute_instruction()
        except Exception as exception:
            self.assertIsInstance(exception, StopIteration)

    def get_start_addr(self) -> int:
        """Получение стартового адреса"""
        prog_addr: int = 0
        operation: Operation = self.cu.data_path.memory[prog_addr]

        while operation.opcode == Opcode.DATA:
            prog_addr += 1
            operation = self.cu.data_path.memory[prog_addr]

        return prog_addr

    def test_alu_addr(self):
        """Тестирования АЛУ для вычисления адреса"""
        code: list[Operation] = read_code("resources/examples_correct/alu_addr.json")
        self.set_program_and_run(code)

        prog_addr: int = self.get_start_addr()

        self.assertEqual(self.cu.data_path.pc_counter, prog_addr + 1)

    def test_alu_data(self):
        """Тестирование АЛУ для вычисления данных"""
        code: list[Operation] = read_code("resources/examples_correct/alu_data.json")

        self.set_program_and_run(code)
        self.assertEqual(self.cu.data_path.reg_file.registers[Register.R1], 6)
        self.assertEqual(self.cu.data_path.reg_file.registers[Register.R2], 2)

        self.assertEqual(self.cu.data_path.data_alu_bus, 3)
        self.assertEqual(self.cu.data_path.get_positive_flag(), True)
        self.assertEqual(self.cu.data_path.reg_file.registers[Register.R3], 3)

    def test_reg_file(self):
        """Тестирование работы регистрового файла"""
        code: list[Operation] = read_code("resources/examples_correct/reg_file.json")

        self.set_program_and_run(code)

        self.assertEqual(self.cu.data_path.reg_file.registers[Register.R1], 5)
        self.assertEqual(self.cu.data_path.reg_file.registers[Register.R3], 5)
        self.assertEqual(self.cu.data_path.reg_file.registers[Register.R4], 5)

    def test_load(self):
        """Тестирование работы чтения из памяти"""
        code: list[Operation] = read_code("resources/examples_correct/load.json")

        self.set_program_and_run(code)

        self.assertEqual(self.cu.data_path.reg_file.registers[Register.R1], 26)
        self.assertEqual(self.cu.data_path.reg_file.registers[Register.R2], 24)

    def test_stoan(self):
        """Проверка работы записи в память"""
        code: list[Operation] = read_code("resources/examples_correct/stoan.json")

        self.set_program_and_run(code)

        prog_addr = self.get_start_addr()

        self.assertEqual(self.cu.data_path.memory[prog_addr].args[0].data, 2)

        self.assertEqual(self.cu.data_path.output_buffer[0], 2)
