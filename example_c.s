
sub	sp, sp, #32
mov	x8, #5
str	x8, [sp, #24]
mov	x8, #-6
str	x8, [sp, #16]
ldr	x8, [sp, #24]
ldr	x9, [sp, #16]
add	x8, x8, x9
mov	x9, #-2
mul	x8, x8, x9
ldr	x9, [sp, #16]
ldr	x10, [sp, #24]
ldr	x11, [sp, #16]
add	x10, x10, x11
add	x10, x10, #3
mul	x9, x9, x10
add	x8, x8, x9
str	x8, [sp, #8]
ldr	x8, [sp, #8]
add	x8, x8, #6
str	x8, [sp, #8]
mov	w0, #0
add	sp, sp, #32