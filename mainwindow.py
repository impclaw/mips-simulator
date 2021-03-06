from PyQt4.QtGui import *
from PyQt4.QtCore import *
from mipsmachine import MipsMachine, Instruction, MipsException
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
		self.mips = MipsMachine()
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

		self.openfilename = None
		self.newfile = True

		#prefpolicy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
		#self.setSizePolicy(prefpolicy)

		self.createMenuBar()
		self.createToolBar()
		self.populateMenuBar()
		self.openFile('tests/test1.s')
		
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
		uploadaction.triggered.connect(self.toolbarMipsUpload)
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
		self.regwidget.update()

	def confirmSaveChanges(self):
		return QMessageBox.question(self, "Unsaved Changes", "You have unsaved changes, would you like to save?", QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel);

	def saveFile(self, filename):
		with open(filename, 'w') as f:
			f.write(self.codewidget.toPlainText())
		self.openfilename = filename
		self.newfile = False
		self.codewidget.changed = False

	def openFile(self, filename):
		with open(filename, 'r') as f:
			self.codewidget.setText(f.read())
		self.openfilename = filename
		self.newfile = False
		self.codewidget.changed = False

	def saveAsDialog(self):
		filename = QFileDialog.getSaveFileName(self, "Save file", "", "*.s")
		if filename != '':
			self.saveFile(filename)

	def toolbarNew(self, e): 
		if self.codewidget.changed:
			response = self.confirmSaveChanges()
			if response == QMessageBox.Yes: 
				self.toolbarSave(e)
			elif response == QMessageBox.No:
				self.codewidget.setText("")
			else:
				return
		else:
			self.codewidget.setText("")
		self.openfilename = None
		self.newfile = True
		self.codewidget.changed = False

	def toolbarOpen(self, e): 
		if self.codewidget.changed:
			response = self.confirmSaveChanges()
			if response == QMessageBox.Yes: 
				self.toolbarSave(e)
			elif response == QMessageBox.Cancel:
				return
		filename = QFileDialog.getOpenFileName(self, "Open file", "", "*.s")
		if filename != '':
			self.openFile(filename)

	def toolbarSave(self, e): 
		if self.codewidget.changed and self.openfilename == None:
			self.saveAsDialog()
		elif self.codewidget.changed and self.openfilename != None:
			self.saveFile(self.openfilename)

	def mipsStep(self):
		self.mips.step()
		self.regwidget.stepupdate()
		self.reload()

	def toolbarMipsUpload(self, e):
		self.iowidget.outputmessage("Uploading to MIPS Processor...")
		try:
			instr = Instruction.fromstring(str(self.codewidget.toPlainText()))
			self.mips.load(instr)
			self.iowidget.outputmessage("Upload Successful")
		except MipsException as e:
			self.iowidget.outputmessage("%d: %s" % (e.lineno, e.message))
		self.iowidget.outputmessage("")
		self.reload()

	def toolbarMipsStep(self, e):
		self.mipsStep()

	def toolbarMipsRun(self, e):
		self.runtimer.start(100)

	def toolbarMipsRunFast(self, e):
		self.runtimer.start(10)

	def toolbarMipsStop(self, e):
		self.runtimer.stop()

	def toolbarMipsReset(self, e):
		self.runtimer.stop()
		self.mips.reset()
		self.regwidget.clearhotregs()
		self.reload()

	def runtimerTick(self):
		self.mipsStep()

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

