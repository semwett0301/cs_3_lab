section .text
.start:
    XOR %r1, %r1

    LD %r2, #STDIN

    MOV %r1, 2
    MOV %r4, %r1
    .find_prime:
        INC %r1
        CMP %r1, %r2
        JG .find_number
        MOV %r3, 2
        .check_mod:
            CMP %r1, %r3
            JE .find_prime
            INC %r3
            CMP %r1, %r3
            JE .mul_step
            JMP .check_mod
        .mul_step:
            MUL %r4, %r1
            JMP .find_prime

    .find_number:
        XOR %r1, %r1
        .next_number:
            ADD %r1, %r4
            XOR %r3, %r3
        .next_divider:
            INC %r3
            CMP %r1, %r3
            JNE .next_number

            CMP %r3, %r2
            JE .exit

            JMP .next_divider
    .exit:
        ST #STDOUT, %r1
        ST #STDOUT, '\n'
        HLT