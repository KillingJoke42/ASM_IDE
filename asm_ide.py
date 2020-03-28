from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QComboBox, QPlainTextEdit, QLineEdit
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QFileDialog, QTableWidget, QTableWidgetItem
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from styles import dark_fusion, default
import classify
import interpreter1 as interpreter
import asmCall
from Speech_recog import Speech
import simulator
from CompilerForMachineCode import registers

register_file = dict()

for register in registers:
	register_file[register] = 0 if register == "$zero" else None

special = dict({'hi':None, 'lo':None})

pc = None

class SyntaxHighlighter(QtGui.QSyntaxHighlighter):
    def __init__(self, parent):
        super(SyntaxHighlighter, self).__init__(parent)
        self._highlight_lines = dict()
        self.fmt = QtGui.QTextCharFormat()
        self.fmt.setForeground(QtGui.QColor("red"))
        self.fmt.setBackground(QtGui.QColor("yellow"))

    def highlight_line(self, line):
        if isinstance(line, int) and line >= 0 and isinstance(self.fmt, QtGui.QTextCharFormat):
            self._highlight_lines[line] = self.fmt
            tb = self.document().findBlockByLineNumber(line)
            self.rehighlightBlock(tb)

    def clear_highlight(self):
        self._highlight_lines = dict()
        self.rehighlight()

    def highlightBlock(self, text):
        line = self.currentBlock().blockNumber()
        fmt = self._highlight_lines.get(line)
        if fmt is not None:
            self.setFormat(0, len(text), fmt)

# define defult main window
class app_home(QApplication):
	def __init__(self, arg):
		super().__init__(arg)

	def change_theme(self, dark):
		dark_fusion(self) if dark else default(self)
		icon = QtGui.QIcon('icon.png' if not dark else 'icon_white.png')
		cmd_speech.setIcon(icon)

# define main window size
class main_window(QWidget):
	def __init__(self):
		super().__init__()
		self.setMinimumSize(640, 400)
		self.setWindowTitle("ASM_IDE: Making Assembly Language Easier")

	def change_size(self, size):
		if size == "Tiny":
			self.resize(640, 400)
		elif size == "Small":
			self.resize(800, 600)
		elif size == "Large":
			self.resize(1920, 1080)
		elif size == "Medium":
			self.resize(1280, 768)

# define main window theme and size options
class theme_select(QComboBox):
	def __init__(self, mode):
		super().__init__()
		if mode == "theme":
			self.addItems(["Dark", "Light"])
			self.currentIndexChanged.connect(self.themeChanged)
			self.setCurrentIndex(0)
			self.themeChanged()
		else:
			self.addItems(["Tiny", "Small", "Medium", "Large"])
			self.currentIndexChanged.connect(self.sizeChanged)
			self.setCurrentIndex(0)

	def themeChanged(self):
		if self.currentIndex() == 0:
			app.change_theme(True)
		else:
			app.change_theme(False)

	def sizeChanged(self):
		if self.currentIndex() == 0:
			window.change_size("Tiny")
		elif self.currentIndex() == 1:
			window.change_size("Small")
		elif self.currentIndex() == 2:
			window.change_size("Medium")
		else:
			window.change_size("Large")

