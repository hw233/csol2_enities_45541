# -*- coding: gb18030 -*-
#
# $Id: ItemsPanel.py,v 1.1 2008-08-14 10:20:10 fangpengjun Exp $

from guis import *
from guis.controls.TabCtrl import TabPanel
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from event.EventCenter import *
from WareItem import WareItem
from guis.controls.CheckBox import CheckBox
import GUIFacade

class ItemsPanel( TabPanel ):

	_item_dragMark = DragMark.NPC_TRADE_BUY
	_cc_row = 6
	_cc_col = 2
	_cc_defIndex = 1

	def __init__( self, type, tabPanel):
		TabPanel.__init__( self, tabPanel )
		self.focus = False
		self.dropFocus = False
		self.__type = type #商品类型
		self.__triggers = {}
		self.__registerTriggers()
		self.__itemInfos = []

		self.__pyForeBtn = Button( tabPanel.foreBtn )
		self.__pyForeBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyForeBtn.onLClick.bind( self.__onForePage)

		self.__pyNextBtn = Button( tabPanel.nextBtn )
		self.__pyNextBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyNextBtn.onLClick.bind( self.__onNextPage )

		self.__pyStPageIndex = StaticText( tabPanel.lbIndex )
		self.__pyStPageIndex.text = "1"

		self.__initItems( tabPanel )

	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_NEW_ITEM_INFO"] = self.__onNewItemInfo
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ):
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	# -----------------------------------------------------------------------------
	def __initItems( self, tabPanel ):
		self.__pyItems = {}
		for name, item in tabPanel.children:
			if "item_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyItem = WareItem( item, self._item_dragMark, self )
			pyItem.index = index
			self.__pyItems[index] = pyItem

	def __onForePage( self ): #前一页
		curIndex = int( self.__pyStPageIndex.text )
		if curIndex <= self._cc_defIndex:
			return
		pageIndex = curIndex - 1
		self.__showBuyItems( pageIndex )

	def __onNextPage( self ): #下一页
		curIndex = int( self.__pyStPageIndex.text )
		if curIndex >= self.__pagesNum:
			return
		pageIndex = curIndex + 1
		self.__showBuyItems( pageIndex )

	def __showBuyItems( self, pageIndex ):
		self.clearItems()
		self.__pyStPageIndex.text = str( pageIndex )
		startIndex = ( pageIndex - 1 )*( self._cc_row*self._cc_col )
		for infoIndex, infoTuple in enumerate( self.__itemInfos ):
			disIndex = infoIndex - startIndex
			if self.__pyItems.has_key( disIndex ):
				self.__pyItems[disIndex].update( infoTuple[0], infoTuple[1] )

	def __setPages( self, count ):
		pages = count/( self._cc_row*self._cc_col )
		remain = count%( self._cc_row*self._cc_col )
		if count != 0 and remain == 0:
			self.__pagesNum = pages
		else:
			self.__pagesNum = pages + 1

	def __onNewItemInfo( self, itemIndex ):
		if( itemIndex  - 1 )/14 +1 == int( self.__pyStPageIndex.text ): #如果新的物品在当前页面
			a = ( itemIndex%14 != 0 and [itemIndex%14] or [14] )[0]
			try:
				infoTuple = self.__itemInfos[itemIndex-1]
				self.__pyItems[a-1].update( infoTuple[0], infoTuple[1] )
			except:
				pass

	# --------------------------------------------------------
	# public
	# --------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def updateItem( self, index, itemInfo ):
		self.__itemInfos.append( ( index, itemInfo ) ) #保存商品的全局索引
		for pyItem in self.__pyItems.itervalues():
			if pyItem.itemInfo is None:
				pyItem.update( index, itemInfo )
				break
		count = GUIFacade.getInvoiceAmount( self.__type ) # 获得某类商品总数量
		self.__setPages( count )

	def showBuyItems( self ):
		self.__showBuyItems( self._cc_defIndex )

	def clearItems( self ):
		for index, item in self.__pyItems.iteritems():
			item.update( index, None )
#		fireEvent( "EVT_ON_ROLE_NEW_ITEM_INFO", len( self.__itemInfos ) )