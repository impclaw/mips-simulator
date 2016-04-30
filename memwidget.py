from PyQt4.QtGui import *
from PyQt4.QtCore import *
from mipscoder import MipsCoder
from __builtin__ import hex

class MemWidget(QWidget):
	def __init__(self, parent):
		QWidget.__init__(self, parent)
		self.parent = parent
		self.vb = QHBoxLayout()
		self.setLayout(self.vb)
		self.scroll = QScrollBar()
		self.memwidget = InternalMemWidget(parent)
		self.vb.addWidget(self.memwidget)
		self.vb.addWidget(self.scroll)
		self.vb.setContentsMargins(0, 0, 0, 0)
		self.scroll.setMinimum(0)
		self.update()
		self.scroll.valueChanged.connect(self.scrolled)

	def scrolled(self):
		self.memwidget.scroll = self.scroll.value()
		self.memwidget.repaint()

	def update(self):
		self.scroll.setMaximum(len(self.parent.mips.memory))
		value = self.scroll.value()
		if self.memwidget.followpc:
			pc = self.parent.mips.reg("pc")
			value = pc / 4
		self.scroll.setValue(value)
		self.memwidget.scroll = self.scroll.value()

class InternalMemWidget(QWidget):
	SHOWTYPE_OP = 1
	SHOWTYPE_ASCII = 2
	SHOWTYPE_INT = 3
	SHOWTYPE_HEX = 4
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.parent = parent
		self.followpc = False
		self.scroll = 0
		self.backcolor = QColor(255, 255, 255)
		self.textcolor = QColor(0, 0, 0)
		self.rowcolor = QColor(255, 255, 210)
		self.rowaltcolor = QColor(240, 240, 190)
		self.pccolor = QColor(210, 210, 250)
		self.setMaximumWidth(300)
		self.setMinimumWidth(300)
		self.memfont = QFont('Monospace', 10)
		self.setupmenu()
		self.showtype = InternalMemWidget.SHOWTYPE_OP
		self.menushowop.setChecked(True)

	def setupmenu(self):
		self.setContextMenuPolicy(Qt.CustomContextMenu)
		self.customContextMenuRequested.connect(self.contextMenu)
		self.popMenu = QMenu(self)
		self.menufollowpc = QAction("Follow PC", self)
		self.menushowop = QAction("Show Opcodes", self)
		self.menushowascii = QAction("Show ASCII", self)
		self.menushowint = QAction("Show Integers", self)
		self.menushowhex = QAction("Show Hex", self)
		self.menufollowpc.setCheckable(True)
		self.menushowop.setCheckable(True)
		self.menushowascii.setCheckable(True)
		self.menushowint.setCheckable(True)
		self.menushowhex.setCheckable(True)
		self.popMenu.addSeparator()
		self.popMenu.addAction(self.menufollowpc)
		self.popMenu.addSeparator()
		self.popMenu.addAction(self.menushowop)
		self.popMenu.addAction(self.menushowascii)
		self.popMenu.addAction(self.menushowint)
		self.popMenu.addAction(self.menushowhex)

		self.menufollowpc.triggered.connect(self.menuFollowPCClicked)
		self.menushowop.triggered.connect(self.menuShowOpClicked)
		self.menushowascii.triggered.connect(self.menuShowAsciiClicked)
		self.menushowint.triggered.connect(self.menuShowIntClicked)
		self.menushowhex.triggered.connect(self.menuShowHexClicked)

	def menuFollowPCClicked(self, checked):
		self.followpc = checked
		self.parent.memwidget.update()

	def uncheckShow(self):
		self.menushowop.setChecked(False)
		self.menushowascii.setChecked(False)
		self.menushowint.setChecked(False)
		self.menushowhex.setChecked(False)
		self.repaint()

	def menuShowOpClicked(self, checked):
		self.showtype = InternalMemWidget.SHOWTYPE_OP
		self.uncheckShow()
		self.menushowop.setChecked(True)

	def menuShowAsciiClicked(self, checked):
		self.showtype = InternalMemWidget.SHOWTYPE_ASCII
		self.uncheckShow()
		self.menushowascii.setChecked(True)

	def menuShowIntClicked(self, checked):
		self.showtype = InternalMemWidget.SHOWTYPE_INT
		self.uncheckShow()
		self.menushowint.setChecked(True)

	def menuShowHexClicked(self, checked):
		self.showtype = InternalMemWidget.SHOWTYPE_HEX
		self.uncheckShow()
		self.menushowhex.setChecked(True)

	def contextMenu(self, point):
		gpoint = self.mapToGlobal(point)
		point = QPoint(gpoint.x()+2, gpoint.y()+2)
		self.popMenu.exec_(point) 

	def mousePressEvent(self, event):
		lineno = (event.y() - 24) / 12

	def mouseDoubleClickEvent(self, event):
		lineno = (event.y() - 24) / 12
		if event.button() == 1:
			pc = self.parent.mips.reg('pc')
			self.parent.mips.breakpoints.append(pc/4-(self.h/14/2)+lineno*4)
			print hex(self.parent.mips.breakpoints[-1])
			self.repaint()

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
			instr = self.parent.mips.memoryrange(start=self.scroll - (h/14/2), end=self.scroll + (h/14/2))
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
				instr = self.parent.mips.mem(i)
				label = ""
				if instr.label != None:
					label = instr.label+':'
				instrtxt = ""
				if self.showtype == InternalMemWidget.SHOWTYPE_OP:
					instrtxt = instr.getopcode()
				elif self.showtype == InternalMemWidget.SHOWTYPE_ASCII:
					decoded =  MipsCoder.decode(instr)
					instrtxt = chr((decoded >> 24) & 0xFF) + chr((decoded >> 16) & 0xFF) + \
					           chr((decoded >> 8) & 0xFF) + chr((decoded) & 0xFF)
				elif self.showtype == InternalMemWidget.SHOWTYPE_INT:
					instrtxt = MipsCoder.decode(instr)
				elif self.showtype == InternalMemWidget.SHOWTYPE_HEX:
					instrtxt = hex(MipsCoder.decode(instr))

				addrtxt = "%s %s" % (label.rjust(8), instrtxt)
				painter.drawText(x, y + 10, "%s %s" % (addr, addrtxt))
				n += 1
