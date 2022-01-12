# -*- coding: gb18030 -*-

import GUI
from guis import *
from guis.common.FlexExWindow import HVFlexExWindow
from guis.common.PyGUI import PyGUI
import csdefine
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from ItemsFactory import ObjectItem as ItemInfo
from guis.MLUIDefine import ItemQAColorMode
from LabelGather import labelGather

class RewardDetails( HVFlexExWindow ):
	
	__instance = None
	itemwnd = ResMgr.openSection("guis/general/kitbag/subkitbag.gui")
	__maxSpace = 12		#创建格子数量

	def __init__( self ):
		assert RewardDetails.__instance is None, "RewardDetails instance has been created."
		RewardDetails.__instance = self
		wnd = GUI.load( RewardDetails.itemwnd )
		uiFixer.firstLoadFix( wnd )
		HVFlexExWindow.__init__( self, wnd )
		self.addToMgr( "rewardDetails" )
		self.activable_ = True
		self.escHide_ = True
		self.posZSegment = ZSegs.L4
		self.__pyItemsPanel = ItemPanel( RewardDetails.__maxSpace, wnd.itemsPanel )
		labelGather.setLabel( wnd.lbTitle, "SpaceCopyTBBattleRank:RewardDetails", "lbTitle")
		
	def __getEmptyItem( self ):
		return self.__pyItemsPanel.getEmptyItem()
		
	def __delItems( self ):
		"""
		更新物品图标为空
		"""
		self.__pyItemsPanel.delItems()
		
	def dispose( self ) :
		self.__pyItemsPanel.dispose()
		HVFlexExWindow.dispose( self )

	def show( self,rewards ):
		self.__delItems()
		for item in rewards:
			itemInfo = ItemInfo( item )	
			self.__getEmptyItem().update( itemInfo )
		HVFlexExWindow.show( self )

	def hide( self ):
		HVFlexExWindow.hide( self )
		
	@staticmethod
	def instance():
		if RewardDetails.__instance is None:
			RewardDetails.__instance = RewardDetails()
		return RewardDetails.__instance

class ItemPanel( PyGUI ):

	def __init__( self, maxSpace = 0, panel = None ):
		PyGUI.__init__( self, panel )
		self.__maxSpace = maxSpace
		self.itemsPanelItems = {}
		self.__initPanel( panel, maxSpace )

	def __initPanel( self, itemsPanel, maxSpace ):
			self.__pyItems = {}
			cols = csdefine.KB_MAX_COLUMN #设置背包的列数
			rows = maxSpace / cols
			for index in xrange( 0, maxSpace ): #创建物品格并排序
				item = GUI.load( "guis/general/spacecopyabout/spaceCopyTBBattle/rewardItem.gui" )
				uiFixer.firstLoadFix( item )
				pyItem = PyGUI( item )
				self.addPyChild( pyItem, "item_%d"%index )
				pyItem.left = ( pyItem.width ) * ( index % cols )
				pyItem.top = ( pyItem.height ) * ( index / cols )
				self.itemsPanelItems[index] = pyItem
			pyRightItem = self.itemsPanelItems[cols - 1] #背包的最右边格子
			pyBottomItem = self.itemsPanelItems[maxSpace - 1] #背包的最下边格子
			self.width = pyRightItem.right#设置背包panel的宽
			self.height = pyBottomItem.bottom #设置背包panel的长
			self.pyTopParent.height = self.bottom + 25.0
			self.center = self.pyTopParent.width/2.0	
			for name, item in itemsPanel.children: #往物品格里添加物品和蒙皮
				if "item_" not in name : continue  #主要起筛选作用，防止itemsPanel里面有其它孩子
				index = int( name.split( "_" )[1] )
				if index in xrange( maxSpace ):
					pyItem = ObjectItem( item, index )
					pyItem.focus = True
					self.__pyItems[index] = pyItem

	def delItems( self ):
		"""
		更新物品图标为空wsf
		"""
		for item in self.__pyItems.itervalues():
			item.update( None )

	def getEmptyItem( self ):
		pyItem_ = None
		indexList = self.__pyItems.keys()
		indexList.sort()
		for index in indexList:
			if self.__pyItems[index].itemInfo == None:
				pyItem_ = self.__pyItems[index]
				return pyItem_
		return pyItem_

	def dispose( self ):
		for i in self.__pyItems.itervalues():
			i.dispose()
		self.__pyItems = {}
		PyGUI.dispose( self )
		
class ObjectItem( PyGUI ):
	def __init__( self, item, index ):
		PyGUI.__init__( self, item )
		self.dragFocus = False
		self.dropFocus = False
		self.focus = True
		
		self.__pyLockIcon = PyGUI( item.lockIcon )
		self.__pyLockIcon.visible = False
		
		self.__pyItem = BOItem( item.item, self )
		self.__pyItem.index = index
		self.__pyItem.focus = False
		self.__pyItem.dragFocus = False
		self.__pyItem.dropFocus = False
		self.itemInfo = None
		
	def __setItemQuality( self, itemBg, quality ):
		util.setGuiState( itemBg, ( 4, 2 ), ItemQAColorMode[quality] )
		
	def dispose( self ) :
		self.__pyItem.dispose()
		PyGUI.dispose( self )

	def update( self, itemInfo ):
		self.__pyItem.update( itemInfo )
		self.itemInfo = itemInfo
		if itemInfo is not None :
			quality = itemInfo.quality
			isBinded = itemInfo.baseItem.isBinded()
			self.__pyLockIcon.visible = isBinded
			self.__setItemQuality( self.getGui(), quality )
		else:
			self.__pyLockIcon.visible = False
			self.__setItemQuality( self.getGui(), 1 )
