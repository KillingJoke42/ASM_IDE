from CompilerForMachineCode import compile
import os
import sys
import struct

table = dict()

def symbol_table(instruction, program_counter):
    program_counter += 4
    label = list()
    count = 0
    instruction = list(instruction)
    label_enable = False
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
        table[label] = program_counter
    return program_counter

def write(code_file_name, outfile_name):

    codefile = open(code_file_name, 'r')
    outfile = open(outfile_name, 'wb')
    outfile_str = open(outfile_name[:-4] + '_str.hex', 'w')

    buffer = list()
    pc = 0
    for line in codefile:
        for i in line:
            if i != '\n':
                buffer.append(i)
        line = "".join(buffer)
        buffer = list()
        pc = symbol_table(line, pc)

    codefile.close()
    codefile = open(code_file_name, 'r')

    for line in codefile:
        for i in line:
            if i != '\n':
                buffer.append(i)
        line = "".join(buffer)
        buffer = list()
        candidates = list()
        if "beq" in line or "bne" in line or "bltz" in line:
            line = line.split()
            for key in table.keys():
                for item in line:
                        if ':' in item:
                            line[line.index(item)] = item[:-1]
                if key in line:
                    #line[line.index(key)] = str(table[key])
                    candidates.append([key, str(table[key]), line.index(key)])
            print(candidates)
            if len(candidates) == 2:
                correct_candidate = candidates.pop()
                line[correct_candidate[2]] = str(correct_candidate[1])
                false_candidate = candidates.pop()
                line[false_candidate[2]] = str(false_candidate[0] + ':')
            else:
                print("in")
                correct_candidate = candidates.pop()
                line[correct_candidate[2]] = str(correct_candidate[1])
            line = " ".join(line)
        print(line)
        output = compile(line, table)
        outfile_str.write(output + '\n')
        outfile.write((int(output, base = 2).to_bytes(4, byteorder = 'big')))
    
    outfile_str.close()
    outfile.close()
    codefile.close()