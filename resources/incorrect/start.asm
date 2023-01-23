section .text
.end:
    HLT
    MOV %r1, 8
    CMP %r1, 8
    JE .end
    INC %r1
    MOV %r1, %r2