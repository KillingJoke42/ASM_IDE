from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QComboBox, QPlainTextEdit, QLineEdit
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from styles import dark_fusion, default
import classify
import interpreter1 as interpreter
#import CompilerForMachineCode as asmtobin

class app_home(QApplication):
	def __init__(self, arg):
		super().__init__(arg)

	def change_theme(self, dark):
		dark_fusion(self) if dark else default(self)

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

class text_area(QPlainTextEdit):
	def __init__(self):
		super().__init__()
		self.setReadOnly(True)

	def commit(self, text, client):
		if client == "user":
			self.appendPlainText("You: " + text)
		elif client == "assistant":
			self.appendPlainText("ASM Assistant: " + text)
		elif client == "system":
			self.appendPlainText(text)
		else:
			self.appendPlainText("Unauthorized Usage Detected")

class text_box(QLineEdit):
	def __init__(self):
		super().__init__()
		self.history = list()
		self.returnPressed.connect(submit_cmd)

def submit_cmd():
	command = cmd_text.text()
	cl_pred = classify.classify(command)
	asm_inst = interpreter.interpreter(command, cl_pred)
	#bin_inst = asmtobin.
	cmd_text.setText("")
	reia_comms.commit(command, "user")
	reia_comms.commit(asm_inst, "assistant")
	asm.commit(asm_inst, "system")

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
reia_comms = text_area()
cmd_text = text_box()
cmd_submit = QPushButton("Submit")
asm_label = QLabel("Final Assembly Code")
asm_label.setStyleSheet("font-weight: bold;")
asm = text_area()
save_asm = QPushButton("Save as .asm")
hex_label = QLabel("Final Hex Code")
hex_label.setStyleSheet("font-weight: bold;")
hex_ = text_area()
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

window.setLayout(main_layout)
window.show()
app.exec_()