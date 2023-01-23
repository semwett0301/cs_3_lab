section .data
RES: 0

section .text
.start:
    MOV %r1, 2
    ST #STDOUT, %r1
    ST (RES), %r1
    HLT