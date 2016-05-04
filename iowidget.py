from PyQt4.QtGui import *
from PyQt4.QtCore import *

class IOWidget(QTabWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.parent = parent
		self.iofont = QFont('Monospace', 12)
		self.iotext = QTextEdit()
		self.iotext.setReadOnly(True)
		self.iotext.setFont(self.iofont)
		self.immediate = QTextEdit()
		self.callstack = StackWidget()
		self.buttons = ButtonWidget()
		self.addTab(self.iotext, "Console")
		self.addTab(self.callstack, "Stack")
		self.addTab(self.buttons, "Physical Hardware")
		self.addTab(self.immediate, "Immediate")
		self.setTabIcon(0, QIcon("icons/console.png"))
		self.setTabIcon(1, QIcon("icons/memory.png"))
		self.setTabIcon(2, QIcon("icons/processor.png"))
		self.setTabIcon(3, QIcon("icons/console-run.png"))
	
	def reload(self):
		self.iotext.setText(self.parent.mips.output)

class StackWidget(QListView):
	def __init__(self, parent = None):
		QListView.__init__(self, parent)

class ButtonWidget(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.grid = QGridLayout()
		self.setLayout(self.grid)
		self.setMaximumWidth(32*8+64)
		self.setMaximumHeight(152)

		self.grid.addWidget(QLabel("Leds (Output)"), 0, 0, 1, 8)
		self.lamps = []
		for i in range(0, 8):
			lamp = LedLamp()
			self.lamps.append(lamp)
			self.grid.addWidget(lamp, 1, i)

		self.grid.addWidget(QLabel("Switches (Input)"), 2, 0, 1, 8)
		self.switches = []
		for i in range(0, 8):
			switch = InputSwitch()
			self.switches.append(switch)
			self.grid.addWidget(switch, 3, i)

class LedLamp(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.setMaximumWidth(32)
		self.setMaximumHeight(32)
		self.offcolor = QColor(32, 32, 32)
		self.oncolor = QColor(255, 92, 92)
		self.bordercolor = QColor(72, 72, 72)
		self.state = False

	def sizeHint(self):
		return QSize(32, 32)

	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		painter.setRenderHint(QPainter.Antialiasing)
		bgcolor = self.palette().color(QPalette.Button) 
		
		w = event.rect().width()
		h = event.rect().height()
		self.h = h
		self.w = w
		#painter.fillRect(event.rect(), QBrush(bgcolor))
		painter.setPen(QPen(self.bordercolor, 2))
		painter.setBrush(QBrush(self.oncolor if self.state else self.offcolor))
		painter.drawEllipse(2, 2, 28, 28)

class InputSwitch(QWidget):
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.setMaximumWidth(32)
		self.setMaximumHeight(40)
		self.color = QColor(255, 255, 255)
		self.bordercolor = QColor(72, 72, 72)
		self.state = True

	def sizeHint(self):
		return QSize(32, 40)

	def paintEvent(self, event):
		painter = QPainter()
		painter.begin(self)
		painter.setRenderHint(QPainter.Antialiasing)
		bgcolor = self.palette().color(QPalette.Button) 
		
		w = event.rect().width()
		h = event.rect().height()
		self.h = h
		self.w = w
		#painter.fillRect(event.rect(), QBrush(bgcolor))
		painter.setPen(QPen(self.bordercolor, 2))
		#painter.setBrush(QBrush(self.color))
		if self.state:
			painter.drawRect(2, 2, w - 4, (h - 4)/2)

