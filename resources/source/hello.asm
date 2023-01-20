section .data
    H: 'h'
    A: 'a'

section .text
.start:
    .print_char:
        LD %r1, (H)
        CMP %r1, 0
        JE .exit ; ndjz vfnm ik.[; ffd
        ST #STDOUT, %r1
        INC %r1
        JMP .print_char
    .exit:
        HLT