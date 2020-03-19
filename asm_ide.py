from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QComboBox, QPlainTextEdit, QLineEdit
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QLabel, QVBoxLayout, QFileDialog
from PyQt5.QtCore import Qt
from PyQt5 import QtGui
from styles import dark_fusion, default
import classify
import interpreter1 as interpreter
import asmCall

# define defult main window
class app_home(QApplication):
	def __init__(self, arg):
		super().__init__(arg)

	def change_theme(self, dark):
		dark_fusion(self) if dark else default(self)

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

	def commit(self, text, client):
		if client == "user":
			self.appendPlainText("You: " + text)
		elif client == "assistant":
			self.appendPlainText("ASM Assistant: " + text)
		elif client == "system":
			self.appendPlainText(text)
		else:
			self.appendPlainText("Unauthorized Usage Detected")

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
	command_in = cmd_text.text()
	cmd_text.history.pop()
	cmd_text.history.append(command_in)
	cmd_text.history.append('')
	cmd_text.topIndex += 1
	cmd_text.tracker = cmd_text.topIndex
	label_def, command = check_for_label(command_in)
	if label_def:
		if '?' in label_def:
			label_def = label_def[1:]
	cl_pred = classify.classify(command)
	asm_inst = interpreter.interpreter(command, cl_pred)
	cmd_text.setText("")
	reia_comms.commit(command_in, "user")
	reia_comms.commit(asm_inst if not label_def else (label_def + ": " + asm_inst), "assistant")
	asm.commit(asm_inst if not label_def else (label_def + ": " + asm_inst), "system")

app = app_home([])
window = main_window()

main_layout = QGridLayout()
theme_layout = QHBoxLayout()
cmd_input_layout = QHBoxLayout()
datagen_layout = QGridLayout()

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

main_layout.addLayout(theme_layout, 0, 0)
main_layout.addWidget(reia_comms, 1, 0)
main_layout.addLayout(datagen_layout, 0, 1, 0, 1)
main_layout.addLayout(cmd_input_layout, 3, 0)

cmd_submit.clicked.connect(submit_cmd)
save_asm.clicked.connect(asm.saveASM)
save_hex.clicked.connect(hex_.saveHEX)

window.setLayout(main_layout)
window.show()
app.exec_()