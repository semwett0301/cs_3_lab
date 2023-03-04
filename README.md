# Assembler. Translator and model

- Mokrov Simon Andreevich, gr. P33121
- `asm | risc | neum | hw | tick | struct | stream | mem | prob5`

## Programming language

``` ebnf
program ::= <section_data> <section_text> | <section_text> <section_data> | <section_text>

<section_data> ::= "section .data\n" <declaratione>*

<section_text> ::= "section .text\n" <instruction>*

<declaration> ::= <comment>* "\t"* (<variable> | <value>) "\n" <comment>*

<instruction> ::= <comment>* "\t"* (<label> | <command>) "\n" <comment>*

<label> ::= "." <name> ":"

<variable> ::= <name> ":"

<name> ::= [a-zA-Z]+

<value> ::= <number> | <char>

<comment> ::= ; <any sequence>

<command> ::= <operation_3_args> | <operation_2_args> | <operation_1_arg> | <operation_0_args>

operation_3_args ::= ("ADD" | "SUB" | "DIV" | "MOD" | "MUL") " " (<register_register_value> | <register_register_register>)

<register_register_value> ::= <reg> ", " <reg> ", " <number | char>

<register_register_register> ::= <reg> ", " <reg> ", " <reg>

operation_2_args ::= ("CMP" | "LD" | "ST" | "MOV") " " (<register_register> | <register_var_name> | <var_name_register>)

<register_register> ::= <reg> ", " <reg>

<register_var_name> ::= <reg> ", " "(" <name> ")"

<var_name_register> ::=  "(" <name> ")" ", " <reg>

operation_1_arg ::= ("JMP" | "JE" | "JNE" | "JG" | "INC" | "DEC") " " (<label> | <reg>)

operation_0_args ::= "HLT"

<reg=> ::= "r1" | "r2" | "r3" | "r4" | "r5" 

<char> ::= "<any ASCII symbol>"
          
<number> ::= [-2^64; 2^64 - 1]

```

Supported arguments:

- **register** - `%r1'. There are 5 registers in total: r1, r2, r3, r4, r5.
- **declared label** - `.<label>:`.
- **memory address** - `#1'. It is recommended to use **only**
with reserved variables. **Cannot** be used with the names of declared variables
- **declared variable** - `(NAME)`. The variable must be in parentheses.
- **symbol** - `a". Translated into ASCII code. **You cannot** specify multiple characters at once (strings are not supported). The symbol must be in single quotes
- **integer** in the range [-2^64 ; 2^64 - 1].


Types of operations:

- **register** operation - can use registers or values as operands: symbol, number. The first n-1 operands must be registers (n is the number of operands, if n = 1, then the operand must be a register).
- **transition** operation - can support labels as operands. Must have 1 operand label.
- memory operation *** - can support addresses and variable names as operands. One of the operands must be a register
- some operations may comply with restrictions, have their own restrictions on operands, or may not have operands at all (see operations)


The code is in the `section .text` and executed sequentially. Operations:

- `ADD <arg1> <arg2> <arg3>` -- add a third argument to the second, put the result in the first. *Register operation*.
- `SUB <arg1> <arg2> <arg3>` -- subtract the third argument from the second, put the result in the first. *Register operation*
- `DIV <arg1> <arg2> <arg3>` -- get the whole part from dividing the second argument by the third, put the result in the first. *Register operation*
- `MOD <arg1> <arg2> <arg3>` -- get the remainder from dividing the second argument by the third, put the result in the first. *Register operation*
- `MUL <arg1> <arg2> <arg3>` -- get the product of the second argument by the third, put the result in the first. *Register operation*
- `MOV <arg1> <arg2>` -- copy the value from the second argument to the first. *Register operation*
- `CMP <arg1> <arg2>` -- get the result of comparing the second argument with the first (0 if the arguments are equal). *Register operation*
- `LD <arg1> <arg2>` -- load 2 into 1 operand. 2 the operand can only be the address or name of the cell, 1 the operand can only be a register. *Register operation* and memory operation **
- 'ST <arg1> <arg2>` -- load into 2 operand 1. 1 the operand can only be the address or name of the cell, 2 the operand can only be the register. *Register operation* (violates general rules) and operation * for working with memory*
- `INC <arg>` -- increment the operand (+1). It can have only a register as an operand. *Register operation*

