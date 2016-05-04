from types import MethodType
from PyQt4.QtCore import *

class Settings():
	def __init__(self):
		self.settings = QSettings("mips-parser", "settings")

	def mainwindowx(self, value = None): return self.intparam("gui/mainwindowx", 600, value)
	def mainwindowy(self, value = None): return self.intparam("gui/mainwindowy", 600, value)
	def mainwindowheight(self, value = None): return self.intparam("gui/mainwindowheight", 600, value)
	def mainwindowwidth(self, value = None): return self.intparam("gui/mainwindowwidth", 800, value)
	def iowidgetsize(self, value = None): return self.intparam("gui/iowidgetsize", 100, value)
	def topwidgetsize(self, value = None): return self.intparam("gui/topwidgetsize", 500, value)
	def sidewidgetsize(self, value = None): return self.intparam("gui/sidewidgetsize", 250, value)
	def codewidgetsize(self, value = None): return self.intparam("gui/codewidgetsize", 550, value)
	def memshowtype(self, value = None): return self.intparam("mem/showtype", 1, value)
	def memfollowpc(self, value = None): return self.boolparam("mem/followpc", 0, value)

	def intparam(self, name, default, value):
		if value == None:
			return self.settings.value(name, default).toInt()[0]
		else:
			self.settings.setValue(name, value)

	def boolparam(self, name, default, value):
		if value == None:
			return self.settings.value(name, default).toBool()
		else:
			self.settings.setValue(name, value)
