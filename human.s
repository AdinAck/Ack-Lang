// super optimized

addi x0, xzr, #5        // long $a = 0; $a+= 5
subi x1, x0, #3         // long $b = $a; $b -= 3

// store temp vars into memory
stur x0, [sp]           // long a = $a
stur x1, [sp, #8]       // long b = $b

// reasonably optimized

addi x0, xzr, #0        // long $a = 0
addi x0, x0, #5         // $a += 5

mov x1, x0              // long $b = a
subi x1, x1, #3         // $b -= 3

// store temp vars into memory
stur x0, [sp]           // long a = $a
stur x1, [sp, #8]       // long b = $b
