# Assembler. Транслятор и модель

- Мокров Семён Андреевич, гр. Р33121
- `asm | risc | neum | hw | tick | struct | stream | mem | prob5`

## Язык программирования

``` ebnf
program ::= line "\n" program

line ::= label
       | variable
       | comment
       | command
       | section

label ::= "." name ":"

variable ::= name ":"

comment ::= ; <any sequence>

command ::= "\t" operation_2_args " " operand ", " operand |
            "\t" operation_1_arg " " operand |
            "\t" operation_0_args |

section ::= "section ." section_name

section_name ::= "text" | "data"

operation_3_args ::= "ADD" | "SUB" | "DIV" | "MOD" | "MUL"

operation_2_args ::= "CMP" | "LD" | "ST" | "MOV"

operation_1_arg ::= "JMP" | "JE" | "JNE" | "JG" | "INC" | "DEC"

operation_0_args ::= "HLT"

operand ::= %r1 | .label | #var | (var) | char | number    ; var here is variable in memory, 
                                                           ; # and () - address mode

char ::= [a-z]
          
number ::= [-2^64; 2^64 - 1]

```

Поддерживаемые аргументы:

- **регистр** - `%r1`. Всего регистров 5: r1, r2, r3, r4, r5.
- **объявленная метка** - `.<label>:`.
- **адрес памяти** - `#1`. Рекомендуется использовать **только**
  с зарезервированными переменными. **Нельзя** использовать с именами объявленных переменных
- **объявленная переменная** - `(NAME)`. Переменная обязательно должна находиться в скобках.
- **символ** - `'a'`. Транслируется в код ASCII. **Нельзя** указывать несколько символов сразу (строки не поддерживаются). Символ обязательно должен находиться в одинарных кавычках
- **целое число** в диапазоне [-2^64 ; 2^64 - 1].


Виды операций:

- **регистровая** операция - может использовать в качестве операндов регистры или значения: символ, число. Первые n-1 операндов должны быть регистрами (n - кол-во операндов, если n = 1, то операнд должен быть регистром).
- операция **перехода** - может поддерживать метки в качестве операндов. Должна иметь 1 операнд-метку.
- операция **по работе с памятью** - может поддерживать адреса и имена переменных в качестве операндов. Один из операндов должен быть регистром
- часть операций может соблюдать ограничения, иметь свои ограничения на операнды или может не иметь операндов вовсе (см. операции)


Код находится в `section .text` и выполняется последовательно. Операции:

- `ADD <arg1> <arg2> <arg3>` -- прибавить ко второму аргументу третий, результат поместить в первый. *Регистровая операция*.
- `SUB <arg1> <arg2> <arg3>` -- вычесть из второго аргумента третий, результат поместить в первый. *Регистровая операция*
- `DIV <arg1> <arg2> <arg3>` -- получить целую часть от деления второго аргумента на третий, результат поместить в первый. *Регистровая операция*
- `MOD <arg1> <arg2> <arg3>` -- получить остаток от деления второго аргумента на третий, результат поместить в первый. *Регистровая операция*
- `MUL <arg1> <arg2> <arg3>` -- получить произведение второго аргумента на третий, результат поместить в первый. *Регистровая операция*
- `MOV <arg1> <arg2>` -- скопировать значение из второго аргумента в первый. *Регистровая операция*
- `CMP <arg1> <arg2>` -- получить результат сравнения второго аргумента с первым (0, если аргументы равны). *Регистровая операция*
- `LD <arg1> <arg2>` -- загрузить в 1 операнд 2. 2 операндом может выступать только адрес или имя ячейки, 1 операндом может выступать только регистр. *Регистровая операция* и операция *по работе с памятью*
- `ST <arg1> <arg2>` -- загрузить в 2 операнд 1. 1 операндом может выступать только адрес или имя ячейки, 2 операндом может выступать только регистр. *Регистровая операция* (нарушает общие правила) и операция *по работе с памятью*
- `INC <arg>` -- инкрементировать операнд (+1). Может иметь в качестве операнда только регистр. *Регистровая операция*
- `DEC <arg>` -- декрементировать (-1) операнд. Может иметь в качестве операнда только регистр. *Регистровая операция*
- `JE <label>` -- если результат предыдущей операции равен 0, перейти на аргумент-метку. *Операция перехода*
- `JNE <label>` -- если результат предыдущей операции не равен 0, перейти на аргумент-метку. *Операция перехода*
- `JG <label>` -- если результат предыдущей операции больше 0, перейти на аргумент-метку. *Операция перехода*
- `JMP <label>` -- безусловный переход на аргумент-метку. *Операция перехода*
- `HLT` -- завершить выполнение программы

