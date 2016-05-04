from PyQt4.QtGui import *
from PyQt4.QtCore import *
from mipsmachine import MipsMachine, Instruction
from regwidget import RegWidget
from codewidget import CodeWidget
from memwidget import MemWidget
from iowidget import IOWidget
from mipscoder import MipsCoder
from settings import Settings

class MainWindow(QMainWindow):
	def __init__(self, parent = None):
		QMainWindow.__init__(self, parent)
		self.settings = Settings()
		self.setWindowTitle("MIPS Simulator")
		instr = Instruction.fromfile('tests/test1.s')
		self.mips = MipsMachine(instr)
		self.codewidget = CodeWidget(self)
		self.memwidget = MemWidget(self)
		self.regwidget = RegWidget(self)
		self.iowidget = IOWidget(self)
		self.statusBar().showMessage("Ready")
		self.runtimer = QTimer(self)
		self.runtimer.timeout.connect(self.runtimerTick)
		self.resize(self.settings.mainwindowwidth(), self.settings.mainwindowheight())
		self.move(self.settings.mainwindowx(), self.settings.mainwindowy())

		self.sidewidget = QSplitter()
		self.sidewidget.addWidget(self.regwidget)
		self.sidewidget.addWidget(self.memwidget)
		self.sidewidget.setOrientation(Qt.Vertical)

		self.topsplit = QSplitter()
		self.mainsplit = QSplitter()
		self.mainsplit.setOrientation(Qt.Vertical)
		self.grid = QVBoxLayout()
		self.grid.setSpacing(2)
		self.widget = QWidget(self)
		self.widget.setLayout(self.grid)
		self.setCentralWidget(self.widget)

		self.topsplit.addWidget(self.codewidget)
		self.topsplit.addWidget(self.sidewidget)
		self.topsplit.setSizes([self.settings.codewidgetsize(), self.settings.sidewidgetsize()])
		self.mainsplit.addWidget(self.topsplit)
		self.mainsplit.addWidget(self.iowidget)
		self.mainsplit.setSizes([self.settings.topwidgetsize(), self.settings.iowidgetsize()])
		self.grid.addWidget(self.mainsplit)
		self.grid.setContentsMargins(0, 0, 0, 0)

		#prefpolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		#self.setSizePolicy(prefpolicy)

		self.createToolBar()
		self.createMenuBar()

	def createToolBar(self):
		stepaction = QAction(QIcon("icons/arrow-step.png"), 'Step', self)
		stepaction.triggered.connect(self.toolbarMipsStep)
		runaction = QAction(QIcon("icons/control-run.png"), 'Run', self)
		runaction.triggered.connect(self.toolbarMipsRun)
		fastrunaction = QAction(QIcon("icons/control-double.png"), 'Run Fast', self)
		fastrunaction.triggered.connect(self.toolbarMipsRunFast)
		stopaction = QAction(QIcon("icons/control-stop.png"), 'Stop', self)
		stopaction.triggered.connect(self.toolbarMipsStop)
		resetaction = QAction(QIcon("icons/control-reset.png"), 'Reset', self)
		resetaction.triggered.connect(self.toolbarMipsReset)

		self.toolbar = self.addToolBar('Main')
		self.toolbar.addAction(stepaction)
		self.toolbar.addAction(runaction)
		self.toolbar.addAction(fastrunaction)
		self.toolbar.addAction(stopaction)
		self.toolbar.addAction(resetaction)

	def createMenuBar(self):
		pass

	def reload(self):
		self.iowidget.reload()
		self.memwidget.update()
		self.memwidget.repaint()
		self.regwidget.repaint()

	def toolbarMipsStep(self, e):
		self.mips.step()
		self.reload()

	def toolbarMipsRun(self, e):
		self.runtimer.start(100)

	def toolbarMipsRunFast(self, e):
		self.runtimer.start(10)

	def toolbarMipsStop(self, e):
		self.runtimer.stop()

	def toolbarMipsReset(self, e):
		self.runtimer.stop()
		self.mips.reset()
		self.reload()

	def runtimerTick(self):
		self.mips.step()
		self.reload()

	def closeEvent(self, e):
		self.settings.mainwindowwidth(self.width())
		self.settings.mainwindowheight(self.height())
		self.settings.mainwindowx(self.x())
		self.settings.mainwindowy(self.y())
		self.settings.topwidgetsize(self.mainsplit.sizes()[0])
		self.settings.iowidgetsize(self.mainsplit.sizes()[1])
		self.settings.codewidgetsize(self.topsplit.sizes()[0])
		self.settings.sidewidgetsize(self.topsplit.sizes()[1])

