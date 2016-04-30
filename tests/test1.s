.data
hello: .asciiz "Hello\n"
.text
main: 
	ori t1,zero,5
	ori t2,zero,6
	ori a0,zero,5
	ori v0,zero,1
	add t1,t1,t2
	syscall
