from PyQt4.QtGui import *
from PyQt4.QtCore import *

class IOWidget(QTextEdit):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.parent = parent
		self.iofont = QFont('Monospace', 12)
		self.backcolor = QColor(255, 255, 255)
		self.setReadOnly(True)
	
	def reload(self):
		self.setText(self.parent.mips.output)
