from PyQt4.QtGui import *
from PyQt4.QtCore import *

class RegListModel(QAbstractListModel):
	def __init__(self, mips, parent = None):
		QAbstractListModel.__init__(self, parent)
		self.mips = mips
		self.hotcolor = QColor(255, 210, 210)
		self.regs = self.mips.allregs()
		self.regfont = QFont('Monospace', 10)
		self.clearhotregs()

	def rowCount(self, parent):
		return len(self.regs)

	def data(self, index, role):
		reg = self.regs[index.row()]
		if role == Qt.DisplayRole:
			return "%s: %s" % (reg, str(self.mips.reg(reg)).ljust(8))

		elif role == Qt.FontRole:
			return self.regfont
		
		elif role == Qt.BackgroundRole:
			if self.hotregs[reg]:
				return self.hotcolor

	def flags(self, index):
		return Qt.ItemIsEnabled

	def clearhotregs(self):
		self.lastregs = {}
		self.hotregs = {}
		for r in self.regs:
			self.lastregs[r] = 0
			self.hotregs[r] = False

	def stepupdate(self):
		for r in self.regs:
			if self.lastregs[r] != self.mips.reg(r):
				self.hotregs[r] = True
			else:
				self.hotregs[r] = False
			self.lastregs[r] = self.mips.reg(r)

	def update(self):
		self.dataChanged.emit(self.index(0, 0), self.index(32, 0))

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
		self.model = RegListModel(self.parent.mips, self)
		self.setModel(self.model)
		self.setResizeMode(QListView.Adjust)
		#self.setLayoutMode(QListView.Batched)
		self.setViewMode(QListView.IconMode)
		self.setFlow (QListView.TopToBottom)
		#self.setItemDelegate(RegItemDelegate())

	def stepupdate(self):
		self.model.stepupdate()

	def clearhotregs(self):
		self.model.clearhotregs()

	def update(self):
		self.model.update()
		self.repaint()

