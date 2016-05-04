from PyQt4.QtGui import *
from PyQt4.QtCore import *

class CodeWidget(QTextEdit):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.backcolor = QColor(255, 255, 255)
		self.textcolor = QColor(0, 0, 0)
		self.setFont(QFont("Monospace", 12, QFont.Normal))

