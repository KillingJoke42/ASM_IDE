from sys import argv

registers = list(['$zero','$at','$v0','$v1',
                  '$a0','$a1','$a2','$a3',
                  '$t0','$t1','$t2','$t3',
                  '$t4','$t5','$t6','$t7',
                  '$s0','$s1','$s2','$s3',
                  '$s4','$s5','$s6','$s7',
                  '$t8','$t9','$k0','$k1',
                  '$gp','$sp','$fp','$ra',
                  ])

classes = ['arith', 'logic', 'shift', 'copy', 'mem', 'control']

reg_used = list()

def main():
	if len(argv) == 1:
		command = input("Enter the command: ")
		cl_pred = input("Enter the class: ")
	else:
		command = argv[1]
		cl_pred = argv[2]
	print(interpreter(command, cl_pred))

def get_reg_data(reg_used):
      flag = True if len(reg_used) == 3 else False
      variable = False
      if len(reg_used) == 1:
            return reg_used[0], reg_used[0], reg_used[0], False
      try:
            int(reg_used[0])
            rt = reg_used[0]
            rs = reg_used[1]
            rd = reg_used[1] if not flag else reg_used[2]
            variable = True
      except ValueError:
            try:
                  int(reg_used[1])
                  rt = reg_used[1]
                  rs = reg_used[0]
                  rd = reg_used[0] if not flag else reg_used[2]
                  variable = True
            except ValueError:
                  if not flag:
                        rt = reg_used[1]
                        rs = rd = reg_used[0]
                        variable = False
                  else:
                        try:
                              int(reg_used[2])
                              rt = reg_used[2]
                              rs = reg_used[0]
                              rd = reg_used[1]
                              variable = True
                        except ValueError:
                              rd = reg_used[2]
                              rt = reg_used[1]
                              rs = reg_used[0]
                              variable = False
      return rd, rs, rt, variable


