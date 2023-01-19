import json
import unittest

from translation import translator
from translation.isa import Encoder


class TestTranslator(unittest.TestCase):

    def test_translation(self):
        with open("resources/prob5.asm", "rt", encoding="utf-8") as file:
            text = file.read()

        code = translator.translate(text)
        self.assertEqual([
            {
                "opcode": "jmp",
                "position": 1,
                "args": [
                    {
                        "data": 2,
                        "mode": "relative"
                    }
                ]
            },
            {
                "opcode": "data",
                "position": 2,
                "args": [
                    {
                        "data": "h",
                        "mode": "data"
                    }
                ]
            },
            {
                "opcode": "data",
                "position": 3,
                "args": [
                    {
                        "data": "a",
                        "mode": "data"
                    }
                ]
            },
            {
                "opcode": "ld",
                "position": 4,
                "args": [
                    {
                        "data": "r1",
                        "mode": "register"
                    },
                    {
                        "data": "HELLO",
                        "mode": "relative"
                    }
                ]
            },
            {
                "opcode": "cmp",
                "position": 5,
                "args": [
                    {
                        "data": "r1",
                        "mode": "register"
                    },
                    {
                        "data": "0x0",
                        "mode": "data"
                    }
                ]
            },
            {
                "opcode": "je",
                "position": 6,
                "args": [
                    {
                        "data": 3,
                        "mode": "relative"
                    }
                ]
            },
            {
                "opcode": "st",
                "position": 7,
                "args": [
                    {
                        "data": 2,
                        "mode": "absolute"
                    },
                    {
                        "data": "r1",
                        "mode": "register"
                    }
                ]
            },
            {
                "opcode": "inc",
                "position": 8,
                "args": [
                    {
                        "data": "r1",
                        "mode": "register"
                    }
                ]
            },
            {
                "opcode": "jmp",
                "position": 9,
                "args": [
                    {
                        "data": -6,
                        "mode": "relative"
                    }
                ]
            },
            {
                "opcode": "hlt",
                "position": 10,
                "args": []
            }
        ],
            json.dumps(code, indent=4, cls=Encoder))
