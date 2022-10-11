// a: 0
// b: 8
// c: 16

subi sp, sp, #16	// allocate 16 bytes on the stack

addi x10, xzr, #5	// a = 5

subi x11, xzr, #6	// b = -6

add x12, x10, x11	// x12 = ab+
subi x13, xzr, #2	// x13 = -2
mul x13, x13, x12	// x13 = ab+-2*
addi x14, x12, #3	// x14 = ab+3+
mul x15, x11, x14	// x15 = bab+3+*
stur x10, [sp, #0]	// store a
add x10, x13, x15	// c = ab+-2*bab+3+*+

stur x11, [sp, #8]	// store b
addi x11, xzr, #2	// x11 = 2
addi x9, xzr, #3	// x9 = 3
mul x11, x11, x9	// x11 = 23*
add x10, x10, x11	// c = c23*+

stur x10, [sp, #16]	// store c

addi sp, sp, #16	// deallocate 16 bytes from the stack
