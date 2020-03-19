def compile(instruction, symbol_table):
    commands = dict({
                    'mfhi':['r',0,16],
                    'mflo':['r',0,18],
                    'lui':['i',15],
                    'add':['r',0,32],
                    'addu':['r',0,33],
                    'sub':['r',0,34],
                    'subu':['r',0,35],
                    'slt':['r',0,42],
                    'mult':['r',0,24],
                    'multu':['r',0,25],
                    'div':['r',0,26],
                    'divu':['r',0,27],
                    'addi':['i',8],
                    'addiu':['i',9],
                    'slti':['i',10],
                    'sll':['r',0,0],
                    'srl':['r',0,2],
                    'sra':['r',0,3],
                    'sllv':['r',0,4],
                    'srlv':['r',0,6],
                    'srav':['r',0,7],
                    'and':['r',0,36],
                    'or':['r',0,37],
                    'xor':['r',0,38],
                    'nor':['r',0,39],
                    'andi':['i',12],
                    'ori':['i',13],
                    'xori':['i',14],
                    'lw':['i',35],
                    'lb':['i',32],
                    'lbu':['i',36],
                    'sw':['i',43],
                    'sb':['i',40],
                    'j':['j',2],
                    'jal':['j',3],
                    'jr':['r',0,8],
                    'bltz':['i',1],
                    'beq':['i',4],
                    'bne':['i',5],
                    'syscall':['r',0,12]
                    })

    registers = list([
                        '$zero',
                        '$at',
                        '$v0',
                        '$v1',
                        '$a0',
                        '$a1',
                        '$a2',
                        '$a3',
                        '$t0',
                        '$t1',
                        '$t2',
                        '$t3',
                        '$t4',
                        '$t5',
                        '$t6',
                        '$t7',
                        '$s0',
                        '$s1',
                        '$s2',
                        '$s3',
                        '$s4',
                        '$s5',
                        '$s6',
                        '$s7',
                        '$t8',
                        '$t9',
                        '$k0',
                        '$k1',
                        '$gp',
                        '$sp',
                        '$fp',
                        '$ra',
                        ''
                    ])

    chars_in_reg = ['$', 'a', 't', 'v', 's', 'k', 'g', 'p', 'r']
    nums_in_reg = list(range(10))
    
    for i in nums_in_reg:
        chars_in_reg.append(str(i))

    instruction = instruction.split()
    buffer = list()
    flag = 0
    register_index = None
    label = list()
    label_enable = False
    count = 0

    for i in instruction:
        if ':' in i:
            label_enable = True   
    if label_enable == True:
        instruction_temp = "".join(instruction)
        for i in instruction_temp:
            if i != ':':
                label.append(i)
                instruction_temp = instruction_temp.replace(i,'')
            else:
                break
        for i in instruction:
            count += 1
            if instruction[0] == '':
                instruction = instruction[1:]       
            for j in i:
                instruction[count - 1] = instruction[count - 1].replace(j,'')
                if j == ':':
                    label_enable = False
                    if i == ':':
                        instruction = instruction[1:]
                    break
            if label_enable == False:
                if ':' in instruction[0]:
                    instruction[0] = instruction[0].replace(':','')
                break
        label = "".join(label)

    for i in instruction:
        for j in i:
            if j != '$':
                buffer.append(j)
            else:
                register_index = instruction.index(i)
                flag = 1
                break
        if flag == 1:
           break
    inst_ext_op = "".join(buffer)
    inst_ext_op = inst_ext_op.lower()
    inst_ext_op = "".join(inst_ext_op)
    if inst_ext_op.find('jal') != -1:
        instructionjump = inst_ext_op[3:]
        inst_ext_op = 'jal'
    elif inst_ext_op.find('jr') == -1:
        if inst_ext_op.find('j') != -1:
            instructionjump = inst_ext_op[1:]
            inst_ext_op = 'j'
    inst_data = commands[inst_ext_op]
    inst_type = inst_data[0]
    if inst_type == 'r':
        opcode = inst_data[1]
        fn = inst_data[2]
    elif inst_type == 'i':
        opcode = inst_data[1]
    elif inst_type == 'j':
        opcode = inst_data[1]
    else:
        print('Error: Unhandled Exception at instruction decode.....')
    buffer = list()
    if register_index != None:
        instruction = instruction[register_index:]
    else:
        instruction = '$zero,$zero,$zero'
    if inst_type == 'r' and fn not in range(4):
        reg1 = list()
        flag1 = 0
        reg2 = list()
        flag2 = 0
        reg3 = list()
        flag3 = 0
        rs = list()
        rt = list()
        rd = list()
        for i in instruction:
            for j in i:
                if j in chars_in_reg:
                    if len(reg1) < 3:
                        flag1 = 1
                        flag2 = 0
                        flag3 = 0
                        reg1.append(j)
                    elif len(reg1) == 3 and j == 'r':
                        reg1.append(j)
                    elif len(reg2) < 3:
                        flag1 = 0
                        flag2 = 1
                        flag3 = 0
                        reg2.append(j)
                    elif len(reg2) == 3 and j == 'r':
                        reg2.append(j)
                    elif len(reg3) < 3:
                        flag1 = 0
                        flag2 = 0
                        flag3 = 1
                        reg3.append(j)
                    elif len(reg3) == 3 and j == 'r':
                        reg3.append(j)
                else:
                    if j == 'z' or j == 'e' or j == 'r' or j == 'o':
                        if flag1 == 1:
                            reg1.append(j)
                        elif flag2 == 1:
                            reg2.append(j)
                        elif flag3 == 1:
                            reg3.append(j)
        reg1 = "".join(reg1)
        reg2 = "".join(reg2)
        reg3 = "".join(reg3)

        if reg1 not in registers or reg2 not in registers or reg3 not in registers:
            print('Invalid Registers Entered. Please try again.')
        else:
            rtype_class1 = ['mfhi','mflo']
            rtype_class2 = ['mult','multu','div','divu']
            rtype_class3 = ['jr','syscall']
            rtype_class4 = ['sllv','srlv','srav']
            if inst_ext_op in rtype_class1:
                rd = registers.index(reg1)
                rd = 0 if rd == 32 else rd
                rs = registers.index(reg2)
                rs = 0 if rs == 32 else rs
                rt = registers.index(reg3)
                rt = 0 if rt == 32 else rt
            elif inst_ext_op in rtype_class2:
                rd = 0
                
                rs = registers.index(reg1)
                rs = 0 if rs == 32 else rs
                rt = registers.index(reg2)
                rt = 0 if rt == 32 else rt
            elif inst_ext_op in rtype_class3:
                if inst_ext_op == 'jr':
                    rd = 0
                    rt = 0
                    rs = registers.index(reg1)
                    rs = 0 if rs == 32 else rs
                else:
                    rs = registers.index(reg1)
                    rs = 0 if rs == 32 else rs
                    rt = registers.index(reg2)
                    rt = 0 if rt == 32 else rt
                    rd = registers.index(reg3)
                    rd = 0 if rd == 32 else rd
            elif inst_ext_op in rtype_class4:
                rd = 0 if registers.index(reg1) == 32 else registers.index(reg1)
                rt = 0 if registers.index(reg2) == 32 else registers.index(reg2)
                rs = 0 if registers.index(reg3) == 32 else registers.index(reg3)
            else: 
                rs = registers.index(reg1)
                rt = registers.index(reg2)
                rd = registers.index(reg3)

    elif inst_type == 'i' or (inst_type == 'r' and fn in range(4)):
        itype_class1 = ['lui','bltz']
        itype_class2 = ['addi','addiu','slti','andi','ori','xori','bne','beq']
        itype_class3 = ['lw','lb','lbu','sw','sb']
        pseudo_itype = ['sll','srl','sra']
        rs = list()
        rt = list()
        imm = list()
        sh = list()
        if inst_ext_op in itype_class1:
            for i in instruction:
                for j in i:
                    if j in chars_in_reg:
                        if inst_ext_op == 'lui':
                            if len(rt) < 3:
                                rt.append(j)
                            else:
                                if j.isnumeric():
                                    imm.append(j)
                        else:
                            if len(rs) < 3:
                                rs.append(j)
                            else:
                                imm.append(j)
           
        elif (inst_ext_op in itype_class2) or (inst_ext_op in pseudo_itype):
            flag1 = 0
            flag2 = 0
            for i in instruction:
                for j in i:
                    if j in chars_in_reg:
                        if len(rs) < 3:
                            flag1 = 1
                            flag2 = 0
                            rs.append(j)
                        elif len(rs) == 3 and j == 'r' and flag1 == 1:
                            rs.append(j)
                        elif len(rt) < 3:
                            flag1 = 0
                            flag2 = 1
                            rt.append(j)
                        elif len(rt) == 3 and j == 'r' and flag2 == 1:
                            rt.append(j)
                        else:
                            if j.isnumeric():
                                imm.append(j)
                    else:
                        if j == 'z' or j == 'e' or j == 'r' or j == 'o':
                            if flag1 == 1:
                                rs.append(j)
                            elif flag2 == 1:
                                rt.append(j)

        elif inst_ext_op in itype_class3:
            flag1 = 0
            flag2 = 0
            for i in instruction:
                for j in i:
                    if j in chars_in_reg and flag2 == 0:
                        if len(rt) < 3:
                            flag1 = 1
                            flag2 = 0
                            rt.append(j)
                        elif len(rt) == 3 and j == 'r':
                            rt.append(j)
                        else:
                            if j.isnumeric():
                                imm.append(j)
                    elif j == '(':
                        flag2 = 1
                        flag1 = 0
                    elif flag2 == 1 and j in chars_in_reg:
                        if len(rs) < 3:
                            rs.append(j)
                        elif len(rs) == 3 and j == 'r':
                            rs.append(j)
                    else:
                        if j == 'z' or j == 'e' or j == 'r' or j == 'o':
                            if flag1 == 1:
                                rt.append(j)
                            elif flag2 == 1:
                                rs.append(j)
        rs = "".join(rs)
        rt = "".join(rt)
        imm = "".join(imm)
        if rs not in registers or rt not in registers:
            print('Invalid Registers Entered. Please try again.')
        elif inst_ext_op in pseudo_itype:
            rd = registers.index(rt)
            rt = registers.index(rs)
            sh = imm
        else:
            rs = registers.index(rs)
            rt = registers.index(rt)

    elif inst_type == 'j':
        jumpaddr = list()
        for i in instructionjump:
            if i.isalnum() == True:
                jumpaddr.append(i)
            else:
                print('Invalid Jump Address....')
        jumpaddr = "".join(jumpaddr)
        try:
            jumpaddr = int(jumpaddr)
        except ValueError:
            print('Accepting jumpaddr as label')
            print('Label: '+jumpaddr)
    machine = list()
    if inst_type == 'r' and fn in range(4):
        opcode = "{0:06b}".format(opcode)
        fn = "{0:06b}".format(fn)
        rs = "{0:05b}".format(0)
        rt = "{0:05b}".format(rt)
        rd = "{0:05b}".format(rd)
        sh = "{0:05b}".format(int(sh) if int(sh) < 32 and int(sh) > 0 else 0)
        machine = [opcode, rs, rt, rd, sh, fn]
    elif inst_type == 'r':
        opcode = "{0:06b}".format(opcode)
        fn = "{0:06b}".format(fn)
        rs = "{0:05b}".format(rs)
        rt = "{0:05b}".format(rt)
        rd = "{0:05b}".format(rd)
        sh = "{0:05b}".format(0)
        machine = [opcode, rs, rt, rd, sh, fn]
    elif inst_type == 'i':
        opcode = "{0:06b}".format(opcode)
        rs = "{0:05b}".format(rs)
        rt = "{0:05b}".format(rt)
        imm = "{0:016b}".format(int(imm))
        machine = [opcode, rs, rt, imm]
    elif inst_type == 'j':
        opcode = "{0:06b}".format(opcode)
        try:
            jumpaddr = symbol_table[jumpaddr]
        except KeyError:
            print("Label Not Found")
        jumpaddr = "{0:026b}".format(jumpaddr)
        machine = [opcode, jumpaddr]
    machine = "".join(machine)
    return machine