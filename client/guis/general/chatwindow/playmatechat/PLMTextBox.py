# -*- coding: gb18030 -*-

# 好友聊天文本框
# written by gjx 2010-06-19

from guis.controls.MLRichTextBox import MLRichTextBox
from guis.tooluis.CSMLRichTextBox import EEmotion, EItem
from ChatFacade import emotionParser, chatObjParsers


class PLMTextBox( MLRichTextBox ) :

	def __init__( self, panel, sb, pyBinder = None ) :
		MLRichTextBox.__init__( self, panel, sb, pyBinder )
		self.setCSTemplates()

	def setCSTemplates( self ) :
		"""
		设置转义模板
		"""
		tpls = []
		if emotionParser.reTpl :
			tpls.append( ( emotionParser.reTpl, EEmotion ) )
		if chatObjParsers.reTpl :
			tpls.append( ( chatObjParsers.reTpl, EItem ) )
		self.setEscTemplates( tpls )

	def notifyInput( self, text, count = 0 ) :
		if not self.tabStop : self.tabStop = True
		MLRichTextBox.notifyInput( self, text, count )