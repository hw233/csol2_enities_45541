# -*- coding: gb18030 -*-
#
# $Id: EquipItem.py,v 1.18 2008/08/29 02:39:57 huangyongwei Exp $

"""
implement equipment item class
"""

from guis import *
import BigWorld
from guis.common.PyGUI import PyGUI
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.general.StoreWindow.CompareDspItem import CompareDspItem
from guis.MLUIDefine import ItemQAColorMode
import csdefine
import GUIFacade
import ItemTypeEnum

class TargetEquipItem( PyGUI ):

	def __init__( self, eqItem, itemName ):
		PyGUI.__init__( self, eqItem )
#		self.dragFocus = False
#		self.dropFocus = False
		self.focus = True
		self.__pyItem = Item( eqItem.item, itemName )
		self.__pyItemBg = PyGUI( eqItem.itemBg )
		self.__pyItemBg.focus = False
		self.itemInfo = None

	def update( self, itemInfo, target ):
		self.__pyItem.update( itemInfo, target )
		self.itemInfo = itemInfo
		quality = itemInfo is None and 1 or itemInfo.quality
		util.setGuiState( self.__pyItemBg.getGui(), ( 4, 2 ), ItemQAColorMode[quality] )

	def clear( self ) :
		self.__pyItem.clear()
		self.itemInfo = None
		self.update( None, self.__pyItem.target )

class Item( CompareDspItem ) :
	def __init__( self, item, itemName ) :
		CompareDspItem.__init__( self, item )
		self.clear()
		self.__itemName = itemName
		self.dragFocus = False
		self.target = None

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDescriptionShow_( self ):	# 鼠标移动到item图标上，显示描述信息
		if self.itemInfo is None:
			selfDsp = self.__itemName
		else:
			item = self.itemInfo.baseItem
			self.description = item.description( self.target ) #获取物品的描述 BigWorld.player()是玩家entity,表示以谁来做为生成的描述
			#toolbox.infoTip.showItemTips( self, selfDsp )
		CompareDspItem.onDescriptionShow_( self )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo , target) :
		"""
		update item
		"""
		self.target = target
		CompareDspItem.update( self, itemInfo )


	def clear( self ) :
		CompareDspItem.clear( self )
		self.__itemInfo = None

	def onRClick_( self, mods ) :
		pass

	def onLClick_( self, mods ) :
		pass

	# ---------------------------------------
	def onDrop_( self, pyTarget, pyDroped ) :
		pass
