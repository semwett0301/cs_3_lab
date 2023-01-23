section .text
.start:
    MOV %r1, 6
    MOV %r2, 2
    DIV %r3, %r1, %r2
    HLT