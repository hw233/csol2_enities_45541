# -*- coding: gb18030 -*-

from guis import *
from guis.controls.ContextMenu import MenuItem
from guis.controls.StaticText import StaticText

class SpecMItem( MenuItem ):
	"""
	交流设置菜单
	"""
	def __init__( self, text ):
		item = GUI.load( "guis/general/playerinfo/specitem.gui" )
		uiFixer.firstLoadFix( item )
		MenuItem.__init__( self, MIStyle.COMMON, item )
		self.__initialize( item )
		self.text = text
		self.pyText_.color = ( 255, 252, 208, 255 )
		self.textColor = ( 255, 252, 208, 255 )

	def __initialize( self, item ):
		self.__pyLbValue = StaticText( item.lbValue )
		self.__pyLbValue.text = ""

	def _getTextValue( self ):
		return self.__pyLbValue.text

	def _setTextValue( self, text ):
		self.__pyLbValue.text = text
		self.__pyLbValue.left = self.pyText_.right + 2.0
		width = self.getRealWidth()
		self.width = width
		self.pyArrow_.right = self.right + 3.0
		if self.pySelfItems is not None :
			self.pySelfItems.onItemRewidth__( self )

	def __getArrowWidth( self ) :
		"""
		获取子菜单项箭头的大小
		"""
		if self.pyArrow_ and self.pySubItems.count :
			return self.pyArrow_.width
		return 0

	def getRealWidth( self ):
		stuffWidth = 0
		if self.pySelfItems is not None :
			for pyItem in self.pySelfItems :
				if pyItem.pyArrow_:
		 			stuffWidth = max( stuffWidth, pyItem.pyArrow_.width )
		else:
			stuffWidth = max( stuffWidth, self.__getArrowWidth() )
		if self.textValue == "":
			return self.pyText_.right + stuffWidth
		else:
			return self.__pyLbValue.right + stuffWidth

	def _getTextColor( self ):
		return self.__pyLbValue.color

	def _setTextColor( self, color ):
		self.__pyLbValue.color = color

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	textValue = property( _getTextValue, _setTextValue )
	textColor = property( _getTextColor, _setTextColor )