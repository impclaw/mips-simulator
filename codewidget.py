from PyQt4.QtGui import *
from PyQt4.QtCore import *
from mipscoder import MipsCoder

class CodeInstruction():
	def __init__(self, code, name, text, args):
		self.code = code
		self.name = name
		self.text = text
		self.args = args

class SyntaxHighlighter(QSyntaxHighlighter):
	def __init__(self, parent = None):
		QSyntaxHighlighter.__init__(self, parent)
		self.instrfmt = QTextCharFormat()
		self.instrfmt.setForeground(QColor(50, 50, 250))
		self.regfmt = QTextCharFormat()
		self.regfmt.setForeground(QColor(250, 75, 75))
		self.commentfmt = QTextCharFormat()
		self.commentfmt.setForeground(QColor(50, 180, 50))
		self.rules = []
		self.rules += [(r'\b%s\b' % w, 0, self.instrfmt) for w in MipsCoder.instructions()]
		self.rules += [(r'\b%s\b' % w, 0, self.regfmt) for w in MipsCoder.regs()]
		self.rules += [(r'#.+', 0, self.commentfmt)]
		self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in self.rules]

	def highlightBlock(self, text):
		for expression, nth, format in self.rules:
			index = expression.indexIn(text, 0)
			while index >= 0:
				index = expression.pos(nth)
				length = expression.cap(nth).length()
				self.setFormat(index, length, format)
				index = expression.indexIn(text, index + length)
		self.setCurrentBlockState(0)

class CodeWidget(QTextEdit):
	def __init__(self, parent = None):
		QTextEdit.__init__(self, parent)
		self.backcolor = QColor(255, 255, 255)
		self.textcolor = QColor(0, 0, 0)
		self.tooltipcolor = QColor(250, 250, 210)
		self.correctcolor = QColor(32, 192, 32)
		self.wrongcolor = QColor(192, 32, 32)
		self.setFont(QFont("Monospace", 12, QFont.Normal))
		self.smallfont = QFont("Monospace", 10, QFont.Normal)
		self.smallbold = QFont("Monospace", 10, QFont.Bold)
		self.syntax = SyntaxHighlighter(self)
		self.setAcceptRichText(False)
		self.changed = False

	def keyPressEvent(self, event):
		QTextEdit.keyPressEvent(self, event)
		self.changed = True
