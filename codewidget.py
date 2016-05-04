import json
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
		self.loadhighlighting()
		self.instrfmt = QTextCharFormat()
		self.instrfmt.setForeground(QColor(50, 50, 250))
		self.regfmt = QTextCharFormat()
		self.regfmt.setForeground(QColor(250, 75, 75))
		self.rules = []
		self.rules += [(r'\b%s\b' % w.code, 0, self.instrfmt) for w in self.instructions]
		self.rules += [(r'\b%s\b' % w, 0, self.regfmt) for w in MipsCoder.regs()]
		self.rules = [(QRegExp(pat), index, fmt) for (pat, index, fmt) in self.rules]

	def loadhighlighting(self):
		self.instructions = []
		with open('mips/mipshighlight.json', 'r') as f:
			data = json.loads(f.read())
			for sym in data:
				self.instructions.append(CodeInstruction(sym['code'], sym['name'], sym['text'], sym['args']))

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

	def keyPressEvent(self, event):
		QTextEdit.keyPressEvent(self, event)
		self.viewport().repaint(0, 0, self.width(), self.height())

	def paintEvent(self, event):
		QTextEdit.paintEvent(self, event)
		painter = QPainter(self.viewport())
		tc = self.textCursor()
		curpos = tc.position()
		position = self.cursorRect()
		tc.select(QTextCursor.LineUnderCursor)
		line = unicode(tc.selectedText())
		tokens = [x.strip() for x in line.strip().split(' ')]
		if len(tokens) == 0 or len(tokens[0]) == 0:
			return
		cmd = tokens[0]
		args = tokens[1].split(',') if len(tokens) > 1 else []
		lst = []
		for i in self.syntax.instructions:
			if i.code.startswith(cmd):
				lst.append(i)
		if len(lst) > 0:
			cr = self.textcolor
			painter.setFont(self.smallbold)
			painter.setBrush(QBrush(self.tooltipcolor))
			painter.drawRect(position.x() + 20, position.y() + 20, 400, 64 + len(lst) * 14)
			painter.drawLine(position.x() + 20, position.y() + 50, position.x() + 420, position.y() + 50)
			l = lst[0]
			painter.setPen(QPen(QColor(cr)))
			if len(lst) > 1:
				painter.drawText(position.x() + 26, position.y() + 40, "%s: %s" % (l.code, l.name))
				painter.setFont(self.smallfont)
				painter.setPen(QPen(QColor(self.textcolor)))
				i = 0
				for l in lst[1:]:
					painter.drawText(position.x() + 26, position.y() + 70 + 16*i, "%s: %s" % (l.code, l.name))
					i += 1
			else:
				cr = self.textcolor
				x = position.x() + 26
				painter.drawText(position.x() + 26, position.y() + 40, l.code)
				fm = painter.fontMetrics();
				x += fm.width(l.code) + 8
				argno = 0
				for arg in l.args:
					argtxt = arg + ("," if arg != l.args[-1:][0] else "")
					painter.setPen(QPen(QColor(cr)))
					painter.drawText(x, position.y() + 40, argtxt)
					x += fm.width(argtxt) + 8
					argno += 1


				painter.setPen(QPen(QColor(self.textcolor)))
				painter.drawText(position.x() + 26, position.y() + 70, l.name)
				painter.setFont(self.smallfont)
				painter.drawText(position.x() + 26, position.y() + 70+16, l.text)
