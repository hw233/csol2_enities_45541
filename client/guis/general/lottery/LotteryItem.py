# -*- coding: gb18030 -*-
#

import Font
from guis import *
from guis.controls.StaticText import StaticText
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.common.PyGUI import PyGUI
from LabelGather import labelGather
from guis.MLUIDefine import ItemQAColorMode

class LotteryItem( PyGUI):
	"""
	物品格UI
	"""

	def __init__(self, lottItem ):
		PyGUI.__init__( self, lottItem )
		self.focus = True
		lottItem.cdCover.visible = False
		self.__pyCover = PyGUI( lottItem.cover )
		self.__pyItem = BOItem( lottItem.item )
		self.__pyStAmount = StaticText( lottItem.item.lbAmount )
		self.__pyItem.visible = False
		self.__pyItem.dragFocus = False		#不能拖动
		self.__selected = False

	def __select( self ):
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		if self.__pyCover:
			self.__pyCover.visible = False

	def update( self, itemInfo ):
		"""
		更新ITEM的信息
		"""
		self.__pyItem.update( itemInfo )
		quality = itemInfo is None and 1 or itemInfo.quality
		util.setGuiState( self.getGui(), ( 4, 2 ), ItemQAColorMode[quality] )
		self.__pyItem.visible = True
		amount = itemInfo.amount
		if itemInfo.id == 60101001:	#金钱的数量显示是个特例,需要拆分成金银铜
			text = ""
			gold = amount / 10000
			argent = ( amount % 10000 ) / 100
			copper = amount % 100
			if gold > 0:
				text += labelGather.getText( "LotteryWindow:main", "miGold", gold )
			if argent > 0:
				text += labelGather.getText( "LotteryWindow:main", "miArgent", argent )
			if copper > 0:
				text += labelGather.getText( "LotteryWindow:main", "miCopper", copper )
			self.__pyStAmount.font = Font.defFont
			self.__pyItem.amountText = text

	def clearItem( self ):
		"""
		清除ITEM的信息
		"""
		self.__pyCover.visible = False
		self.__pyItem.visible = False
		self.__pyItem.update( None )

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected

	selected = property( _getSelected, _setSelected )