from PyQt4.QtGui import *
from PyQt4.QtCore import *

class CodeWidget(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.backcolor = QColor(255, 255, 255)
		self.textcolor = QColor(0, 0, 0)

	def paintEvent(self, event):
			painter = QPainter()
			painter.begin(self)
			painter.setFont(QFont("Ubuntu", 14, QFont.Normal))
			
			w = event.rect().width()
			h = event.rect().height()
			self.h = h
			self.w = w
			painter.fillRect(event.rect(), QBrush(self.backcolor))

