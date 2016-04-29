.data
hello: .asciiz "Hello\n"
.text
main: 
	li t1,5
	li t2,6
	li a0,5
	li v0,1
	add t1,t1,t2
	syscall
