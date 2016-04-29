from PyQt4.QtGui import *
from PyQt4.QtCore import *
from __builtin__ import hex

class MemWidget(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.parent = parent
		self.backcolor = QColor(255, 255, 255)
		self.textcolor = QColor(0, 0, 0)
		self.rowcolor = QColor(255, 255, 210)
		self.rowaltcolor = QColor(240, 240, 190)
		self.pccolor = QColor(210, 210, 250)
		self.setMaximumWidth(300)
		self.memfont = QFont('Monospace', 10)

	def paintEvent(self, event):
			painter = QPainter()
			painter.begin(self)
			painter.setFont(self.memfont)
			
			w = event.rect().width()
			h = event.rect().height()
			self.h = h
			self.w = w
			painter.fillRect(event.rect(), QBrush(self.backcolor))
			pc = self.parent.mips.reg('pc')
			instr = self.parent.mips.memoryrange(start=pc/4 - (h/14/2), end=pc/4 + (h/14/2))
			ybase = 4 + 20
			painter.fillRect(0, ybase-6, w, h, self.rowcolor)
			painter.drawLine(0, ybase-6, w, ybase-6)
			painter.drawText(4, 14, "Simulator Memory")
			n = 0
			for i in instr:
				x = 0
				y = ybase + n*14
				if i == pc:
					painter.fillRect(x, y-1, w, 13, self.pccolor)
				elif n % 2 == 0:
					painter.fillRect(x, y-1, w, 13, self.rowaltcolor)
				else:
					painter.fillRect(x, y-1, w, 13, self.rowcolor)
				addr = hex(i).rjust(8, '0')
				mem = self.parent.mips.mem(i)
				if mem == None or mem == 0:
					addrtxt = "         nop"
				else:
					label = ""
					if mem.label != None:
						label = mem.label+':'
					addrtxt = "%s %s" % (label.rjust(8), mem.text)
				painter.drawText(x, y + 10, "%s %s" % (addr, addrtxt))
				n += 1
