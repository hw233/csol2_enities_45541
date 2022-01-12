# -*- coding: gb18030 -*-
#
# $Id: ItemsPanel.py,v 1.3 2008-09-05 08:05:00 fangpengjun Exp $

from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.UIStatesTab import HStatesTabEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.controls.ODComboBox import ODComboBox
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.controls.BaseObjectItem import BaseObjectItem
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Align import PL_Align
from ItemsFactory import ObjectItem
from config.client.msgboxtexts import Datas as mbmsgs
from LabelGather import labelGather
from guis.MLUIDefine import QAColor, ItemQAColorMode


class BaseItemsPanel( TabPanel ):

	def __init__( self, tabPanel, pyBinder = None ):
		TabPanel.__init__( self, tabPanel, pyBinder )

		self.pyMsgBox_ = None
		self.sortHandlerMap_ = {}
		self.triggers_ = {}
		self.registerTriggers_()
		self.initialize_( tabPanel )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.triggers_.iterkeys() :
			ECenter.unregisterEvent( key, self )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initialize_( self, tabPanel ) :
		self.initPagesPanel_( tabPanel )

		self.pyItemsAmount_ = StaticText( tabPanel.stNumber )
		self.pyItemsAmount_.text = "0"

		self.initSortBox_( tabPanel.sortComBox )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( tabPanel.sortText, "vendwindow:BaseItemsPanel", "stSortText" )
		labelGather.setLabel( tabPanel.numberText, "vendwindow:BaseItemsPanel", "stNumberText" )

	def initPagesPanel_( self, tabPanel, viewSize = ( 6, 2 ) ) :
		self.pyPagesPanel_ = ODPagesPanel( tabPanel.clipPanel, tabPanel.ctrlBar )
		self.pyPagesPanel_.onViewItemInitialized.bind( self.initItem_ )
		self.pyPagesPanel_.onItemRClick.bind( self.onItemRClick_ )
		self.pyPagesPanel_.onDrawItem.bind( self.drawItem_ )
		self.pyPagesPanel_.viewSize = viewSize
		self.pyPagesPanel_.selectable = True


	def initSortBox_( self, comboBox ) :
		"""
		初始化排序控件
		"""
		tempMap = (
					( 0, "type", self.sortByType_ ),
					( 1, "quality", self.sortByQuality_ ),
					( 2, "price", self.sortByPrice_ ),
					( 3, "level", self.sortByLevel_ ),
					)
		self.sortBox_ = ODComboBox( comboBox )
		self.sortBox_.onItemLClick.bind( self.onSort_ )
		self.sortBox_.pyBox.text = labelGather.getText( "vendwindow:BaseItemsPanel", "option" )
		for index, sortText, handler in tempMap :
			self.sortBox_.addItem( labelGather.getText( "vendwindow:BaseItemsPanel", sortText ) )
			self.sortHandlerMap_[index] = handler

	def registerTriggers_( self ) :
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	# sort function
	# -------------------------------------------------
	def onSort_( self, index ) :
		handler = self.sortHandlerMap_[ index ]
		self.pyPagesPanel_.sort( cmp = handler )

	def sortByType_( self, item1, item2 ) :
		"""
		按类型排序
		"""
		if item1.id != item2.id :
			return cmp( item1.id, item2.id )
		else :
			return cmp( item1.baseItem.isBinded(), item2.baseItem.isBinded() )

	def sortByQuality_( self, item1, item2 ) :
		"""
		按品质从高到低排序；同品质按等级从高到低排序；同品质、等级，按id排序。
		"""
		if item1.quality != item2.quality :
			return cmp( item2.quality, item1.quality )					# 先按品质排序
		elif item1.level != item2.level :
			return cmp( item2.level, item1.level )						# 同品质按等级排序
		elif item1.id != item2.id :
			return cmp( item1.id, item2.id )
		else :
			return cmp( item1.baseItem.isBinded(), item2.baseItem.isBinded() )

	def sortByPrice_( self, item1, item2 ) :
		"""
		按价格从高到低排序；同价格按等级从高到低排序；同价格、等级，按id排序。
		"""
		if item1.rolePrice != item2.rolePrice :									# 先按价格排序
			return cmp( item2.rolePrice, item1.rolePrice )
		elif item1.quality != item2.quality :
			return cmp( item2.quality, item1.quality )					# 同价格按品质排序
		elif item1.level != item2.level :
			return cmp( item2.level, item1.level )						# 同品质按等级排序
		elif item1.id != item2.id :
			return cmp( item1.id, item2.id )
		else :
			return cmp( item1.baseItem.isBinded(), item2.baseItem.isBinded() )

	def sortByLevel_( self, item1, item2 ) :
		"""
		按等级从高到低排序；同等级按品质从高到低排序；同等级、品质，按id排序。
		"""
		if item1.level != item2.level :
			return cmp( item2.level, item1.level )						# 先按等级排序
		elif item1.quality != item2.quality :
			return cmp( item2.quality, item1.quality )					# 同等级按品质排序
		elif item1.id != item2.id :
			return cmp( item1.id, item2.id )
		else :
			return cmp( item1.baseItem.isBinded(), item2.baseItem.isBinded() )

	# -------------------------------------------------
	def initItem_( self, pyViewItem ) :
		"""
		初始化添加的技能列表项
		"""
		pyBuyItem = VendBuyItem()
		pyViewItem.pyBuyItem = pyBuyItem
		pyViewItem.addPyChild( pyBuyItem )
		pyBuyItem.left = 2
		pyBuyItem.top = 0

	def drawItem_( self, pyViewItem ) :
		"""
		"""
		pyBuyItem = pyViewItem.pyBuyItem
		pyBuyItem.update( pyViewItem )

	def onItemRClick_( self, pyViewItem ) :
		pass

	def onRemoveItem_( self, uid ):
		for itemInfo in self.pyPagesPanel_.items:
			if itemInfo.baseItem.uid == uid:
				self.pyPagesPanel_.removeItem( itemInfo )
				break
		self.pyItemsAmount_.text = str( self.pyPagesPanel_.itemCount )


	# ------------------------------------------------------------
	# public
	# ------------------------------------------------------------
	def showMsg( self, msg, style = MB_OK, callback = lambda res : False ) :
		def callback_inline( res ) :
			self.pyMsgBox_ = None
			callback( res )
		if self.pyMsgBox_ is not None :
			self.pyMsgBox_.hide()
		self.pyMsgBox_ = showMessage( msg, "", style, callback_inline, self.pyTopParent )

	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.triggers_[eventMacro]( *args )

	def reset( self ):
		self.pyPagesPanel_.clearItems()
		self.pyItemsAmount_.text = str( self.pyPagesPanel_.itemCount )



