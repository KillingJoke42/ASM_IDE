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

def main():

    codefile = open(sys.argv[1], 'r')
    outfile = open('code.hex', 'wb')
    outfile_str = open('code_str.hex', 'w')

    buffer = list()
    pc = 0
    for line in codefile:
        for i in line:
            if i != '\n':
                buffer.append(i)
        line = "".join(buffer)
        buffer = list()
        print(line)
        pc = symbol_table(line, pc)

    print(table)
    for line in codefile:
        for i in line:
            if i != '\n':
                buffer.append(i)
        line = "".join(buffer)
        buffer = list()
        print(line)
        output = compile(line)
        outfile_str.write(output + '\n')
        #for i in output:
            #outfile.write(chr(ord(i) - 48))
        #outfile.write('\n')
        outfile.write((int(output, base = 2).to_bytes(4, byteorder = 'big')))
        #outfile.write('\n')
    
    outfile.close()
    codefile.close()
if __name__ == "__main__":
    main()