import struct
MIPS_REGS = ('zero', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 
             't2', 't3', 't4', 't5', 't6', 't7', 's0', 's1', 's2', 's3', 
             's4', 's5', 's6', 's7', 't8', 't9', 'k0', 'k1', 'gp', 'sp', 
             'fp', 'ra')

class OpCode():
	TYPE_R = 1
	TYPE_I = 2
	TYPE_J = 3
	TYPE_N = 4
	def __init__(self):
		self.codetype = OpCode.TYPE_N
		self.instruction = "nop"
		self.args = []
		self.opcode = 0b000000
		self.function = 0b000000
	
	def __repr__(self):
		return "%s %s" % (self.instruction, self.args)

class MipsCoder():
	opcodes = []
	@staticmethod
	def initialize(codefile):
		with open(codefile, 'r') as f:
			for line in f:
				code = OpCode()
				tokens = line.split(' ')
				code.codetype = OpCode.TYPE_R if tokens[0] == 'R' else \
				                OpCode.TYPE_I if tokens[0] == 'I' else \
				                OpCode.TYPE_J if tokens[0] == 'J' else None
				code.instruction = tokens[1]
				code.args = [] if tokens[2].lower() == 'none' else tokens[2].split(',')
				rawopcode = int(tokens[3], 2)
				if code.codetype == OpCode.TYPE_R:
					code.opcode = 0b000000
					code.function = rawopcode
				else:
					code.opcode = rawopcode
				MipsCoder.opcodes.append(code)

	@staticmethod
	def decode(instr):
		opcodes = [x for x in MipsCoder.opcodes if x.instruction == instr.cmd]
		if len(opcodes) != 1:
			if instr.cmd == 'nop':
				return 0
			return None
		opcode = opcodes[0]
		if len(opcode.args) != len(instr.args):
			return None
		args = {}
		argvals = dict.fromkeys(['rt', 'rs', 'sa', 'rd'], 0)
		for i in range(len(opcode.args)):
			args[opcode.args[i]] = instr.args[i]
			if opcode.args[i] in ('rt', 'rs', 'sa', 'rd'):
				argvals[opcode.args[i]] = MIPS_REGS.index(instr.args[i])
			if opcode.args[i] in ('imm'):
				try:
					val = int(instr.args[i])
				except:
					return None
				if val < 0: #assume unsigned, convert to signed
					val = 65535 + val
				if val > 65535:
					return None
				argvals[opcode.args[i]] = val

		#encoding
		if opcode.codetype == OpCode.TYPE_I:
			val = 0
			val += argvals['imm']
			val += (argvals['rt'] << 16)
			val += (argvals['rs'] << 21)
			val += (opcode.opcode << 26)
			return val
		elif opcode.codetype == OpCode.TYPE_R:
			val = 0
			val += opcode.function
			val += (argvals['sa'] << 6)
			val += (argvals['rd'] << 11)
			val += (argvals['rt'] << 16)
			val += (argvals['rs'] << 21)
			val += (opcode.opcode << 26)
			return val
		elif opcode.codetype == OpCode.TYPE_J:
			return -1
		elif opcode.codetype == OpCode.TYPE_N:
			return 0
		else:
			return None
