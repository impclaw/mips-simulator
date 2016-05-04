import sys
from PyQt4.QtGui import *
from mainwindow import *

if __name__ == "__main__":
	MipsCoder.initialize('mips/mipscodes')
	app = QApplication(sys.argv)
	mw = MainWindow()
	mw.show()
	sys.exit(app.exec_())
