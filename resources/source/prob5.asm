section .text
.start:
    MOV %r4, 20

    MOV %r5, 2
    MOV %r1, %r5
    .find_prime:
        INC %r1
        CMP %r1, %r4
        JG .find_number
        MOV %r3, 2
        .check_mod:
            MOD %r2, %r1, %r3
            JE .find_prime
            INC %r3
            CMP %r1, %r3
            JE .mul_step
            JMP .check_mod
        .mul_step:
            MUL %r5, %r5, %r1
            JMP .find_prime

    .find_number:
        MOV %r1, 0
        .next_number:
            ADD %r1, %r1, %r5
            MOV %r3, 0
        .next_divider:
            INC %r3
            MOD %r2, %r1, %r3
            JNE .next_number

            CMP %r3, %r4
            JE .exit

            JMP .next_divider
    .exit:
        ST #STDOUT, %r1
        HLT
