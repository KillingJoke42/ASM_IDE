import asmCall
from sys import argv
from CompilerForMachineCode import commands

def mfhi(rs, rt, rd, sh, hi):
	if hi != None:
		return hi
	else:
		print("Error: No data in hi register")
		return False

def mflo(rs, rt, rd, sh, lo):
	if lo != None:
		return lo
	else:
		print("Error: No data in lo register")
		return False

def lui(rs, rt, imm, jump_enabled, pc):
	try:
		return imm << 16
	except:
		print("Invalid Immediate Value Entered")
		return False

def add(rs, rt, rd, sh):
	print(rs, rt, rs + rt)
	return (rs + rt)

def sub(rs, rt, rd, sh):
	return rs - rt

def slt(rs, rt, rd, sh):
	return 1 if rs < rt else 0

def mult(rs, rt, rd, sh):
	multiply = rs * rt
	str_multiply = "{0:032b}".format(multiply)
	hi = int(str_multiply[:16], base=2)
	lo = int(str_multiply[-16:], base=2)
	return hi, lo

def div(rs, rt, rd, sh):
	divide = rs // rt
	remainder = rs % rt
	str_divide = "{0:032b}".format(divide)
	str_rem = "{0:032b}".format(remainder)
	hi = int(str_rem, base=2)
	lo = int(str_divide, base=2)
	return hi, lo

def addi(rs, rt, imm, jump_enabled, pc):
	return (0 if rs == None else rs) + imm

def slti(rs, rt, imm, jump_enabled, pc):
	return 1 if rs < imm else 0

def sll(rs, rt, rd, sh):
	return rt << sh

def srl(rs, rt, rd, sh):
	return rt >> sh

def sllv(rs, rt, rd, sh):
	return rt << rs

def srlv(rs, rt, rd, sh):
	return rt >> rs

def and_(rs, rt, rd, sh):
	return rs & rt

def or_(rs, rt, rd, sh):
	return rs | rt

def xor(rs, rt, rd, sh):
	return rs ^ rt

def nor(rs, rt, rd, sh):
	return ~(rs | rt)

def andi(rs, rt, imm, jump_enabled, pc):
	return rs & imm

def ori(rs, rt, imm, jump_enabled, pc):
	return rs | imm

def xori(rs, rt, imm, jump_enabled, pc):
	return rs ^ imm

def j(jumpaddr,pc):
	pc = jumpaddr // 4
	return pc - 1

def bltz(rs, rt, imm, jump_enabled, pc):
	pc = ((imm // 4) - 1) if rs < 0 else (pc+1)
	return pc

def beq(rs, rt, imm, jump_enabled, pc):
	pc = ((imm // 4) - 1) if rs == rt else (pc+1)
	return pc

def bne(rs, rt, imm, jump_enabled, pc):
	pc = ((imm // 4) - 1) if rs != rt else (pc+1)
	return pc

def syscall(rs, rt, rd, sh):
	print("syscall")
	return "reset"

def code_get(codefile_name):
	codefile = open(codefile_name, 'r')
	if not codefile:
		return
	buffer = list()
	pc = 0
	for line in codefile:
	    for i in line:
	        if i != '\n':
	            buffer.append(i)
	    line = "".join(buffer)
	    buffer = list()
	    pc = asmCall.symbol_table(line, pc)

	codefile.close()
	return asmCall.table

def simulate(instruction):
	inst = None
	rs = rt = rd = sh = imm = jumpaddr = 0
	jump_enabled = False
	opcode = int(instruction[:6], base=2)
	for key in commands.keys():
		if '\n' in instruction:
			function = int(instruction[-7:-1], base=2) if opcode == 0 else None
		else:
			function = int(instruction[-6:], base=2) if opcode == 0 else None
		if function != None:
			if len(commands[key]) == 3 and commands[key][2] == function:
				inst_type = 'r'
				rs = int(instruction[6:11], base=2)
				rt = int(instruction[11:16], base=2)
				rd = int(instruction[16:21], base=2)
				sh = int(instruction[21:26], base=2)
				inst = key
		else:
			if commands[key][1] == opcode:
				inst = key
				inst_type = commands[key][0]
				if inst_type == 'i':
					rs = int(instruction[6:11], base=2)
					rt = int(instruction[11:16], base=2)
					imm = int(instruction[-16:], base=2)
					if opcode in [1,4,5]:
						jump_enabled = True
				else:
					jumpaddr = int(instruction[-26:], base=2)
					jump_enabled = True
	if inst_type == 'r':
		return inst, rs, rt, rd, sh
		#globals()[inst](rs, rt, rd, sh)
		#pc += 1
	elif inst_type == 'i':
		return inst, rs, rt, imm
		#pc = globals()[inst](rs, rt, imm, jump_enabled, pc)
	elif inst_type == 'j':
		return inst, jumpaddr
		#pc = globals()[inst](jumpaddr, pc)