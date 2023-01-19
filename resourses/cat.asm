section .text
.start:
    .read_char:
        LD %r2, #STDIN
        CMP %r2, '0x0'
        JE .exit
        ST #STDOUT, %r2
        JMP .read_char
    .exit:
        HLT
