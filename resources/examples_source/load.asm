section .data
    SRC: 24

section .text
.start:
    MOV %r1, 2
    LD %r2, (SRC)
    ADD %r1, %r1, %r2
    HLT