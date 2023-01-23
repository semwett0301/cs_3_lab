section .data
    S21RC: '2
    dfsa: :256

section .text
.start:
    MOV %r1, 2
    LD %r2, (S21RC)
    ADD %r1, %r1, %r2
    HLT