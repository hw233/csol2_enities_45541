# -*- coding: gb18030 -*-
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.StaticText import StaticText

class RatioItem( PyGUI ):
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pyStTitle = StaticText( item.quaText )
		self.__pyStTitle.text = ""
		self.__pyStRatio = StaticText( item.stRatio )
		self.__pyStRatio.text = ""

	def _getText( self ):
		return self.__pyStRatio.text

	def _setText( self, text ):
		self.__pyStRatio.text = text

	def _getTitle( self ):
		return self.__pyStTitle.text

	def _setTitle( self, title ):
		self.__pyStTitle.text = title
	
	def _getTitleColor( self ):
		return self.__pyStTitle.color
	
	def _setTitleColor( self, color ):
		self.__pyStTitle.color = color

	text = property( _getText, _setText )
	title = property( _getTitle, _setTitle )
	titleColor = property( _getTitleColor, _setTitleColor )