Переменные объявляются в `section .data` и имеют следующий синтаксис - `<VAR>: <value>`:
- `<VAR>` - имя переменной. При обращении к нему необходимо учитывать регистр. Имя не должно иметь пробелов и должно заканчиваться символом `:`
- `<value>` - значение переменной. Может быть числом или символом (`'a'`). Правила записи те же, что и для аргументов.
- Одна переменная должна располагаться на 1 строчке.
- Не имеют фиксированного адреса  памяти.

Дополнительные конструкции:

- `; <any sequence not containing ';'>` - комментарий
- `section .text` - объявление секции кода
- `section .data` - объявление секции данных
- `.<label>:` - метки для переходов / названия переменных. Могут быть объявлены только в `section .text`. Должны располагаться на отдельной строчке

Зарезервированные переменные:
  - Имеют фиксированный адрес в памяти
  - Возможно обратиться только напрямую через адрес в памяти (#STDIN)
  - При трансляции превращаются в их адрес
  - Виды:
    - ```STDIN``` - при чтении переменной происходит ввод данных. В переменную нельзя записывать.
    - ``STDOUT`` - при записи в переменную происходит вывод данных. Из переменной нельзя читать.


Примечания:

- Результаты операций с 3 аргументами (если он есть) помещаются в 1 аргумент
- Должен присутствовать `section .text` - тело программы
- Должна присутствовать метка `.start:` в `section .text` - точка входа в программу
- При обращении к необъявленной метке или переменной возникнет ошибка.
- Все составляющие языка **регистрозависимы**

## Система команд

### Особенности процессора:

- **Машинное слово** -- 64 бита, знаковое.
- **Память:**
    - адресуется через регистры `pс_counter` и через шину данных `addr_bus`;
    - может быть записана из регистровый файл;
    - может быть прочитана в регистровый файл или в `Instruction Decoder`;
    - имеет зарезервированные ячейки для подключения потоков ввода-вывода (задаются через конфигурацию).
- **Регистровый файл**:
    - состоит из регистров общего назначения размером с машинное слово
    - регистры расположены последовательно
    - всего регистров 5: *r1, r2, r3, r4, r5* (количество и названия регистров можно изменить в конфигурации)
    - имеет два выхода и 1 вход: `argument_1`, `argument_2`, `out`. Устанавливаются при помощи сигналов Instruction Decoder.
    - регистр, подключенный к `out`, может быть записан из памяти, АЛУ (связанного с ним), регистра, подключенного к `argument_1` или операндом из `Instruction Decoder`
    - регистр, подключенный к `argument_1` может быть прочитан в левый вход к АЛУ (подключенному к регистровому файлу) или в регистр, подключенный к `out`
    - регистр, подключенный к `argument_2` может быть прочитан в память или на правый вход АЛУ (подключенного к регистровому файлу)
- **АЛУ, соединенный с регистровым файлом**:
  - имеет два входа и 1 выход
  - прозводит арифметические операции с регистрами общего назначения и аргументами из Instruction Decoder
  - управляется сигналами из Instruction Decoder
  - устанавливает флаг равенства нулю и флаг положительного результата по результату вычисленной операции
  - умеет складывать, вычитать, умножать, делить нацело, получать остаток от деления
  - результат вычислений записывается в регистр общего назначения
- **АЛУ, соединенный с регистровым файлом**:
  - имеет два входа и 1 выход
  - прозводит арифметические операции с `pc_couner` и аргументами из Instruction Decoder
  - управляется сигналами из Instruction Decoder
  - умеет складывать, вычитать, умножать, делить нацело, получать остаток от деления
  - результат вычислений записывается в `pc_counter` или передается на шину `addr_bus`
  - используется для вычисления смещения
- **step_counter** -- счетчик шагов:
  - отвечает за хранения номера шага текущей команды
  - меняет значение каждый такт
  - меняется через аргументы от Instruction Decoder
  - может быть обнулен или увеличен на 1
- **Instruction Decoder** -- декодировщик инструкций:
  - отвечает за декодирование и исполнение инструкций
  - отправляет управляющие сигналы
  - может читать инструкцию из памяти, флаги, установленные АЛУ, и step_counter
- **Ввод-вывод** -- memory-mapped через резервированные ячейки памяти, символьный. Ячейки задаются через конфигурацию.
- **pс_counter** -- счётчик команд:
    - инкрементируется после каждой инструкции или перезаписывается инструкцией перехода (с учетом смещения).

### Набор инструкций

Аргументы и их ограничения:
- число в диапазоне [-2^64 ; 2^64 - 1]
- смещение относительно текущего значения `pc_counter` - сумма не должна выходить за пределы памяти
- адрес в памяти  - адрес не должен выходить за пределы памяти
- регистр - должен находиться в регистровом файле
- ограничения на аргументы у каждой отдельной инструкции выходят из языка программирования (см п.1)

| Syntax                                  | Mnemonic                                | Ticks | Comment                                                                                                                                             |
|:----------------------------------------|:----------------------------------------|-------|:----------------------------------------------------------------------------------------------------------------------------------------------------|
| `add/sub/mul/div/mod <arg> <arg> <arg>` | ADD/SUB/MUL/DIV/MOD `<arg> <arg> <arg>` | 3     | кол-во тактов фиксировано                                                                                                                           |
| `cmp <arg> <arg>`                       | CMP `<arg>`                             | 2     | кол-во тактов фиксировано                                                                                                                           |
| `mov <arg> <arg>`                       | MOV `<arg> <arg>`                       | 3     | кол-во тактов фиксировано                                                                                                                           |
| `je, jne, jg, jmp <arg>`                | JE, JNE, JG, JMP `<arg> <arg>`          | 2-3   | кол-во тактов зависит от флагов АЛУ <br/>работают только с относительной адресацией                                                                 |
| `inc/dec <arg>`                         | INC/DEC `<arg>`                         | 3     | кол-во тактов фиксировано                                                                                                                           |
| `hlt`                                   | HLT                                     | 0     | вызывает остановку симуляции                                                                                                                        |
| `data <arg>`                            | DATA `<arg>`                            | 0     | инструкция хранения данных - реализует ячейки памяти с данными                                                                                      |
| `ld <arg> <arg>`                        | LD `<arg> <arg>`                        | 3-4   | Выполняет чтение из указанной ячейки памяти<br/>Поддерживает абсолютную и относительную адресации<br/>Количество тактов зависит от режима адресации |
| `st <arg> <arg>`                        | ST `<arg> <arg>`                        | 2-3   | Выполняет запись в указанную ячейку памяти<br/>Поддерживает абсолютную и относительную адресации<br/>Количество тактов зависит от режима адресации  |

### Кодирование инструкций

- Машинный код сериализуется в список JSON.
- Один элемент списка, одна инструкция.
- Инструкция имеет фиксированный размер - машинное слово

Пример:

```json
[{
        "opcode": "mov",
        "position": 1,
        "args": [
            {
                "data": "r4",
                "mode": "register"
            },
            {
                "data": 20,
                "mode": "data"
            }
        ]
    }
]
```

где:

- `opcode` -- строка с кодом операции;
- `position` -- позиция инструкции в памяти
- `args` -- аргументы инструкции:
  - `mode` -- режим адресации аргумента
  - `data` -- значение аргумента

Типы данных в модуле [isa](./src/translation/isa.py), где:

- `Opcode` -- перечисление кодов операций;
- `AddrMode` -- перечисление режимов аддресации:
  - `REG` -- аргумент является регистром. Поле `data`: регистр
  - `REL` -- аргумент отражает относительную адресацию. Поле `data`: смещение
  - `ABS` -- аргумент отражает прямую адресацию. Поле `data`: адрес
  - `DATA` -- аргумент является значением. Поле `data`: число
- `Operation` -- структура для описания всей необходимой информации об инструкции.
- `Argument` -- структура для описания всей необходимой информации об аргументе


## Транслятор

Интерфейс командной строки: `translator.py <input_file> <target_file>"`

Реализовано в модуле: [translator](src/translation/translator.py)

Этапы трансляции (функция `translate`):

1. Препроцессирование исходного кода: удаление лишних пробелов, запятых, комментариев. Реализовано в функции `preprocessing` модуля [preprocessor](src/translation/preprocessor.py)
2. Проверка наличия метки `.start`
3. Преобразование `section .text` в машинный код (с учетом ограничений) - функция `parse_text`
4. Преобразование `section .data` в машинный код (с учетом ограничений) - функция `parse_data`
5. Объединение машинных кодов двух секций и определение адресов переменных внутри команд - функция `join_text_and_data`
6. Установка стартового адреса программы (с учетом смещения относительно данных и зарезервированных ячеек) - функция `add_start_address`

Правила генерации машинного кода:

- один `Operation` (класс, описывающий операцию) -- одна инструкция;
- в начале каждой программы стоит команда `jmp`, которая указывает на стартовый адрес
- вместо регистров подставляются их имена (экземпляры enum `Register`)
- вместо адресов в памяти подставляются сами адреса или адреса зарезервированных ячеек (если они используются)
- вместо переменных подставляется смещение относительно текущего адреса,
- вместо меток подставляется смещение относительно текущего адреса до ячеек памяти, на которые они указывают.
- вместо символов подставляются их ASCII коды
- числа остаются числами

## Модель процессора
### Схема DataPath и ControlUnit
### DataPath
### ControlUnit

## Апробация


| ФИО         | алг.  | LoC | code байт | code инстр. | инстр. | такт. | вариант      |
|-------------|-------|-----|-----------|-------------|--------|-------|--------------|
| Мокров С.А. | hello | 41  | -         | 38          | 28     | 83    | см. в начале |
| Мокров С.А. | cat   | 6   | -         | 4           | 26     | 69    | см. в начале |
| Мокров С.А. | prob5 | 39  | -         | 27          | 1475   | 4196  | см. в начале |