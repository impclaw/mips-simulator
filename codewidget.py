from PyQt4.QtGui import *
from PyQt4.QtCore import *
from mipscoder import MipsCoder

class SyntaxHighlighter(QSyntaxHighlighter):
	def __init__(self, parent = None):
		QSyntaxHighlighter.__init__(self, parent)
		self.instrfmt = QTextCharFormat()
		self.instrfmt.setForeground(QColor(50, 50, 250))
		self.regfmt = QTextCharFormat()
		self.regfmt.setForeground(QColor(250, 75, 75))
		self.rules = []
		self.rules += [(r'\b%s\b' % w, 0, self.instrfmt) for w in MipsCoder.instructions()]
		self.rules += [(r'\b%s\b' % w, 0, self.regfmt) for w in MipsCoder.regs()]
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
		self.setFont(QFont("Monospace", 12, QFont.Normal))
		self.syntax = SyntaxHighlighter(self)

	def paintEvent(self, event):
		QTextEdit.paintEvent(self, event)
		painter = QPainter(self.viewport())
		tc = self.textCursor()
		tc.select(QTextCursor.WordUnderCursor)
		painter.drawText(250, 250, tc.selectedText())
