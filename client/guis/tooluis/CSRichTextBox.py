# -*- coding: gb18030 -*-
#

"""
implement richtext box class for ������

2009.12.17: writen by huangyongwei
"""

import struct
import csstring
from ChatFacade import emotionParser, chatObjParsers
from guis import *
from guis.controls.RichTextBox import RichTextBox
from guis.controls.RichTextBox import BaseElement
from guis.controls.StaticText import StaticText
from guis.tooluis.emotionbox.FaceIcon import FaceIcon
from guis.tooluis.emotionbox.EmotionBox import Emote
class CSRichTextBox( RichTextBox ) :
	def __init__( self, box, pyBinder = None ) :
		RichTextBox.__init__( self, box, pyBinder )
		self.setCSTemplates()

	def setCSTemplates( self, page = 0 ) :
		"""
		����Ϊ����������ת��ģ��
		"""
		tpls = []
		if emotionParser.reTpl:
			tpls.append( ( emotionParser.reTpl, EEmotion ) )
		if chatObjParsers.reTpl :
			tpls.append( ( chatObjParsers.reTpl, EItem ) )
		if chatObjParsers.reTpl:
			tpls.append( ( chatObjParsers.reTpl, LItem  ) )
		self.setEscTemplates( tpls )


# --------------------------------------------------------------------
# ����Ԫ��
# --------------------------------------------------------------------

class EEmotion( BaseElement, FaceIcon ) :
	def __init__( self, start, text ) :
		BaseElement.__init__( self, start, text )
		path, dsp = emotionParser.getEmotion( text )
		FaceIcon.__init__( self )
		self.focus  = False
		self.crossFocus = False
		self.update( Emote( text,path, dsp ) )
		self.play()


# --------------------------------------------------------------------
# ��ƷԪ��
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
		���� pyRich �����ԣ������ı�����
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
	def getInst( start, text ) :
		"""
		�Ƿ���Ч
		"""
		viewTextInfo = chatObjParsers.getViewObj( text )
		if viewTextInfo is None : return None
		viewText, color = viewTextInfo
		pyItem = EItem( start, text )
		StaticText._setColor( pyItem, color )
		pyItem.text = viewText
		return pyItem

	# -------------------------------------------------
	def getWViewText( self, scope = None ) :
		"""
		��ȡ�����ı�
		"""
		if scope is None :
			return self.wtext
		elif scope[0] < self.end and scope[1] > self.start :
			return self.wtext
		return csstring.toWideString( "" )

	# ---------------------------------------
	def getViewLen( self ) :
		"""
		��ȡ�����ı����ַ���
		"""
		return self.length

	def getWViewLen( self ) :
		"""
		��ȡ�����ı�������
		"""
		return self.wlength


# --------------------------------------------------------------------
# ����Ԫ��
# --------------------------------------------------------------------
class LItem( BaseElement, StaticText ) :
	def __init__( self, start, text ) :
		BaseElement.__init__( self, start, text )
		StaticText.__init__( self )


	# ----------------------------------------------------------------
	# protect
	# ----------------------------------------------------------------
	def setAttributes_( self, pyRich ) :
		"""
		���� pyRich �����ԣ������ı�����
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
	def getInst( start, text ) :
		"""
		�Ƿ���Ч
		"""
		viewTextInfo = chatObjParsers.getViewObj( text )
		if viewTextInfo is None : return None
		viewText, color = viewTextInfo
		pyItem = LItem( start, text )
		StaticText._setColor( pyItem, color )
		pyItem.text = viewText
		return pyItem

	# -------------------------------------------------
	def getWViewText( self, scope = None ) :
		"""
		��ȡ�����ı�
		"""
		if scope is None :
			return self.wtext
		elif scope[0] < self.end and scope[1] > self.start :
			return self.wtext
		return csstring.toWideString( "" )

	# ---------------------------------------
	def getViewLen( self ) :
		"""
		��ȡ�����ı����ַ���
		"""
		return self.length

	def getWViewLen( self ) :
		"""
		��ȡ�����ı�������
		"""
		return self.wlength
