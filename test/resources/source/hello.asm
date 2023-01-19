section .data
    H: 'h'
    A: 'a'

section .text
.start:
    .print_char:
        LD %r1, (HELLO)
        CMP %r1,'0x0'
        JE .exit
        ST #STDOUT, %r1
        INC %r1
        JMP .print_char
    .exit:
        HLT