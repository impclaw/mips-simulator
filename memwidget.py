from PyQt4.QtGui import *
from PyQt4.QtCore import *
from mipscoder import MipsCoder
from __builtin__ import hex

class MemListModel(QAbstractTableModel):
	def __init__(self, mips, parent = None):
		QAbstractTableModel.__init__(self, parent)
		self.mips = mips
		self.showtype = MemWidget.SHOWTYPE_OP
		self.codefont = QFont('Monospace', 10)
		self.backcolor = QColor(255, 255, 255)
		self.textcolor = QColor(0, 0, 0)
		self.rowcolor = QColor(255, 255, 210)
		self.rowaltcolor = QColor(240, 240, 190)
		self.pccolor = QColor(210, 210, 250)

	def rowCount(self, parent):
		return len(self.mips.memory)

	def columnCount(self, parent):
		return 3

	def setShowType(self, showtype):
		self.showtype = showtype

	def updateStep(self):
		pc = self.mips.reg("pc")
		self.dataChanged.emit(self.index(pc/4-1, 0), self.index(pc/4+1, 2))

	def data(self, index, role):
		#print index.column(), index.row()
		if role == Qt.DisplayRole:
			instr = self.mips.memoryat(index.row()*4)
			if index.column() == 0:
				return '0x%08X' % (index.row()*4)
			elif index.column() == 1:
				return instr.label+':' if instr.label != None else ""
			elif index.column() == 2:
				instrtxt = ""
				if self.showtype == MemWidget.SHOWTYPE_OP:
					instrtxt = instr.getopcode()
				elif self.showtype == MemWidget.SHOWTYPE_ASCII:
					decoded =  MipsCoder.decode(instr)
					instrtxt = chr((decoded >> 24) & 0xFF) + chr((decoded >> 16) & 0xFF) + \
							   chr((decoded >> 8) & 0xFF) + chr((decoded) & 0xFF)
				elif self.showtype == MemWidget.SHOWTYPE_INT:
					instrtxt = MipsCoder.decode(instr)
				elif self.showtype == MemWidget.SHOWTYPE_HEX:
					instrtxt = '0x%08X' % MipsCoder.decode(instr)
				return instrtxt
			else:
				return None
		elif role == Qt.FontRole:
			return self.codefont
		elif role == Qt.BackgroundRole:
			if self.mips.reg("pc") / 4 == index.row():
				return self.pccolor
			if index.row() % 2 == 0:
				return self.rowcolor
			else:
				return self.rowaltcolor
		else:
			return None

	def headerData(self, section, orientation, role):
		if role == Qt.DisplayRole:
			if orientation == Qt.Horizontal:
				if section == 0: return "Address"
				elif section == 1: return "Label"
				elif section == 2: return "Contents"
				else: return QVariant()
		elif role == Qt.SizeHintRole:
			pass
			#if section == 0: return QSize(50, 10)
		else: return QVariant()

	def flags(self, index):
		return Qt.ItemIsEnabled

class MemWidget(QTableView):
	SHOWTYPE_OP = 1
	SHOWTYPE_ASCII = 2
	SHOWTYPE_INT = 3
	SHOWTYPE_HEX = 4
	def __init__(self, parent = None):
		QWidget.__init__(self, parent)
		self.parent = parent
		self.scroll = 0
		self.followpc = self.parent.settings.memfollowpc()
		self.showtype = self.parent.settings.memshowtype()
		self.model = MemListModel(self.parent.mips, self)
		self.setModel(self.model)
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)
		self.setShowGrid(False)
		self.setFont(QFont('Monospace', 10))
		self.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.setColumnWidth(0, 90)
		self.setColumnWidth(2, 150)
		self.setRowHeight(0, 20)
		self.verticalHeader().setVisible(False)
		self.verticalHeader().setDefaultSectionSize(16)
		self.horizontalHeader().setStretchLastSection(True)
		self.setupmenu()

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
		if self.showtype == MemWidget.SHOWTYPE_OP:
			self.menuShowOpClicked(True)
		elif self.showtype == MemWidget.SHOWTYPE_ASCII:
			self.menuShowAsciiClicked(True)
		elif self.showtype == MemWidget.SHOWTYPE_INT:
			self.menuShowIntClicked(True)
		elif self.showtype == MemWidget.SHOWTYPE_HEX:
			self.menuShowHexClicked(True)
		if self.followpc:
			self.menufollowpc.setChecked(True)

	def menuFollowPCClicked(self, checked):
		self.followpc = checked
		self.update()

	def uncheckShow(self):
		self.menushowop.setChecked(False)
		self.menushowascii.setChecked(False)
		self.menushowint.setChecked(False)
		self.menushowhex.setChecked(False)
		self.repaint()

	def menuShowOpClicked(self, checked):
		self.showtype = MemWidget.SHOWTYPE_OP
		self.uncheckShow()
		self.menushowop.setChecked(True)
		self.update()

	def menuShowAsciiClicked(self, checked):
		self.showtype = MemWidget.SHOWTYPE_ASCII
		self.uncheckShow()
		self.menushowascii.setChecked(True)
		self.update()

	def menuShowIntClicked(self, checked):
		self.showtype = MemWidget.SHOWTYPE_INT
		self.uncheckShow()
		self.menushowint.setChecked(True)
		self.update()

	def menuShowHexClicked(self, checked):
		self.showtype = MemWidget.SHOWTYPE_HEX
		self.uncheckShow()
		self.menushowhex.setChecked(True)
		self.update()

	def contextMenu(self, point):
		gpoint = self.mapToGlobal(point)
		point = QPoint(gpoint.x()+2, gpoint.y()+2)
		self.popMenu.exec_(point) 

	def update(self):
		pc = self.parent.mips.reg("pc")
		self.model.setShowType(self.showtype)
		if self.followpc:
			self.scrollTo(self.model.index(pc/4, 0), QAbstractItemView.PositionAtCenter)
		self.model.updateStep()
		self.repaint()

	def sizeHint(self):
		return QSize(300, 100)
		
	def saveSettings(self, settings):
		settings.memshowtype(self.showtype)
		settings.memfollowpc(self.followpc)

