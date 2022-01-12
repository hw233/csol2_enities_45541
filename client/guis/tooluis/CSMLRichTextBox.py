# -*- coding: gb18030 -*-
#

"""
implement multiline richtext box for chuangshi class。

2010.03.03: writen by huangyongwei
"""

from guis import *
from guis.controls.StaticText import StaticText
from guis.controls.MLRichTextBox import MLRichTextBox
from guis.controls.MLRichTextBox import BaseElement
from guis.tooluis.emotionbox.FaceIcon import FaceIcon
from guis.tooluis.emotionbox.EmotionBox import Emote
from ChatFacade import emotionParser, chatObjParsers

class CSMLRichTextBox( MLRichTextBox ) :
	def __init__( self, panel, pySBar, pyBinder = None ) :
		MLRichTextBox.__init__( self, panel, pySBar, pyBinder )
		self.setCSTemplates()

	def setCSTemplates( self, page = 0 ) :
		"""
		设置为《创世》的转义模板
		"""
		tpls = [
				( emotionParser.reTpl, EEmotion ),
			]
		self.setEscTemplates( tpls )

# --------------------------------------------------------------------
# 表情元素
# --------------------------------------------------------------------
class EEmotion( BaseElement, FaceIcon ) :
	def __init__( self, start, wtext ) :
		BaseElement.__init__( self, start, wtext )
		path, dsp = emotionParser.getEmotion( wtext )
		FaceIcon.__init__( self )
		self.focus  = False
		self.crossFocus = False
		self.update( Emote( wtext, path, dsp ) )
		self.play()

# --------------------------------------------------------------------
# 物品元素
# --------------------------------------------------------------------
class EItem( BaseElement, StaticText ) :
	def __init__( self, start, text ) :
		BaseElement.__init__( self, start, text )
		StaticText.__init__( self )


	# ----------------------------------------------------------------
	# protect
	# ----------------------------------------------------------------
	def setAttributes_( self, pyRich ) :
		"""
		根据 pyRich 的属性，设置文本属性
		"""
		self.font = pyRich.font
		self.fontSize = pyRich.fontSize
		self.charSpace = pyRich.charSpace
		self.limning = pyRich.limning
		self.limnColor = pyRich.limnColor


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@staticmethod
	def getInst( start, wtext ) :
		"""
		是否有效
		"""
		viewTextInfo = chatObjParsers.getViewObj( wtext )
		if viewTextInfo is None : return None
		viewText, color = viewTextInfo
		pyItem = EItem( start, wtext )
		StaticText._setColor( pyItem, color )
		pyItem.text = viewText
		return pyItem

	# -------------------------------------------------
	def getWViewText( self, scope = None ) :
		"""
		获取表现文本
		"""
		if scope is None :
			return self.wtext
		elif scope[0] < self.end and scope[1] > self.start :
			return self.wtext
		return csstring.toWideString( "" )

	# ---------------------------------------
	def getViewLen( self ) :
		"""
		获取可视文本的字符数
		"""
		return self.length

	def getWViewLen( self ) :
		"""
		获取可视文本的字数
		"""
		return self.wlength
