	.section	__TEXT,__text,regular,pure_instructions
	.build_version macos, 12, 0	sdk_version 12, 3
	.globl	_main                           ; -- Begin function main
	.p2align	2
_main:                                  ; @main
	.cfi_startproc
; %bb.0:
	sub	sp, sp, #32
	.cfi_def_cfa_offset 32
	mov	x8, #5						// x8 = 5
	str	x8, [sp, #24]				// a = x8 (5)
	mov	x8, #6						// x8 = 6
	str	x8, [sp, #16]				// b = x8 (6)
	ldr	x8, [sp, #24]				// x8 = a
	ldr	x9, [sp, #16]				// x9 = b
	add	x9, x8, x9					// x9 = x8 (a) + x9 (b)
	ldr	x8, [sp, #16]				// x8 = b
	ldr	x10, [sp, #24]				// x10 = a
	ldr	x11, [sp, #16]				// x11 = b
	add	x10, x10, x11				// x10 = x10 (a) + x11 (b)
	add	x10, x10, #3				// x10 = x10 (a + b) + 3
	mul	x8, x8, x10					// x8 = x8 (b) * x10 (a + b + 3)
	add	x8, x8, x9, lsl #1			// x8 = x8 (b * (a + b + 3)) + x9 << 1 ((a + b) * 2)
	str	x8, [sp, #8]				// c = x8 ((a + b) * 2 + b * (a + b + 3))
	mov	w0, #0
	add	sp, sp, #32
	ret
	.cfi_endproc
                                        ; -- End function
.subsections_via_symbols
