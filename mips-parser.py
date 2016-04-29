import sys
from PyQt4.QtGui import *
from mainwindow import *

if __name__ == "__main__":
	app = QApplication(sys.argv)
	mw = MainWindow()
	mw.show()
	sys.exit(app.exec_())
