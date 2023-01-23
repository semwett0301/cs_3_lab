section .text
.end:
    HLT
.start:
    MOV %r1, 8
    CMP %r1, 8
    JE .end
    INC %r1
    MOV %r1, %r2


