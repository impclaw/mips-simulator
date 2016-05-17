#!/usr/bin/env python
import sys, os, collections
from mipscoder import MipsCoder

MODE_DATA = 1
MODE_TEXT = 2
MIPS_R = 1
MIPS_I = 2
MIPS_J = 3
MIPS_ILIST = ["addi", "slti", "andi", "ori", "xori", "sll", "srl", "lui", "la"]
MIPS_AL = {'add' : '+', 'addi' : '+', 'sub' : '-', 'subi' : '-', 
           'and' : '&', 'andi' : '&', 'or'  : '|', 'ori'  : '|',    
           'xor': '^', 'xori': '^', 'rem': '%', 'sll': '<<', 'srl': '>>', 
		   'sllv': '<<', 'slrv': '>>'} 
MIPS_SAL = {'abs': 'abs', 'not': '~', 'neg': '-'}
MIPS_COND = {'seq': '==', 'sge': '>=', 'sgt': '>', 'sle': '<=', 'slt': '<'}
MIPS_REGS = ('zero', 'at', 'v0', 'v1', 'a0', 'a1', 'a2', 'a3', 't0', 't1', 
             't2', 't3', 't4', 't5', 't6', 't7', 's0', 's1', 's2', 's3', 
             's4', 's5', 's6', 's7', 't8', 't9', 'k0', 'k1', 'gp', 'sp', 
             'fp', 'ra')

class MipsException(Exception):
	def __init__(self, message, lineno = None):
		super(Exception, self).__init__(message)
		self.lineno = lineno

#Every line of code except empty is an instruction
class Instruction:
	def __init__(self, code, label = None):
		if code.strip() == "" or code == None:
			self.text = "nop"
		else:
			self.text = code
		self.label = label
		self.raw = self.text.split(' ', 1)
		self.cmd = self.raw[0].lower()
		if len(self.raw) > 1:
			self.args = [x.strip().lower() for x in self.raw[1].split(',')]
		else:
			self.args = []

		if self.cmd in MIPS_ILIST: 
			self.fmt = MIPS_I
		elif self.cmd == "j": 
			self.fmt = MIPS_J
		else: 
			self.fmt = MIPS_R

			
			#self.cmd, self.args = self.text.split(' ', 1)
			#self.args = [x.strip() for x in self.args.split(',')]

	def getopcode(self):
		return self.text

	def getarg(self, n):
		return self.args[n]

	def intarg(self, n):
		if len(self.args) > n:
			return int(self.args[n])
		else:
			return None

	def regarg(self, n):
		if len(self.args) > n:
			return self.args[n].replace("$", '')
		else:
			return None
	
	def argcount(self):
		return len(self.args)

	def __repr__(self):
		return '"%s (%s)"' % (self.text, "I" if self.fmt == MIPS_I else "J" if self.fmt == MIPS_J else "R")

	@staticmethod
	def fromstring(mipstext):
		instrlst = []
		mode = 0
		curline = 0x0000
		lastlabel = None
		for line in mipstext.strip().split('\n'):
			if '#' in line:
				line = line.split("#", 1)[0]
			line = line.strip()
			if len(line) == 0:
				continue
			curline += 1
			if line.startswith('.data'):
				mode = MODE_DATA
				continue
			elif line.startswith('.text'):
				mode = MODE_TEXT
				continue
			if mode == 0:
				raise MipsException("Text outside .data or .text block", curline)
			else:
				if ':' in line:
					label, line = line.split(':', 1)
					lastlabel = label
					if line == "":
						continue
				if mode == MODE_DATA:
					tokens = [x.strip() for x in line.strip().split(' ', 1)]
					if len(tokens) < 2:
						raise MipsException("Invalid data declaration", curline)
					if tokens[0] == ".asciiz":
						rawdata = [ord(x) for x in list(tokens[1])]
						data = [0]*(len(rawdata)/4)
						for x in range(0, len(data), 4):
							data[x/4] = (rawdata[x] << 24) + (rawdata[x+1] << 16) \
							            + (rawdata[x+2] << 8) + rawdata[x+3]
					if tokens[0] == ".word":
						data = int(tokens[1])
						print MipsCoder.encode(data)
				if mode == MODE_TEXT:
					phylst = MipsCoder.devirtualize(Instruction(line, lastlabel))
					for i in phylst:
						if not MipsCoder.validate(i):
							raise MipsException("Invalid instruction or argument", curline)
					instrlst += phylst
					lastlabel = None
		return instrlst
		
	@staticmethod
	def fromfile(filename):
		with open(filename, 'r') as f:
			return Instruction.formstring(f.read())

