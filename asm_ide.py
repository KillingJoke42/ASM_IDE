from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QComboBox, QPlainTextEdit, QLineEdit
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QPushButton, QLabel, QVBoxLayout
from styles import dark_fusion, default

class app_home(QApplication):
	def __init__(self, arg):
		super().__init__(arg)

	def change_theme(self, dark):
		dark_fusion(self) if dark else default(self)

class main_window(QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("ASM_IDE: Making Assembly Language Easier")

class theme_select(QComboBox):
	def __init__(self):
		super().__init__()
		self.addItems(["Dark", "Light"])
		self.setCurrentIndex(1)
		self.currentIndexChanged.connect(self.themeChanged)

	def themeChanged(self):
		if self.currentIndex() == 0:
			app.change_theme(True)
		else:
			app.change_theme(False)

class text_area(QPlainTextEdit):
	def __init__(self):
		super().__init__()
		self.setReadOnly(True)

class text_box(QLineEdit):
	def __init__(self):
		super().__init__()
		
app = app_home([])
window = main_window()

main_layout = QGridLayout()
theme_layout = QHBoxLayout()
cmd_input_layout = QHBoxLayout()
datagen_layout = QGridLayout()

theme_label = QLabel("Theme: ")
choose_theme = theme_select()
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

window.setLayout(main_layout)
window.show()
app.exec_()