class BuyItemsPanel( BaseItemsPanel ):

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ):
		self.triggers_["EVT_ON_VEND_RECEIVE_VEND_ITEMS"] = self.__onReceiveItems
		self.triggers_["EVT_ON_VEND_ITEM_SELLED"] = self.onRemoveItem_ 			# 卖出物品回调
		BaseItemsPanel.registerTriggers_( self )

	def onItemRClick_( self, pyViewItem ) :
		"""
		右击表示欲购买该物品
		"""
		itemInfo = pyViewItem.pageItem
		if itemInfo is None : return
		self.pyPagesPanel_.selIndex = pyViewItem.itemIndex
		def query( rs_id ) :
			if rs_id == RS_OK :
				player = BigWorld.player()
				player.vend_buy( itemInfo.uid, player.sellerID )
		moneyStr = utils.currencyToViewText( itemInfo.rolePrice, False )
		# "你要花费%s购买%s个%s么?"
		msg = mbmsgs[0x0a61] % ( moneyStr, itemInfo.amount, itemInfo.name() )
		self.showMsg( msg, MB_OK_CANCEL, query )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onReceiveItems( self, itemList ):
		self.pyPagesPanel_.clearItems()
		for baseItem in itemList :
			itemInfo = ObjectItem( baseItem )
			itemInfo.rolePrice = itemInfo.price
			self.pyPagesPanel_.addItem( itemInfo )
		self.pyItemsAmount_.text = str( self.pyPagesPanel_.itemCount )



class VendBuyItem( HStatesTabEx ) :

	__ITEM = None

	def __init__( self, item = None, pyBinder = None ) :
		if item is None :
			if VendBuyItem.__ITEM is None :
				VendBuyItem.__ITEM = GUI.load( "guis/general/vendwindow/buywindow/buygoodsitem.gui" )
				uiFixer.firstLoadFix( VendBuyItem.__ITEM )
			item = util.copyGuiTree( VendBuyItem.__ITEM )
		HStatesTabEx.__init__( self, item )
		self.setExStatesMapping( UIState.MODE_R2C1 )

		self.initialize_( item )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initialize_( self, item ) :
		self.__pyName = CSRichText( item.rt_resume1 )
		self.__pyName.foreColor = ( 236, 218, 157, 255 )
		self.__pyCost = CSRichText( item.rt_resume2 )
		self.__pyCost.align = "R"
		self.__pyItem = BaseObjectItem( item.item.item )
		self.__pyItem.focus = False
		self.__pyItem.dragMark = DragMark.VEND_BUY_WND


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, pyViewItem ) :
		itemInfo = pyViewItem.pageItem
		self.__pyItem.update( itemInfo )
		if itemInfo is None :
			self.__pyName.text = ""
			self.__pyCost.text = ""
			util.setGuiState( self.gui.item, ( 4, 2 ), ItemQAColorMode[0] )
			pyViewItem.focus = False
		else :
			costStr =  utils.currencyToViewText( itemInfo.rolePrice )
			QALVColor = QAColor[ itemInfo.quality ]
			self.__pyName.text = PL_Font.getSource( itemInfo.name(), fc = QALVColor )
			priceColor = itemInfo.rolePrice> BigWorld.player().money and ( 255,0,0,255 ) or ( 16, 197, 165, 255 )
			self.__pyCost.text = PL_Align.getSource( lineFlat = "M" ) + PL_Font.getSource( costStr, fc = priceColor )
			util.setGuiState( self.gui.item, ( 4, 2 ), ItemQAColorMode[itemInfo.quality] )
			pyViewItem.focus = True
		if pyViewItem.selected or pyViewItem.highlight :
			self.setStateView_( UIState.HIGHLIGHT )
		else :
			self.setStateView_( UIState.COMMON )

	@property
	def pyItem( self ) :
		return self.__pyItem