class MipsMachine:
	def __init__(self):
		self.nopinstr = Instruction("nop")
		self.maxinstr = 0x1ffc
		self.rawiset = []
		self.reset()

	def reset(self):
		self.memory = collections.OrderedDict([x*4, self.nopinstr] for x in range(self.maxinstr/4))
		self.regsrc1 = self.regsrc2 = self.regdst = None
		self.imm = self.regbase = self.regaux = None
		self.result = None
		self.jumps = {}
		self.breakpoints = []
		self.output = ""
		curline = 0x1000
		for i in self.rawiset:
			self.memory[curline] = i
			if i.label != None:
				self.jumps[i.label] = curline
			curline += 4
		self.regs = {}
		self.regs["pc"] = 0x1000

	def load(self, instr):
		self.rawiset = instr
		self.reset()

	def allregs(self):
		return MIPS_REGS

	def memoryrange(self, start=0, end=0):
		result = collections.OrderedDict([x*4, 0] for x in range(start, end))
		return result

	def memoryat(self, pos):
		return self.memory[pos]

	def step(self):
		self.ifstage()
		if self.instruction.cmd == "syscall":
			self.syscall()
			return
		if self.instruction.cmd == "nop":
			return
		self.idstage()
		self.exstage()
		self.memstage()
		self.wbstage()

	def ifstage(self):
		self.instruction = self.memory[self.regs["pc"]]
		self.regs["pc"] += 4

	def idstage(self):
		i = self.instruction
		if i.fmt == MIPS_R:
			self.regsrc1 = self.reg(i.regarg(1))
			self.regsrc2 = self.reg(i.regarg(2))
			self.regdst = i.regarg(0)
		elif i.fmt == MIPS_I:
			if i.cmd == "lui":
				self.regbase = i.regarg(0)
				self.imm = i.intarg(1)
			else:
				self.regbase = i.regarg(0)
				self.regaux = self.reg(i.regarg(1))
				self.imm = i.intarg(2)
		elif i.fmt == MIPS_J:
			self.imm = i.intarg(0)

	def exstage(self):
		i = self.instruction
		if i.cmd == "nop":
			pass
		elif i.cmd == "lui":
			self.result = (self.imm << 16 & 0xFFFF0000) + (self.reg(self.regbase) & 0x0000FFFF)
		elif i.cmd == "slti": #single case so no generic matching
			self.result = 1 if self.regaux < self.imm else 0
		elif i.cmd == "div": #div has variable arguments
			if i.argcount() == 2:
				self.reg("lo", self.regsrc1 / self.regsrc2)
				self.reg("hi", self.regsrc1 % self.regsrc2)
				self.result = None
			if i.argcount() == 3:
				self.result = self.regsrc1 / self.regsrc2
		elif i.fmt == MIPS_R and i.cmd in MIPS_COND.keys():
			self.result = 1 if eval(str(self.regsrc1) + ' ' + MIPS_COND[i.cmd] + ' ' + str(self.regsrc2)) else 0
		elif i.fmt == MIPS_R and i.cmd in MIPS_SAL.keys():
			self.result = eval(MIPS_SAL[i.cmd]+'('+str(self.regsrc1)+')')
		elif i.fmt == MIPS_R and i.cmd in MIPS_AL.keys():
			self.result = eval(str(self.regsrc1) + ' ' + MIPS_AL[i.cmd] + ' ' + str(self.regsrc2))
		elif i.fmt == MIPS_I and i.cmd in MIPS_AL.keys():
			#print i.cmd, str(self.regaux) + ' ' + MIPS_AL[i.cmd] + ' ' + str(self.imm)
			self.result = eval(str(self.regaux) + ' ' + MIPS_AL[i.cmd] + ' ' + str(self.imm))

	def memstage(self):
		pass

	def wbstage(self):
		i = self.instruction
		if self.result != None:
			if i.fmt == MIPS_I:
				self.reg(self.regbase, self.result)
			elif i.fmt == MIPS_R:
				self.reg(self.regdst, self.result)

	def reg(self, name, value = None):
		if value == None:
			if name in self.regs:
				return self.regs[name]
			else:
				return 0
		else:
			self.regs[name] = value

	def mem(self, pos, value = None):
		if value == None:
			if pos in self.memory:
				return self.memory[pos]
			else:
				return self.nopinstr
		else:
			pass
			#self.regs[name] = value
	
	def syscall(self):
		v0 = self.regs["v0"]
		if v0 == 1:
			self.output += "%d" % (self.reg("a0"))
		if v0 == 10:
			exit("Exiting")

	def printregs(self):
		for k in self.regs:
			print k, " =", self.regs[k], " (%s)" % bin(self.regs[k])


#filename = sys.argv[1]
#instr = Instruction.fromfile(filename)
#mips = MipsMachine(instr)
#for r in range(0, 9):
#	mips.step()
#	mips.printregs()