# display MIPS Instruction and hexcode and save data
class text_area(QPlainTextEdit):
	def __init__(self, read_only):
		super().__init__()
		self.setReadOnly(read_only)
		self.tempFileName = ""
		self.instr = list()
		self.highlighter = SyntaxHighlighter(self.document())
		#self.instr_indicator(0)

	def commit(self, text, client):
		if client == "user":
			self.appendPlainText("You: " + text)
		elif client == "assistant":
			self.appendPlainText("ASM Assistant: " + text)
		elif client == "system":
			self.appendPlainText(text)
		else:
			self.appendPlainText("Unauthorized Usage Detected")

	def instr_indicator(self, pc):
		self.highlighter.clear_highlight()
		self.highlighter.highlight_line(pc)

	def remove_line(self):
		self.setPlainText("\n".join(self.toPlainText().split('\n')[:-1]))

	def saveASM(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"Save Code","","All Files (*);;ASM Files (*.asm)", options=options)
		if fileName:
			file = open(fileName, 'w')
			data = self.toPlainText()
			file.write(data)
			file.close()
			hex_.tempFileName = fileName

	def saveHEX(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		hexfile, _ = QFileDialog.getSaveFileName(self,"Save HEX file","","All Files (*);;HEX Files (*.hex)", options=options)
		if hexfile:
			asmCall.write(self.tempFileName, hexfile)
			file = open(hexfile[:-4] + '_str.hex', 'r')
			self.setPlainText(file.read())

	def get_asm_file(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;ASM Files (*.asm)", options=options)
		if fileName:
			codefile = open(fileName, 'r')
			for code in codefile:
				self.instr.append(code)
				self.insertPlainText(code)
			codefile.close()

	def get_hex_file(self):
		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;HEX Files (*.hex)", options=options)
		if fileName:
			codefile = open(fileName[:-4] + "_str.hex", 'r')
			for code in codefile:
				self.instr.append(code)
				self.insertPlainText(code)
			codefile.close()

class text_box(QLineEdit):
	def __init__(self):
		super().__init__()
		self.history = list([''])
		self.topIndex = 0
		self.tracker = self.topIndex
		self.returnPressed.connect(submit_cmd)

	def keyPressEvent(self, event):
		try:
			if event.key() == Qt.Key_Up:
				self.tracker -= 1 if self.tracker > 0 else 0
				self.setText(self.history[self.tracker])
			elif event.key() == Qt.Key_Down:
				self.tracker += 1 if self.tracker <= self.topIndex else 0
				self.setText(self.history[self.tracker])
			else:
				self.tracker = self.topIndex
				super(text_box, self).keyPressEvent(event)
		except IndexError:
			pass

class RegisterFile(QTableWidget):
	def __init__(self):
		super().__init__()
		self.setColumnCount(2)
		self.setRowCount(32)
		self.setHorizontalHeaderLabels(["Register", "Value"])
		row_index = 0
		for reg in register_file.keys():
			reg = QTableWidgetItem(reg)
			reg.setFlags(Qt.ItemIsEnabled)
			self.setItem(row_index, 0, reg)
			row_index += 1

	def update(self):
		row_index = 0
		for reg in register_file.keys():
			item = QTableWidgetItem(str(register_file[reg])) if register_file[reg] != None else None
			self.setItem(row_index, 1, item)
			row_index += 1

def check_for_label(command):
	cmd_wrd = command.split()
	if "define" in cmd_wrd or "def" in cmd_wrd:
		label = cmd_wrd[1]
		cmd_wrd = cmd_wrd[2:]
		cmd = " ".join(cmd_wrd)
		return label, cmd
	else:
		return None, command

def submit_cmd():
	try:
		command_in = cmd_text.text()
		for keyword in ["erase", "remove", "incorrect", "misinterpreted", "not correct"]:
			if keyword in command_in:
				reia_comms.commit("Understood. Removing previous prediction.......\n", "assistant")
				asm.remove_line()
				cmd_text.setText("")
				return
		cmd_text.history.pop()
		cmd_text.history.append(command_in)
		cmd_text.history.append('')
		cmd_text.topIndex += 1
		cmd_text.tracker = cmd_text.topIndex
		reia_comms.commit(command_in, "user")
		label_def, command = check_for_label(command_in)
		if label_def:
			if '?' in label_def:
				label_def = label_def[1:]
		cl_pred = classify.classify(command)
		asm_inst = interpreter.interpreter(command, cl_pred)
		cmd_text.setText("")
	except IndexError:
		reia_comms.commit("An Error Occured. Have you accidently entered an incorrect instruction? Perhaps submitted a blank query?", "assistant")
		reia_comms.commit("It can also be caused by an irregular number of registers for said instruction\n", "assistant")
		return
	except Exception as err:
		reia_comms.commit("Something went wrong. Can you please try again? Error: " + str(err) + '\n', "assistant")
		return
	reia_comms.commit(asm_inst if not label_def else (label_def + ": " + asm_inst), "assistant")
	reia_comms.commit('', "system")
	asm.commit(asm_inst if not label_def else (label_def + ": " + asm_inst), "system")

def get_cmd():
	reia_comms.commit("Speech Activated. Say Something......", "assistant")
	try:
		speech_in = Speech().lower()
		reia_comms.commit("Speech Done", "assistant")
	except:
		reia_comms.commit("Speech Failed. Please Try Again", "assistant")
		return
	cmd_text.setText(speech_in)

def start_simulator():
	global pc
	if code_area.toPlainText() == '':
		sim_comms.commit("Error: ASM file not loaded", "assistant")
		sim_comms.commit("Hey! You forgot to load the code file! Use the load button to do so!\n", "assistant")
		return
	elif hex_area.toPlainText() == '':
		sim_comms.commit("Error: HEX file not loaded", "assistant")
		sim_comms.commit("Hey! You forgot to load the hex file! Use the load button to do so!\n", "assistant")
		return
	pc = 0
	pc = simulate(pc)

def next_inst():
	global pc
	if pc == None:
		sim_comms.commit("Error: You must \"Start\" the simulation before step into the next instruction\n", "assistant")
		return
	pc = simulate(pc)

def reset_simulator():
	global pc
	pc = None
	code_area.highlighter.clear_highlight()
	code_area.setPlainText('')
	hex_area.setPlainText('')
	code_area.instr = list()
	hex_area.instr = list()
	sim_comms.commit("Understood. Exiting Simulator.........\n", "assistant")

def simulate(pc):
	instruction = hex_area.instr[pc]
	try:
		metrics = simulator.simulate(instruction)
	except Exception as err:
		sim_comms.commit("Instruction Simulation Failed. Error: " + str(err))
		sim_comms.commit("Sorry, I failed to make a decision about what to do here. Can you check for buggy assembly code?\n", "assistant")
		return
	print(metrics)
	try:
		if len(metrics) == 5:
			inst, rs, rt, rd, sh = metrics
			rs_val = register_file[registers[rs]] if register_file[registers[rs]] != None else 0
			rt_val = register_file[registers[rt]] if register_file[registers[rt]] != None else 0
			rd_val = register_file[registers[rd]] if register_file[registers[rd]] != None else 0
			if inst in ["mfhi", "mflo"]:
				register_file[registers[rd]] = getattr(simulator, inst)(rs_val, rt_val, rd_val, sh, special["hi" if inst == "mfhi" else "lo"])
				pc += 1
			elif inst in ["mult", "multu", "div", "divu"]:
				#register_file[registers[rs]] = getattr(simulator, inst)(rs_val, rt_val, rd_val, sh)
				special["hi"], special["lo"] = getattr(simulator, inst)(rs_val, rt_val, rd_val, sh)
				pc += 1
			else:
				register_file[registers[rd]] = getattr(simulator, inst if inst not in ["and","or"] else inst+'_')(rs_val, rt_val, rd_val, sh)
				pc += 1
		elif len(metrics) == 4:
			inst, rs, rt, imm = metrics
			rs_val = register_file[registers[rs]]
			rt_val = register_file[registers[rt]]
			if inst in ["bltz", "beq", "bne"]:
				pc = getattr(simulator, inst)(rs_val, rt_val, imm, True, pc)
			else:
				register_file[registers[rt]] = getattr(simulator, inst)(rs_val, rt_val, imm, False, pc)
				pc += 1
		else:
			inst, jumpaddr = metrics
			pc = getattr(simulator, inst)(jumpaddr, pc)
	except Exception as err:
		sim_comms.commit("Register Fetch Failed. Error: " + str(err))
		sim_comms.commit("Sorry, I failed to make a decision about what to do here. Can you check for buggy assembly code?\n", "assistant")
		return

	register_file_table.update()
	code_area.instr_indicator(pc)
	sim_comms.commit("Instruction Executed Successfully, updating pc.....\n", "assistant")
	return pc

def sim_exe():
	simulator_window.show()

app = app_home([])
window = main_window()
simulator_window = main_window()

main_layout = QGridLayout()
theme_layout = QHBoxLayout()
cmd_input_layout = QHBoxLayout()
datagen_layout = QGridLayout()

icon = QtGui.QIcon('icon_white.png')
cmd_speech = QPushButton()
cmd_speech.setIcon(icon)
theme_label = QLabel("Theme: ")
choose_theme = theme_select("theme")
size_label = QLabel("Window Size: ")
choose_size = theme_select("size")
reia_comms = text_area(True)
cmd_text = text_box()
cmd_submit = QPushButton("Submit")
asm_label = QLabel("Final Assembly Code")
asm_label.setStyleSheet("font-weight: bold;")
asm = text_area(False)
save_asm = QPushButton("Commit .asm")
hex_label = QLabel("Final Hex Code")
hex_label.setStyleSheet("font-weight: bold;")
hex_ = text_area(True)
save_hex = QPushButton("Save as .hex")
simulator_start = QPushButton("Simulator")

theme_layout.addWidget(theme_label)
theme_layout.addWidget(choose_theme)
theme_layout.addWidget(size_label)
theme_layout.addWidget(choose_size)

datagen_layout.addWidget(asm_label, 0, 0)
datagen_layout.addWidget(save_asm, 0, 1)
datagen_layout.addWidget(asm, 1, 0, 1, 0)
datagen_layout.addWidget(hex_label, 2, 0)
datagen_layout.addWidget(save_hex, 2, 1)
datagen_layout.addWidget(hex_, 3, 0, 1, 0)

cmd_input_layout.addWidget(cmd_text)
cmd_input_layout.addWidget(cmd_submit)
cmd_input_layout.addWidget(cmd_speech)

main_layout.addLayout(theme_layout, 0, 0)
main_layout.addWidget(reia_comms, 1, 0)
main_layout.addLayout(datagen_layout, 0, 1, 0, 1)
main_layout.addLayout(cmd_input_layout, 3, 0)
main_layout.addWidget(simulator_start, 4, 0)

cmd_submit.clicked.connect(submit_cmd)
cmd_speech.clicked.connect(get_cmd)
save_asm.clicked.connect(asm.saveASM)
save_hex.clicked.connect(hex_.saveHEX)
simulator_start.clicked.connect(sim_exe)

window.setLayout(main_layout)
window.show()

simulate_layout = QGridLayout()
load_layout = QHBoxLayout()
code_layout = QHBoxLayout()
area_layout = QVBoxLayout()
register_file_layout = QVBoxLayout()
control_layout = QHBoxLayout()

add_asm_label = QLabel("Load .asm file: ")
add_hex_label = QLabel("Load .hex file: ")
add_asm = QPushButton("Load")
add_hex = QPushButton("Load")
register_file_label = QLabel("Register State and Values")
sim_comms_label = QLabel("Terminal")
sim_comms = text_area(True)
code_area = text_area(True)
hex_area = text_area(True)
register_file_table = RegisterFile()
start = QPushButton("Start")
step = QPushButton("Next")
reset = QPushButton("Reset/Exit")

load_layout.addWidget(add_asm_label)
load_layout.addWidget(add_asm)
load_layout.addWidget(add_hex_label)
load_layout.addWidget(add_hex)

code_layout.addWidget(code_area)
code_layout.addWidget(hex_area)

area_layout.addLayout(code_layout)
area_layout.addWidget(sim_comms_label)
area_layout.addWidget(sim_comms)

register_file_layout.addWidget(register_file_label)
register_file_layout.addWidget(register_file_table)

control_layout.addWidget(start)
control_layout.addWidget(step)
control_layout.addWidget(reset)

simulate_layout.addLayout(load_layout, 0, 0)
simulate_layout.addLayout(area_layout, 1, 0)
simulate_layout.addLayout(register_file_layout, 0, 1, 0, 1)
simulate_layout.addLayout(control_layout, 2, 0, 2, 1)

add_asm.clicked.connect(code_area.get_asm_file)
add_hex.clicked.connect(hex_area.get_hex_file)
start.clicked.connect(start_simulator)
step.clicked.connect(next_inst)
reset.clicked.connect(reset_simulator)

simulator_window.setLayout(simulate_layout)

app.exec_()