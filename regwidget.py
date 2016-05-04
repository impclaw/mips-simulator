from PyQt4.QtGui import *
from PyQt4.QtCore import *

class RegListModel(QAbstractListModel):
	def __init__(self, mips, parent = None):
		QAbstractListModel.__init__(self, parent)
		self.mips = mips

	def rowCount(self, parent):
		return len(self.mips.allregs())

	def data(self, index, role):
		if role == Qt.DisplayRole:
			return "Non"

class RegWidget(QListView):
	def __init__(self, parent = None):
		QListView.__init__(self, parent)
		self.parent = parent
		self.backcolor = QColor(255, 255, 255)
		self.textcolor = QColor(0, 0, 0)
		self.regmisccolor = self.backcolor
		self.regtcolor = QColor(255, 230, 230)
		self.regscolor = QColor(230, 255, 230)
		self.regacolor = QColor(230, 230, 250)
		self.setMaximumHeight(7*32)
		self.regfont = QFont('Monospace', 10)
		self.headfont = QFont('Monospace', 12)
		self.model = RegListModel(self.parent.mips, self)
		self.setModel(self.model)
		self.setResizeMode(QListView.Adjust)
		self.setGridSize(QSize(15, 15))

#	def paintEvent(self, event):
#			painter = QPainter()
#			painter.begin(self)
#			painter.setFont(self.regfont)
#			
#			w = event.rect().width()
#			h = event.rect().height()
#			self.h = h
#			self.w = w
#			painter.fillRect(event.rect(), QBrush(self.backcolor))
#
#			painter.drawText(4, 14, "Simulator Registers")
#			ybase = 4 + 20
#			painter.drawLine(0, ybase-5, w, ybase-5)
#			n = 0
#			for reg in self.parent.mips.allregs():
#				x = 4 if n < 16 else w/2
#				y = ybase+n*12 if n < 16 else ybase+(n-16)*12
#
#				cr = self.regmisccolor
#				if reg[0] == 't':
#					cr = self.regtcolor
#				if reg[0] == 's' and reg != 'sp':
#					cr = self.regscolor
#				if (reg[0] == 'a' or reg[0] == 'v') and reg != "at":
#					cr = self.regacolor
#				painter.fillRect(0 if n < 16 else w/2, y-2, w/2 if n < 16 else w, 14, cr)
#
#				painter.drawText(x, y+8, "%s %d" % ((reg+':').ljust(5), self.parent.mips.reg(reg)))
#				n += 1
