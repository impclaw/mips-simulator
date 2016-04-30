from PyQt4.QtGui import *
from PyQt4.QtCore import *
from mipsmachine import MipsMachine, Instruction
from regwidget import RegWidget
from codewidget import CodeWidget
from memwidget import MemWidget
from iowidget import IOWidget
from mipscoder import MipsCoder

class MainWindow(QMainWindow):
	def __init__(self, parent = None):
		QMainWindow.__init__(self, parent)
		self.setWindowTitle("MIPS Simulator")
		instr = Instruction.fromfile('tests/test1.s')
		self.mips = MipsMachine(instr)
		print MipsCoder.decode(self.mips.nopinstr)
		self.codewidget = CodeWidget(self)
		self.memwidget = MemWidget(self)
		self.regwidget = RegWidget(self)
		self.iolabel = QLabel("Output: ")
		self.iolabel.setMaximumHeight(14)
		self.iowidget = IOWidget(self)
		self.statusBar().showMessage("Ready")
		self.runtimer = QTimer(self)
		self.runtimer.timeout.connect(self.runtimerTick)
		self.mainlayout = QVBoxLayout()
		self.sidelayout = QVBoxLayout()

		self.grid = QHBoxLayout()
		self.grid.setSpacing(2)
		self.widget = QWidget(self)
		self.widget.setLayout(self.grid)
		self.setCentralWidget(self.widget)

		self.mainlayout.addWidget(self.codewidget)
		self.mainlayout.addWidget(self.iolabel)
		self.mainlayout.addWidget(self.iowidget)
		self.sidelayout.addWidget(self.regwidget)
		self.sidelayout.addWidget(self.memwidget)
		self.grid.addLayout(self.mainlayout)
		self.grid.addLayout(self.sidelayout)
		self.grid.setContentsMargins(0, 0, 0, 0)

		#prefpolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		#self.setSizePolicy(prefpolicy)

		self.createToolBar()

		self.resize(800, 600)
		self.move(200, 200)

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