Variables are declared in `section .data` and have the following syntax - `<VAR>: <value>`:
- `<VAR>` - variable name. When accessing it, it is necessary to take into account the case. The name must not have spaces and must end with the character `:`
- `<value>` - the value of the variable. It can be a number or a symbol (`a"). The writing rules are the same as for arguments.
- One variable should be located on 1 line.
- Do not have a fixed memory address.

Additional designs:

- `; <any sequence not containing';'>` - comment
- `section .text` - declaration of the code section
- `section .data` - declaration of the data section
- `.<label>:` - labels for transitions / variable names. Can only be declared in `section .text`. Must be located on a separate line

Reserved variables:
- Have a fixed address in memory
- It is possible to access only directly through the address in memory (#STDIN)
- When translated, they turn into their address
- Types:
- ``STDIN`` - when reading a variable, data is entered. You cannot write to a variable.
- `STDOUT` - when writing to a variable, data is output. You cannot read from a variable.


Notes:

- The results of operations with 3 arguments (if any) are placed in 1 argument
- Must be present `section.text` - program body
- The label `.start:` must be present in the `section.text` - the entry point to the program
- An error will occur when accessing an undeclared label or variable.
- All components of the language **are case-sensitive**

## Memory organization
- It is possible to declare variables in `section .data`

Processor Memory Model:

- Data memory. The machine word is 64 bits, signed. Implemented by a list of processor instructions - `Operation'. Accessing memory takes 1 clock cycle.

Types of addressing:

- - Direct register: The operand of the instruction is a register.
- Direct loading: The operand is a constant supplied as one of the arguments.
- Direct absolute: the operand of the instruction is the memory address
- Direct relative: the operand of an instruction is an offset relative to the current instruction


## Command system

### Processor Features:

- **Machine word** -- 64 bits, signed.
- **Memory:**
- is addressed via the registers `p_counter` and via the data bus `addr_bus`;
- can be written from a register file;
- can be read into a register file or in the `Instruction Decoder`;
- has reserved cells for connecting I/O streams (set via configuration).
- **Register file**:
- consists of general purpose registers the size of a machine word
- registers are arranged sequentially
- there are 5 registers in total: *r1, r2, r3, r4, r5* (the number and names of registers can be changed in the configuration)
- has two outputs and 1 input: `argument_1`, `argument_2`, `out'. They are installed using Instruction Decoder signals.
- a register connected to `out` can be written from memory, an ALU (associated with it), a register connected to `argument_1` or an operand from `Instruction Decoder`
- the register connected to `argument_1` can be read into the left input to the ALU (connected to the register file) or into the register connected to `out`
- the register connected to `argument_2` can be read into memory or to the right input of the ALU (connected to the register file)
- **ALU connected to a register file**:
- has two inputs and 1 output
- performs arithmetic operations with general-purpose registers and arguments from Instruction Decoder
- controlled by signals from Instruction Decoder
- sets the flag of equality to zero and the flag of a positive result based on the result of the calculated operation
- can add, subtract, multiply, divide completely, get the remainder of the division
- the result of calculations is recorded in a general-purpose register
- **ALU connected to a register file**:
- has two inputs and 1 output
- performs arithmetic operations with `pc_couner` and arguments from Instruction Decoder
- controlled by signals from Instruction Decoder
- can add, subtract, multiply, divide completely, get the remainder of the division
- the result of calculations is written to `pc_counter` or transmitted to the `addr_bus` bus
- used to calculate the offset
- **step_counter** -- step counter:
- responsible for storing the step number of the current command
- changes the value every clock cycle
- changes via arguments from Instruction Decoder
- can be reset to zero or increased by 1
- **Instruction Decoder** -- Instruction Decoder:
- responsible for decoding and executing instructions
- sends control signals
- can read instructions from memory, flags set by ALU, and step_counter
- **I/O** -- memory-mapped via reserved memory cells, symbolic. Cells are set via configuration.
- **p_counter** -- command counter:
- incremented after each instruction or overwritten by the transition instruction (taking into account the offset).

### Instruction Set

Arguments and their limitations:
- number in the range [-2^64 ; 2^64 - 1]
- offset relative to the current value of `pc_counter` - the amount should not exceed the memory limits
- address in memory - the address must not go out of memory
- register - must be in a register file
- restrictions on the arguments of each individual instruction come out of the programming language (see paragraph 1)

| Syntax                                  | Mnemonic                                | Ticks | Comment                                                                                                                                              |
|:----------------------------------------|:----------------------------------------|-------|:-----------------------------------------------------------------------------------------------------------------------------------------------------|
| `add/sub/mul/div/mod <arg> <arg> <arg>` | ADD/SUB/MUL/div/MOD `<arg> <arg> <arg>` | 3     | number of clock cycles fixed                                                                                                                         |
| `cmp <arg> <arg>`                       | cmp `<arg>`                             | 2     | number of clock cycles fixed                                                                                                                         |
| `mov <arg> <arg>`                       | mov `<arg> <arg>`                       | 3     | number of clock cycles fixed                                                                                                                         |
| `je, jne, jg, jmp <arg>`                | JE, JNE, JG, JMP `<arg> <arg>`          | 2-3   | number of clock cycles depends on ALU flags <br/>work only with relative addressing                                                                  |
| `inc/dec <arg>`                         | INC/DEC `<arg>`                         | 3     | number of clock cycles fixed                                                                                                                         |
| `hlt`                                   | HLT                                     | 0     | causes simulation to stop                                                                                                                            |
| `data <arg>`                            | DATA `<arg>`                            | 0     | data storage instruction - implements memory cells with data                                                                                         |
| `ld <arg> <arg>`                        | LD `<arg> <arg>`                        | 3-4   | Reads from the specified memory location<br/>Supports absolute and relative addressing<br/>The number of clock cycles depends on the addressing mode |
| `st <arg> <arg>`                        | ST `<arg> <arg>`                        | 2-3   | Writes to the specified memory location<br/>Supports absolute and relative addressing<br/>The number of clock cycles depends on the addressing mode  |

### Encoding instructions

- Machine code is serialized to a JSON list.
- One list item, one instruction.
- The instruction has a fixed size - machine word

Example:

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

where:

- `opcode` -- a string with the operation code;
- `position' -- the position of the instruction in memory
- `args' -- instruction arguments:
- `mode' -- argument addressing mode
- `data' -- argument value

Data types in the [isa] module(./src/translation/isa.py ), where:

- `Opcode` -- enumeration of operation codes;
- `AddrMode' -- enumeration of addressment modes:
- `REG` -- the argument is a register. `data' field: register
- `REL` -- the argument reflects relative addressing. Field `data': offset
- `ABS' -- the argument reflects direct addressing. `data' field: address
- `DATA' -- the argument is a value. `data` field: number
- `Operation` -- a structure for describing all the necessary information about the instruction.
- `Argument` -- a structure for describing all the necessary information about an argument


## Translator

Command line interface: `translator.py <input_file> <target_file>"`

Implemented in the module: [translator](src/translation/translator.py )

Translation stages (`translate` function):

1. Preprocessing the source code: removing unnecessary spaces, commas, comments. Implemented in the `preprocessing` function of the [preprocessor] module (src/translation/preprocessor.py )
2. Checking for the presence of the `.start` label
3. Transform `section.text` to machine code (subject to restrictions) - function `parse_text`
4. Conversion of `section .data` to machine code (subject to restrictions) - function `parse_data`
5. Combining the machine codes of two sections and determining the addresses of variables inside commands - the `join_text_and_data` function
6. Setting the start address of the program (taking into account the offset relative to the data and reserved cells) - the `add_start_address` function

Rules for generating machine code:

- one `Operation' (class describing the operation) -- one instruction;
- at the beginning of each program there is a command `jmp`, which points to the starting address
- instead of registers, their names are substituted (instances of enum `Register`)
- instead of addresses in memory, the addresses themselves or the addresses of reserved cells are substituted (if they are used)
- an offset relative to the current address is substituted instead of variables,
- instead of labels, an offset relative to the current address to the memory cells they point to is substituted.
- their ASCII codes are substituted instead of characters
- numbers remain numbers

## Processor model
### DataPath and ControlUnit schema
![DataPath and ControlUnit schema](scheme.png)
### DataPath
Implemented in the `DataPath` class

- `memory` is single-port, so we either read or write.
- `reg_file' -- register management device. Receives input signals with operands and a register for writing.
- - `reg_file.argument_1` -- the register from which data will be fed to the left input of the ALU or to the register file
- - `reg_file.argument_2` -- the register from which data will be fed to the right input of the ALU or to memory
- - `reg_file.out` -- the register into which data will be read when the signal is applied
- `addr_alu` -- An ALU that calculates a relative address.
- - `addr_alu.left' -- data from the left input of the ALU
- - `addr_alu.right' -- data from the right input of the ALU
- `data_alu` -- An ALU that performs arithmetic operations with values from a register file.
- - `data_alu.left' -- data from the left input of the ALU
- - `data_alu.right' -- data from the right input of the ALU
- `pc_counter` -- command counter
- `data_alu_bus` -- the bus that exits from `data_alu` to `reg_file`.
- `addr_alu_bus' -- the bus connecting the output to `addr_alu` and the multiplexer defining the value of `addr_bus'.
- `addr_bus` -- a bus containing an address for accessing (reading or writing) memory. Connects multiplexer and `memory`
- `mem_bus' -- bus connecting `memory` and `reg_file`
- `input_buffer' -- buffer with input data (bound to a memory cell)
- `output_buffer' -- buffer with output data (bound to a memory cell)

Signals:

- `set_regs_args` -- send a RegFile signal with register data
- `latch_register' -- snap the data going to the register file to the register `reg_file.out'. The data source is selected depending on the 'sel_reg` signal.
- `latch_addr_bus' -- put data on the bus that defines the read/write address
- `latch_pc` -- snap data into the command counter
- `set_data_alu_args (const_operand)' -- snap the inputs `data_alu'. When feeding const_operand is placed on the right input (sel_data).
- `set_addr_alu_args (const_operand)' -- snap the 'addr_alu` inputs. When feeding const_operand is placed on the right input (sel_data).
- `execute_data_alu` -- calculate the output value of `data_alu' by sending a signal to it with an operation, attach it to the 'data_alu_bus` bus.
- `execute_addr_alu` -- calculate the output value of `addr_alu` by sending a signal to it with an operation, attach it to the 'addr_alu_bus` bus.
- `read` -- read the value from memory at the address from `addr_bus` and put it on the `mem_bus` bus.
- `write` -- write the value of `reg_file.argument_2` to memory at the address from `addr_bus`.

Flags:

- `_zero_flag' -- reflects the presence of a zero value at the output of the ALU connected to the register file. Used for conditional transitions.
- `_positive_flag` -- reflects the presence of a positive value at the output of the ALU connected to the register file. Used for conditional transitions.


### Control Unit
Implemented in the `Control Unit` class
- Hardwired (implemented entirely in python).
- Simulation at the clock level.
- Translation of instructions into a sequence of signals (taking into account the current clock cycle): `decode_and_execute_instruction`.
- Reading and decoding instructions takes 1 clock cycle
- Contains `step_counter`

Signals:

- `latch_inc_program_counter` -- a signal to increase the command counter by 1 in DataPath.
- `- `latch_step_counter` -- snap the value of the step counter to ControlUnit (depending on `sag_next').

Features of the model:

- The standard logging module is used for the processor status log.
- The number of simulation instructions is limited by a hardcoded constant.
- Simulation is stopped using exceptions:
- `IndexError` -- if there is no data to read from the I/O port;
- `StopIteration' -- if the `HLT` instruction is executed.
- Simulation control is implemented in the `simulate` function.

## Approbation
Several types of tests were implemented (`unittest` was used):
- integration tests: [integration_test](test/integration_test.py )
- translator unit tests: [unit_translator_test](test/unit_translator_test.py )
- unit validation tests: [unit_validation_test](test/unit_validation_test.py )
- CPU unit tests: [unit_machine_test](test/unit_machine_test.py )

All materials used in tests: [test](test)

There are 3 algorithms implemented in integration tests (and partially in translator unit tests):
- [hello_world](resources/source/hello.asm)
- [cat](resources/source/cat.asm)
- [prob5](resources/source/pro b5.asm)

For the rest of the tests, the algorithms were written separately and reflect one of the key areas of the module:
- processor unit tests: [examples_correct](resources/examples_correct)
- validator unit tests: [incorrect](resources/incorrect)

### CI
```yaml
lab3:
  stage: test
  image:
    name: python-tools
    entrypoint: [""]
  script:
    - python3-coverage run -m pytest --verbose
    - find . -type f -name "*.py" | xargs -t python3-coverage report
    - find . -type f -name "*.py" | xargs -t pep8 --ignore=E501
    - find . -type f -name "*.py" | xargs -t pylint --disable=C0301,R0903,R1702,R0912,R0915,R0916,R0902
    - find . -type f -name "*.py" | xargs -t mypy --check-untyped-defs --explicit-package-bases --namespace-packages
```

where:

- `python3-coverage` -- generating a report on the level of coverage of the source code.
- 'pytest' -- utility for running tests.
- `pep8' -- utility for checking the formatting of the code. `E501' (string length) is disabled.
- 'pylint' -- a utility for checking the quality of the code. Some rules are disabled in order to simplify the code.
- `mypy' is a utility for checking the correctness of static typing.
-`--check-untyped-defs' -- additional check.
- `--explicit-package-bases` and `--namespace-packages` -- helps to search for imported modules correctly.
- Docker image `python-tools` includes all the utilities listed. Its configuration is [Dockerfile](./Dockerfile).

### Usage example

Usage example and processor operation log using the example of `cat`:

``` commandline
$ cat resources/input.txt
Do!;,
@1

$ cat resources/source/cat.asm
section .text
.start:
    .read_char:
        LD %r2, #STDIN
        ST #STDOUT, %r2
        JMP .read_char
        
$ py ./translation/translator.py resources/source/cat.asm resources/result/cat.json
source LoC: 6 instr: 4

$ cat resources/result/cat.json
[
    {
        "opcode": "jmp",
        "position": 0,
        "args": [
            {
                "data": 1,
                "mode": "relative"
            }
        ]
    },
    {
        "opcode": "ld",
        "position": 1,
        "args": [
            {
                "data": "r2",
                "mode": "register"
            },
            {
                "data": 0,
                "mode": "absolute"
            }
        ]
    },
    {
        "opcode": "st",
        "position": 2,
        "args": [
            {
                "data": 1,
                "mode": "absolute"
            },
            {
                "data": "r2",
                "mode": "register"
            }
        ]
    },
    {
        "opcode": "jmp",
        "position": 3,
        "args": [
            {
                "data": -2,
                "mode": "relative"
            }
        ]
    }
]

$ py machine.py resources/result/cat.json resources/input.txt
DEBUG:root:TICK: 0, PC: 2, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 0, MEM_BUS: 0, Z: False, P: False, STEP_COUNTER: 0 -
DEBUG:root:TICK: 1, PC: 2, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 0, MEM_BUS: 0, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 2, OPCODE: jmp, ARGS: [('relative', 1)]

DEBUG:root:TICK: 2, PC: 2, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 0, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 2, OPCODE: jmp, ARGS: [('relative', 1)]

DEBUG:root:TICK: 3, PC: 3, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 0, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 2, OPCODE: jmp, ARGS: [('relative', 1)]

DEBUG:root:TICK: 4, PC: 3, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 0, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 5, PC: 3, ADDR_BUS: 0, R1: 0, R2: 0, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 6, PC: 4, ADDR_BUS: 0, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 7, PC: 4, ADDR_BUS: 0, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 8, PC: 5, ADDR_BUS: 1, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 9, PC: 5, ADDR_BUS: 1, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 10, PC: 5, ADDR_BUS: 1, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 11, PC: 3, ADDR_BUS: 1, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 12, PC: 3, ADDR_BUS: 1, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 68, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 13, PC: 3, ADDR_BUS: 0, R1: 0, R2: 68, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 14, PC: 4, ADDR_BUS: 0, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 15, PC: 4, ADDR_BUS: 0, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 16, PC: 5, ADDR_BUS: 1, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 17, PC: 5, ADDR_BUS: 1, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 18, PC: 5, ADDR_BUS: 1, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 19, PC: 3, ADDR_BUS: 1, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 20, PC: 3, ADDR_BUS: 1, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 111, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 21, PC: 3, ADDR_BUS: 0, R1: 0, R2: 111, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 22, PC: 4, ADDR_BUS: 0, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 23, PC: 4, ADDR_BUS: 0, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 24, PC: 5, ADDR_BUS: 1, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 25, PC: 5, ADDR_BUS: 1, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 26, PC: 5, ADDR_BUS: 1, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 27, PC: 3, ADDR_BUS: 1, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 28, PC: 3, ADDR_BUS: 1, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 33, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 29, PC: 3, ADDR_BUS: 0, R1: 0, R2: 33, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 30, PC: 4, ADDR_BUS: 0, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 31, PC: 4, ADDR_BUS: 0, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 32, PC: 5, ADDR_BUS: 1, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 33, PC: 5, ADDR_BUS: 1, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 34, PC: 5, ADDR_BUS: 1, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 35, PC: 3, ADDR_BUS: 1, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 36, PC: 3, ADDR_BUS: 1, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 59, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 37, PC: 3, ADDR_BUS: 0, R1: 0, R2: 59, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 38, PC: 4, ADDR_BUS: 0, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 39, PC: 4, ADDR_BUS: 0, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 40, PC: 5, ADDR_BUS: 1, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 41, PC: 5, ADDR_BUS: 1, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 42, PC: 5, ADDR_BUS: 1, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 43, PC: 3, ADDR_BUS: 1, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 44, PC: 3, ADDR_BUS: 1, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 44, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 45, PC: 3, ADDR_BUS: 0, R1: 0, R2: 44, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 46, PC: 4, ADDR_BUS: 0, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 47, PC: 4, ADDR_BUS: 0, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 48, PC: 5, ADDR_BUS: 1, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 49, PC: 5, ADDR_BUS: 1, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 50, PC: 5, ADDR_BUS: 1, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 51, PC: 3, ADDR_BUS: 1, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 52, PC: 3, ADDR_BUS: 1, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 10, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 53, PC: 3, ADDR_BUS: 0, R1: 0, R2: 10, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 54, PC: 4, ADDR_BUS: 0, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 55, PC: 4, ADDR_BUS: 0, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 56, PC: 5, ADDR_BUS: 1, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 57, PC: 5, ADDR_BUS: 1, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 58, PC: 5, ADDR_BUS: 1, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 59, PC: 3, ADDR_BUS: 1, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 60, PC: 3, ADDR_BUS: 1, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 64, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 61, PC: 3, ADDR_BUS: 0, R1: 0, R2: 64, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 62, PC: 4, ADDR_BUS: 0, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

DEBUG:root:TICK: 63, PC: 4, ADDR_BUS: 0, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 64, PC: 5, ADDR_BUS: 1, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 4, OPCODE: st, ARGS: [('absolute', 1), ('register', <Register.R2: 'r2'>)]

DEBUG:root:TICK: 65, PC: 5, ADDR_BUS: 1, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 66, PC: 5, ADDR_BUS: 1, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 1 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 67, PC: 3, ADDR_BUS: 1, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 2 
CELL_NUMBER: 5, OPCODE: jmp, ARGS: [('relative', -2)]

DEBUG:root:TICK: 68, PC: 3, ADDR_BUS: 1, R1: 0, R2: 49, R3: 0, R4: 0, R5: 0, D_ALU_BUD: 0, A_ALU_BUD: 3, MEM_BUS: 49, Z: False, P: False, STEP_COUNTER: 0 
CELL_NUMBER: 3, OPCODE: ld, ARGS: [('register', <Register.R2: 'r2'>), ('absolute', 0)]

WARNING:root:Input buffer came to the end
Output:
68(D) 111(o) 33(!) 59(;) 44(,) 10(
) 64(@) 49(1) 

instr_counter: 26 ticks: 69
```


| Name / Surname | alg.  | LoC | code byte | code instr. | instr. | tick. | variant               |
|----------------|-------|-----|-----------|-------------|--------|-------|-----------------------|
| Мокров С.А.    | hello | 41  | -         | 38          | 28     | 83    | look at the beginning |
| Мокров С.А.    | cat   | 6   | -         | 4           | 26     | 69    | look at the beginning |
| Мокров С.А.    | prob5 | 39  | -         | 27          | 1475   | 4196  | look at the beginning |