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
	TYPE_V = 4
	def __init__(self):
		self.codetype = OpCode.TYPE_N
		self.instruction = "nop"
		self.args = []
		self.opcode = 0b000000
		self.function = 0b000000
		self.virtual = False
	
	def __repr__(self):
		return "%s %s" % (self.instruction, self.args)

class MipsCoder():
	opcodes = []
	instrlist = []
	@staticmethod
	def initialize(codefile):
		with open(codefile, 'r') as f:
			for line in f:
				code = OpCode()
				tokens = line.split(' ')
				code.codetype = OpCode.TYPE_R if tokens[0] == 'R' else \
				                OpCode.TYPE_I if tokens[0] == 'I' else \
				                OpCode.TYPE_V if tokens[0] == 'V' else \
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
				MipsCoder.instrlist.append(code.instruction)

	@staticmethod
	def instructions():
		return MipsCoder.instrlist

	@staticmethod
	def regs():
		return MIPS_REGS

	@staticmethod
	def validate(instr):
		return True if MipsCoder.decode(instr) != None else False

	@staticmethod
	def devirtualize(instr):
		from mipsmachine import Instruction, MipsException
		if instr.cmd == "li":
			if len(instr.args) != 2:
				raise MipsException("Invalid virtual instruction")
			reg = instr.args[0]
			imm = int(instr.args[1])
			if imm > 65535:
				instra = Instruction('lui %s,%d' % (reg, (imm & 0xFFFF0000) >> 16), instr.label)
				instrb = Instruction('ori %s,%s,%d' % (reg, reg, imm & 0x0000FFFF))
				print instra, instrb
				return [instra, instrb]
			else:
				return [Instruction('ori %s,%s,%d' % (reg, reg, imm), instr.label)]
		elif instr.cmd == "move":
			if len(instr.args) != 2:
				raise MipsException("Invalid virtual instruction")
			return [Instruction('add %s,%s,zero' % (instr.args[0], instr.args[1]))]
		return [instr]

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
				if instr.args[i] not in MIPS_REGS:
					return None
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
		elif opcode.codetype == OpCode.TYPE_V:
			return None
		elif opcode.codetype == OpCode.TYPE_N:
			return 0
		else:
			return None

	@staticmethod
	def encode(data):
		opcode = data >> 26
		print bin(data)
		print bin(opcode)

