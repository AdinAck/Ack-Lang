// a: 0
// b: 8
// c: 16
// ab+: 24

addi x11, xzr, #5	// a = 5

subi x12, xzr, #6	// b = -6

add x13, x11, x12	// ab+ = a + b
subi x14, xzr, #2	// x14 = -2
mul x14, x14, x13	// ab+-2* = ab+ * -2
addi x15, x13, #3	// ab+3+ = ab+ + 3
stur x11, [sp, #0]	// store a
mul x11, x12, x15	// bab+3+* = b * ab+3+
stur x12, [sp, #8]	// store b
add x12, x14, x11	// ab+-2*bab+3+*+ = ab+-2* + bab+3+*

stur x13, [sp, #24]	// store ab+
addi x13, x12, #2	// c2+ = c + 2

stur x12, [sp, #16]	// store c
