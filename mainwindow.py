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

		self.createMenuBar()
		self.createToolBar()
		self.populateMenuBar()
		
	def createMenuBar(self):
		menubar = self.menuBar()
		self.filemenu = menubar.addMenu('&File')
		self.editmenu = menubar.addMenu('&Edit')
		self.debugmenu = menubar.addMenu('&Debug')

	def populateMenuBar(self):
		exitaction = QAction("E&xit", self)
		self.filemenu.addAction(exitaction)

	def createToolBar(self):
		newaction = QAction(QIcon("icons/document-new.png"), 'New File', self)
		openaction = QAction(QIcon("icons/document-open.png"), 'Open File', self)
		saveaction = QAction(QIcon("icons/document-save.png"), 'Save File', self)
		undoaction = QAction(QIcon("icons/undo.png"), 'Undo', self)
		redoaction = QAction(QIcon("icons/redo.png"), 'Redo', self)
		newaction.triggered.connect(self.toolbarNew)
		openaction.triggered.connect(self.toolbarOpen)
		saveaction.triggered.connect(self.toolbarSave)

		uploadaction = QAction(QIcon("icons/processor.png"), '&Upload to Simulator', self)
		stepaction = QAction(QIcon("icons/arrow-step.png"), '&Step', self)
		runaction = QAction(QIcon("icons/control-run.png"), 'Upload && &Run', self)
		fastrunaction = QAction(QIcon("icons/control-double.png"), 'Upload && Run &Fast', self)
		stopaction = QAction(QIcon("icons/control-stop.png"), 'S&top', self)
		resetaction = QAction(QIcon("icons/control-reset.png"), '&Reset', self)
		stepaction.triggered.connect(self.toolbarMipsStep)
		runaction.triggered.connect(self.toolbarMipsRun)
		fastrunaction.triggered.connect(self.toolbarMipsRunFast)
		stopaction.triggered.connect(self.toolbarMipsStop)
		resetaction.triggered.connect(self.toolbarMipsReset)

		newaction.setShortcut(QKeySequence.New)
		openaction.setShortcut(QKeySequence.Open)
		saveaction.setShortcut(QKeySequence.Save)

		self.fileToolbar = self.addToolBar('File')
		self.fileToolbar.addAction(newaction)
		self.fileToolbar.addAction(openaction)
		self.fileToolbar.addAction(saveaction)
		self.fileToolbar.addSeparator()
		self.fileToolbar.addAction(undoaction)
		self.fileToolbar.addAction(redoaction)
		self.fileToolbar.addSeparator()
		self.debugToolbar = self.addToolBar('Debugging')
		self.debugToolbar.addAction(uploadaction)
		self.debugToolbar.addAction(runaction)
		self.debugToolbar.addAction(fastrunaction)
		self.debugToolbar.addAction(stopaction)
		self.debugToolbar.addSeparator()
		self.debugToolbar.addAction(stepaction)
		self.debugToolbar.addAction(resetaction)
		self.fileToolbar.setMovable(False)
		self.fileToolbar.setFloatable(False)
		self.debugToolbar.setMovable(False)
		self.debugToolbar.setFloatable(False)

		self.filemenu.addAction(newaction)
		self.filemenu.addAction(openaction)
		self.filemenu.addAction(saveaction)
		self.editmenu.addAction(undoaction)
		self.editmenu.addAction(redoaction)
		self.debugmenu.addAction(uploadaction)
		self.debugmenu.addAction(runaction)
		self.debugmenu.addAction(fastrunaction)
		self.debugmenu.addAction(stopaction)
		self.debugmenu.addSeparator()
		self.debugmenu.addAction(stepaction)
		self.debugmenu.addAction(resetaction)

	def reload(self):
		self.iowidget.reload()
		self.memwidget.update()
		self.memwidget.repaint()
		self.regwidget.repaint()

	def toolbarNew(self, e): 
		pass
	def toolbarOpen(self, e): 
		pass
	def toolbarSave(self, e): 
		pass

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
		self.memwidget.saveSettings(self.settings)
		self.settings.mainwindowwidth(self.width())
		self.settings.mainwindowheight(self.height())
		self.settings.mainwindowx(self.x())
		self.settings.mainwindowy(self.y())
		self.settings.topwidgetsize(self.mainsplit.sizes()[0])
		self.settings.iowidgetsize(self.mainsplit.sizes()[1])
		self.settings.codewidgetsize(self.topsplit.sizes()[0])
		self.settings.sidewidgetsize(self.topsplit.sizes()[1])

