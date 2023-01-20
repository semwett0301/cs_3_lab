"""Модуль препроцессорной обработки"""

import re


def remove_comment(line: str) -> str:
    return re.sub(r';.*', '', line)


def remove_extra_spaces(line: str) -> str:
    return re.sub(r'\s+', ' ', line)


def remove_commas(line: str) -> str:
    return line.replace(',', ' ')


def preprocessing(asm_text: str) -> str:
    lines: list[str] = asm_text.splitlines()

    remove_comments = map(remove_comment, lines)
    strip_lines = map(str.strip, remove_comments)
    remove_empty_lines = filter(bool, strip_lines)
    removed_commas = map(remove_commas, remove_empty_lines)
    remove_spaces = map(remove_extra_spaces, removed_commas)

    minified_text: str = '\n'.join(remove_spaces)

    return minified_text
