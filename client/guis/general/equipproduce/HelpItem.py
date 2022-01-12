# -*- coding: gb18030 -*-

"""
implement RespondItem class
"""

from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.ListItem import SingleColListItem
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font

class HelpItem( SingleColListItem ):
	def __init__( self, item ):
		item.lbText.text = ""
		SingleColListItem.__init__( self, item )
		self.width = 130.0
		self.pyRichText_ = CSRichText( item.rtText )
		self.pyRichText_.opGBLink = True
		self.pyRichText_.maxWidth = 100
		self.highlightForeColor = ( 0, 255, 0, 255 )
		self.selectedForeColor = ( 0, 255, 0, 255 )
		self.__pyMark = PyGUI( item.outMark )
		self.__pyMark.visible = True
		self.__pyMark.mark = 0
		#self.disableForeColor = ( 0, 255, 0, 255 )
		self.__text = ""

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
		self.pyRichText_.foreColor = ( 0, 255, 255, 255 )	# wsf,设置文本的初始颜色
		self.pyRichText_.text = text
		self.height = self.pyRichText_.bottom

	def _setMarkType( self, mark ):
		self.__pyMark.mark = mark

		util.setGuiState( self.__pyMark.getGui(), (1,25), mark )

	def _getMarkType( self ):
		return self.__pyMark.mark

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )
	mark = property( _getMarkType, _setMarkType )