def interpreter(command, cl_pred):
      cmd_wrd = command.split()
      print(cmd_wrd)
      inst_type = 'j'
      
      for i in cmd_wrd:
            if i in registers or ('$'+i) in registers:
                  if inst_type == 'j' and len(reg_used) == 0:
                        inst_type = 'r'
                  elif inst_type == 'j' and len(reg_used) == 1:
                        inst_type = 'i'
                  reg_used.append(i if '$' in i else ('$'+i))
            elif i[0] == '?':
                  reg_used.append(i[1:])
                  if inst_type == 'r':
                        inst_type = 'i'
            else:
                  try:
                        imm = int(i)
                        reg_used.append(imm)
                        inst_type = 'i'
                  except ValueError:
                        continue
      if len(reg_used) == 0:
            inst_type = 'r'

      final_inst = ""
      if cl_pred == "copy":
            if inst_type == 'r':
                  if 'hi' in cmd_wrd or 'upper' in cmd_wrd or 'remainder' in cmd_wrd:
                        final_inst = "mfhi {}".format(reg_used[0])
                  else:
                        final_inst = "mflo {}".format(reg_used[0])
            else:
                  index2 = 1
                  index1 = 0
                  try:
                        int(reg_used[0])
                        index2 = 0
                        index1 = 1
                  except ValueError:
                        index2 = 1
                        index1 = 0
                  final_inst = "lui {}, {}".format(reg_used[index1], reg_used[index2])

      elif cl_pred == "mem":
            if "word" in cmd_wrd and "load" in cmd_wrd or "access" in cmd_wrd:
                  final_inst = "lw {}, {}({})".format(reg_used[1], reg_used[2] if len(reg_used) == 3 else '0', reg_used[0])
            elif "byte" in cmd_wrd and "load" in cmd_wrd or "access" in cmd_wrd:
                  final_inst = "lb{} {}, {}({})".format('u' if "unsigned" in cmd_wrd else '',reg_used[1], reg_used[2] if len(reg_used) == 3 else '0', reg_used[0])
            elif "word" in cmd_wrd and "save" in cmd_wrd or "store" in cmd_wrd:
                  final_inst = "sw {}, {}({})".format(reg_used[1], reg_used[2] if len(reg_used) == 3 else '0', reg_used[0])
            elif "byte" in cmd_wrd and "save" in cmd_wrd or "store" in cmd_wrd:
                  final_inst = "sb {}, {}({})".format(reg_used[1], reg_used[2] if len(reg_used) == 3 else '0', reg_used[0])

      elif cl_pred == "control":
            if inst_type == 'j':
                  if "procedure" in cmd_wrd or "call" in cmd_wrd:
                        final_inst = "jal {}".format(reg_used[0])
                  else:
                        final_inst = "j {}".format(reg_used[0])
            elif inst_type == 'r':
                  if "syscall" in cmd_wrd or "system" in cmd_wrd:
                        final_inst = "syscall"
                  else:
                        final_inst = "jr {}".format(reg_used[0])
            else:
                  if "zero" in cmd_wrd:
                        final_inst = "bltz {}, {}".format(reg_used[0] if '$' in reg_used[0] else reg_used[1], reg_used[1] if '$' in reg_used[0] else reg_used[0])
                  else:
                        rs = ""
                        rt = ""
                        label = ""
                        for i in reg_used:
                              if '$' in i and len(rs) != 0:
                                    rt = i
                              elif '$' in i and len(rs) == 0:
                                    rs = i
                              else:
                                    label = i
                        final_inst = "{} {}, {}, {}".format("bne" if "not" in cmd_wrd else "beq", rs, rt, label)

      elif cl_pred == "shift":
            rd, rs, rt, variable = get_reg_data(reg_used)
            final_inst = "s{}{}{} {}, {}, {}".format('l' if "left" in cmd_wrd else 'r', 'l' if "logically" in cmd_wrd else 'a', 
                                                      'v' if not variable else '', rd, rs, rt)
      
      elif cl_pred == "logic":
            rd, rs, rt, flag = get_reg_data(reg_used)
            if "or" in cmd_wrd:
                  final_inst = "or{} {}, {}, {}".format('i' if flag else '', rd, rs, rt)
            elif "xor" in cmd_wrd:
                  final_inst = "xor{} {}, {}, {}".format('i' if flag else '', rd, rs, rt)
            elif "nor" in cmd_wrd:
                  final_inst = "nor {}, {}, {}".format(rd, rs, rt)
            else:
                  final_inst = "and{} {}, {}, {}".format('i' if flag else '', rd, rs, rt)

      else:
            rd, rs, rt, flag = get_reg_data(reg_used)
            if "add" in cmd_wrd or "addition" in cmd_wrd or "double" in cmd_wrd or "copy" in cmd_wrd or "update" in cmd_wrd or "increment" in cmd_wrd or "upgrade" in cmd_wrd or "plus" in cmd_wrd:
                  final_inst = "add{}{} {}, {}, {}".format('i' if flag else '', 'u' if "unsigned" in cmd_wrd else '', rd, rs, rt)

            if "subtract" in cmd_wrd or "half" in cmd_wrd or "remove" in cmd_wrd or "decrement" in cmd_wrd or "downgrade" in cmd_wrd or "minus" in cmd_wrd:
                  final_inst = "sub{} {}, {}, {}".format('u' if "unsigned" in cmd_wrd else '', rd, rs, rt)

            if "check" in cmd_wrd or "compare" in cmd_wrd or "set" in cmd_wrd:
                  rd = '$' + cmd_wrd[cmd_wrd.index("set")+1] if '$' not in cmd_wrd[cmd_wrd.index("set")+1] else cmd_wrd[cmd_wrd.index("set")+1]
                  if rd == reg_used[0]:
                        rs = reg_used[1]
                        rt = reg_used[2]
                  elif rd == reg_used[2]:
                        rs = reg_used[0]
                        rt = reg_used[1]
                  final_inst = "slt{} {}, {}, {}".format('i' if flag else '', rd, rs, rt)

            if "multiply" in cmd_wrd or "square" in cmd_wrd:
                  final_inst = "mult{} {}, {}".format('u' if "unsigned" in cmd_wrd else '', rs, rt)
            if "divide" in cmd_wrd:
                  final_inst = "div{} {}, {}".format('u' if "unsigned" in cmd_wrd else '', rs, rt)


      return [reg_used, inst_type, final_inst]

if __name__ == '__main__':
      main()