# -*- coding: gb18030 -*-

"""
implement RespondItem class
"""

from guis import *
from guis.controls.ListItem import SingleColListItem
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
import Font
# ----------------------------------------------------------------
# 调整属性字体尺寸修饰器
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

class deco_InitRichFont( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF, pyRichText ) :
		"""
		繁体任务对话选项字体
		"""
		pyRichText.charSpace = -1
		pyRichText.fontSize = 11

class RespondItem( SingleColListItem ):
	def __init__( self, item ):
		item.lbText.text = ""
		SingleColListItem.__init__( self, item )
		uiFixer.firstLoadFix( item )
		self.pyRichText_ = CSRichText( item.rtText )
		self.pyRichText_.opGBLink = True
		self.pyRichText_.limning = Font.LIMN_NONE
		self.pyRichText_.maxWidth = self.width
		self.pyRichText_.font = "MSYHBD.TTF"
		self.pyRichText_.fontSize = 12.0
		self.commonForeColor = ( 68, 141, 204, 255 )
		self.highlightForeColor = ( 0, 128, 0, 255 )
		self.selectedForeColor = ( 0, 128, 0, 255 )
		self.commonBackColor = ( 255, 255, 255, 0 )
		self.highlightBackColor = ( 255, 255, 255, 255 )
		self.selectedBackColor = ( 255, 255, 255, 255 )
		self.__text = ""
		self.__initRichFont( self.pyRichText_ )

	@deco_InitRichFont
	def __initRichFont( self, pyRichText ):
		pyRichText.charSpace = 0

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ):
		SingleColListItem.onStateChanged_( self, state )
		richSource = PL_Font.getSource( self.text, fc = self.foreColor )
		self.pyRichText_.text = richSource

	def onMouseLeave_( self ):
		self.selected = False
		SingleColListItem.onMouseLeave_( self )

	def _getText( self ):
		return self.__text

	def _setText( self, text ):
		self.__text = text
		self.pyRichText_.foreColor = ( 68, 141, 204, 255 )	# wsf,设置文本的初始颜色
		self.pyRichText_.text = text
		self.height = self.pyRichText_.bottom - 2.0

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )
