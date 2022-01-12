# -*- coding: gb18030 -*-
# $Id: IconChoiceWnd.py, fangpengjun Exp $

from guis import *
from guis.common.PyGUI import PyGUI
from LabelGather import labelGather

class TongIcon( PyGUI ):
	def __init__( self, tongIcon, type ):
		PyGUI.__init__( self, tongIcon )
		self.__pyIcon = Item( tongIcon.icon, self )
		self.__pyCover = PyGUI( tongIcon.cover )
		self.__pyCover.visible = False
		self.__selected = False
		self.index = -1
		self.type = type				# 区分哪些是本地图标，是系统经典还是推荐图标
		self.reqMoney = 0				# 使用该图标花费金钱

	def __select( self ):
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		if self.__pyCover:
			self.__pyCover.visible = False

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected

	def _getTexture( self ):
		return self.__pyIcon.texture

	def _setTexture( self, texture ):
		self.crossFocus = texture != ""
		if texture != "":
			util.setGuiState( self.getGui(), ( 2, 1 ), ( 1, 1 ) )
		else:
			util.setGuiState( self.getGui(), ( 2, 1 ), ( 2, 1 ) )
		self.__pyIcon.texture = texture

	selected = property( _getSelected, _setSelected )
	texture = property( _getTexture, _setTexture )

import event.EventCenter as ECenter
from guis import *
import BigWorld
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem

TONG_LOCAL_ICON		= 0
TONG_RECOM_ICON 	= 1
TONG_CLASSIC_ICON 	= 2

class Item( BOItem ):
	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.dragFocus = False
		self.selectable = True
		self.description = ""
		self.__initialize( item )

	def subclass( self, item ) :
		BOItem.subclass( self, item )
		self.__initialize( item )
		return True

	def __initialize( self, item ) :
		if item is None : return

	def onMouseEnter_( self ):
#		BOItem.onMouseEnter_( self )
		if self.texture != "":
#			toolbox.itemCover.highlightItem( self )
			if self.pyBinder.type == TONG_CLASSIC_ICON: #经典图标,显示花费
				toolbox.infoTip.showToolTips( self, labelGather.getText( "TongAbout:TongIcon", "infoTip", self.pyBinder.reqMoney/10000 ) )
			elif self.pyBinder.type == TONG_RECOM_ICON:
				toolbox.infoTip.showToolTips( self, labelGather.getText( "TongAbout:TongIcon", "freeTip" ) )
#		return True

	def onMouseLeave_( self ):
		BOItem.onMouseLeave_( self )
		toolbox.infoTip.hide()
		return True

	def onRClick_( self,mods ):
		BOItem.onRClick_( self, mods )
		return True

	def onLClick_( self, mods ):
		BOItem.onLClick_( self, mods )
		if self.texture == "":return
		index = self.pyBinder.index
		type = self.pyBinder.type
		if type == TONG_LOCAL_ICON:
			ECenter.fireEvent( "EVT_ON_TONGICON_SELECTED", index )
		elif type == TONG_RECOM_ICON:
			ECenter.fireEvent( "EVT_ON_RECOM_TONGICON_SELECTED", index )
		elif type == TONG_CLASSIC_ICON:
			ECenter.fireEvent( "EVT_ON_CLASSIC_TONGICON_SELECTED", index )
		return True
