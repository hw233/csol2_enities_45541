# -*- coding: gb18030 -*-
#
# $Id: YuanBaoPanel.py, fangpengjun Exp $

"""
implement goods panel class

"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.controls.ODPagesPanel import ODPagesPanel
import csdefine

class TranstPanel( TabPanel ):
	
	bill_viewCount = 12
	
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.sortByOrder = False
		self.sortByUnPrice = False
		self.sortByTotalNum = False
		self.sortByTime = False
		self.pyTaxBtns = {}
		for name, item in panel.children:
			if not name.startswith( "colBtn_" ):continue
			index = int( name.split( "_" )[1] )
			pyTaxBtn = HButtonEx( item )
			pyTaxBtn.setExStatesMapping( UIState.MODE_R3C1 )
			pyTaxBtn.isSort = True
			labelGather.setPyBgLabel( pyTaxBtn, "SpecialShop:TranstPanel", name )
			pyTaxBtn.charSpace = -2
			pyTaxBtn.index = index
			self.pyTaxBtns[index] = pyTaxBtn
			pyTaxBtn.onLClick.bind( self.__onSortByIndex )
		
		self.pyPagesPanel_ = ODPagesPanel( panel.itemsPanel, panel.pgIdxBar )
		self.pyPagesPanel_.selectable = True
		self.pyPagesPanel_.btnsCheck = False
		self.pyPagesPanel_.onViewItemInitialized.bind( self.__initOrderItem )
		self.pyPagesPanel_.onDrawItem.bind( self.__drawOrderItem )
		self.pyPagesPanel_.viewSize = 10, 1
		
		self.pyBtnFresh_ = HButtonEx( panel.btnFresh )
		self.pyBtnFresh_.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnFresh_, "SpecialShop:ybPanel", "btnFresh" )
		labelGather.setLabel( panel.stPages, "SpecialShop:main", "page" )

	def __initOrderItem( self, pyViewItem ):
		pyOrder = OrderItem( )
		pyViewItem.addPyChild( pyOrder )
		pyViewItem.crossFocus = True
		pyOrder.pos = 2, 1
		pyViewItem.pyItem = pyOrder
		pyViewItem.visible = False
	
	def __drawOrderItem( self, pyViewItem ):
		pyItem = getattr( pyViewItem, "pyItem", None )
		if pyItem is not None :
			pyItem.setOrderInfo( pyViewItem )
		curPageIndex = self.pyPagesPanel_.pageIndex
		totalPageIndex = self.pyPagesPanel_.maxPageIndex
#		self.pyStPages_.text = "%d/%d"%( curPageIndex + 1, totalPageIndex + 1 )

	def __onSortByIndex( self, pyTaxBtn ):
		if pyTaxBtn is None:return
		index = pyTaxBtn.index
		sortsMap = {0: self.__sortByOrder,
					1: self.__sortByUnitprice,
					2: self.__sortByTotalNum,
					3: self.__sortByRemainTime,
				}
		sortsMap[index]()
	
	def __sortByOrder( self ):
		"""
		订单号排序
		"""
		flag = self.sortByOrder and True or False
		self.pyPagesPanel_.sort( key = lambda item : item[1], reverse = flag )
		self.sortByOrder = not self.sortByOrder
	
	def __sortByUnitprice( self ):
		"""
		单价排序
		"""
		flag = self.sortByUnPrice and True or False
		self.pyPagesPanel_.sort( key = lambda item : item[-1], reverse = flag )
		self.sortByUnPrice = not self.sortByUnPrice
	
	def __sortByTotalNum( self ):
		"""
		元宝总数
		"""
		flag = self.sortByTotalNum and True or False
		self.pyPagesPanel_.sort( key = lambda item : item[3], reverse = flag )
		self.sortByTotalNum = not self.sortByTotalNum

	def __sortByRemainTime( self ):
		"""
		剩余时间
		"""
		flag = self.sortByTime and True or False
		self.pyPagesPanel_.sort( key = lambda item : item[3], reverse = flag )
		self.sortByTime = not self.sortByTime
	
	def onLeaveWorld( self ):
		self.pyPagesPanel_.clearItems()
	
	def onHide( self ):
		self.pyPagesPanel_.clearItems()
	
# ----------------------------------------------------------------
from TranstBox import BuyBox
# 元宝寄售界面
class SellPanel( TranstPanel ):
	def __init__( self, panel ):
		TranstPanel.__init__( self, panel )
		self.lastRefTime = 0.0
		self.__triggers = {}
		self.__registerTriggers()
		self.pyPagesPanel_.onItemSelectChanged.bind( self.__onItemSelected )
		self.pyPagesPanel_.pyBtnDec.enable = True
		self.pyPagesPanel_.pyBtnDec.onLClick.bind( self.__onQueryFrontPage )
		self.pyPagesPanel_.pyBtnInc.enable = True
		self.pyPagesPanel_.pyBtnInc.onLClick.bind( self.__onQueryNextPage )

		self.__pyBtnBuy = HButtonEx( panel.btnBuy )
		self.__pyBtnBuy.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnBuy.enable = False
		labelGather.setPyBgLabel( self.__pyBtnBuy, "SpecialShop:ybPanel", "btnBuy" )
		self.__pyBtnBuy.onLClick.bind( self.__onBuy )
		self.pyBtnFresh_.onLClick.bind( self.__onFreshSellList )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_YBT_SHOW_SELL_BILL_INFO"] = self.__onRecSellBill
		self.__triggers["EVT_ON_YBT_ENABLE_BUY"] = self.__onShowBuyBox
		self.__triggers["EVT_ON_YBT_BUY_YUANBAO"] = self.__onHideBuyBox
		self.__triggers["EVT_ON_YBT_UPDATE_SELL_BILL"] = self.__onUpdateBill
		self.__triggers["EVT_ON_YBT_DELETE_SELL_BILL"] = self.__onDelBill
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
	# ------------------------------------------------------------
	def __onRecSellBill( self, bills ):
		"""
		接收订单信息
		"""
		self.pyPagesPanel_.clearItems()
		for bill in bills:
			if not bill in self.pyPagesPanel_.items and bill[3] > 0:
				self.pyPagesPanel_.addItem( bill )
		curPageIndex = self.pyPagesPanel_.pageIndex
		totalPageIndex = self.pyPagesPanel_.maxPageIndex
#		self.pyStPages_.text = "%d/%d"%( curPageIndex + 1, totalPageIndex + 1 )
#		self.pyPagesPanel_.pyBtnInc.enable = len( self.pyPagesPanel_.items ) >= self.bill_viewCount
	
	def __onShowBuyBox( self, tick, uid ):
		"""
		弹出元宝购买框
		"""
		buyBill = None
		for bill in self.pyPagesPanel_.items:
			if bill[0] == tick and bill[1] == uid:
				buyBill = bill
				break
		if buyBill:
			BuyBox.instance().show( buyBill, self )
	
	def __onHideBuyBox( self ):
		"""
		关闭元宝购买框
		"""
		BuyBox.instance().hide()
		
	def __onUpdateBill( self, tick, uid, deposit ):
		"""
		更新订单信息
		"""
		for index, bill in enumerate( self.pyPagesPanel_.items ):
			if bill[0] == tick and bill[1] == uid:
				bill[3] = deposit
				self.pyPagesPanel_.updateItem( index, bill )
				break
	
	def __onDelBill( self, tick, uid ):
		"""
		删除订单
		"""
		for bill in self.pyPagesPanel_.items:
			if bill[0] == tick and bill[1] == uid:
				self.pyPagesPanel_.removeItem( bill )
		
	def __onFreshSellList( self ):
		if time.time() - self.lastRefTime >= 10.0:
			self.lastRefTime = time.time()
			self.pyPagesPanel_.clearItems()
			curPageIndex = self.pyPagesPanel_.pageIndex
			BigWorld.player().getSellBillsInfo( curPageIndex + 1, self.bill_viewCount )
		else:
			showAutoHideMessage( 3.0, labelGather.getText( "SpecialShop:DetailsPanel", "freshWarning" ),"", MB_OK, pyOwner = self )
			return
	
	def __onItemSelected( self, index ):
		self.__pyBtnBuy.enable = index != -1
	
	def __onBuy( self ):
		selItem = self.pyPagesPanel_.selItem
		if selItem is None:return
		tick = selItem[0]
		uid = selItem[1]
		BigWorld.player().buyYBRequest( tick, uid )

	def __onQueryFrontPage( self ):
		pageIndex = self.pyPagesPanel_.pageIndex
		BigWorld.player().getSellBillsInfo( pageIndex, self.bill_viewCount )
	
	def __onQueryNextPage( self ):
		pageIndex = self.pyPagesPanel_.pageIndex
		BigWorld.player().getSellBillsInfo( pageIndex + 1, self.bill_viewCount )
	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )
	
	def onSelected( self ):
		if not rds.statusMgr.isInWorld():return
		self.pyPagesPanel_.clearItems()
		curPageIndex = self.pyPagesPanel_.pageIndex
		BigWorld.player().getSellBillsInfo( curPageIndex + 1, self.bill_viewCount )
	
	def onLeaveWorld( self ):
		TranstPanel.onLeaveWorld( self )
		self.lastRefTime = 0.0

# ----------------------------------------------------------------
from TranstBox import SellBox
# 元宝求购界面
class BuyPanel( TranstPanel ):
	def __init__( self, panel ):
		TranstPanel.__init__( self, panel )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyBtnSell = HButtonEx( panel.btnSell )
		self.__pyBtnSell.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSell.enable = False
		self.lastRefTime = 0.0
		labelGather.setPyBgLabel( self.__pyBtnSell, "SpecialShop:ybPanel", "btnSell" )
		self.__pyBtnSell.onLClick.bind( self.__onSell )
		
		self.pyBtnFresh_.onLClick.bind( self.__onFreshBuyList )
		self.pyPagesPanel_.onItemSelectChanged.bind( self.__onItemSelected )
		self.pyPagesPanel_.pyBtnDec.enable = True
		self.pyPagesPanel_.pyBtnDec.onLClick.bind( self.__onQueryFrontPage )
		self.pyPagesPanel_.pyBtnInc.enable = True
		self.pyPagesPanel_.pyBtnInc.onLClick.bind( self.__onQueryNextPage )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_YBT_SHOW_BUY_BILL_INFO"] = self.__onRecBuyBill
		self.__triggers["EVT_ON_YBT_ENABLE_SELL"] = self.__onShowSellBox
		self.__triggers["EVT_ON_YBT_SELL_YUANBAO"] =self.__onHideSellBox
		self.__triggers["EVT_ON_YBT_UPDATE_BUY_BILL"] = self.__onUpdateBill
		self.__triggers["EVT_ON_YBT_DELETE_BUY_BILL"] = self.__onDelBill
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
	# ------------------------------------------------------------------
	def __onRecBuyBill( self, bills ):
		self.pyPagesPanel_.clearItems()
		for bill in bills:
			if not bill in self.pyPagesPanel_.items and bill[3] > 0:
				self.pyPagesPanel_.addItem( bill )
		curPageIndex = self.pyPagesPanel_.pageIndex
		totalPageIndex = self.pyPagesPanel_.maxPageIndex
		self.pyStPages_.text = "%d/%d"%( curPageIndex + 1, totalPageIndex + 1 )
#		self.pyPagesPanel_.pyBtnInc.enable = len( self.pyPagesPanel_.items ) >= self.bill_viewCount
	
	def __onShowSellBox( self, tick, uid ):
		"""
		弹出出售元宝框
		"""
		sellBill = None
		for bill in self.pyPagesPanel_.items:
			if bill[0] == tick and bill[1] == uid:
				sellBill = bill
				break
		if sellBill:
			SellBox.instance().show( sellBill, self )
	
	def __onHideSellBox( self ):
		"""
		关闭出售元宝框
		""" 
		SellBox.instance().hide()

	def __onUpdateBill( self, tick, uid, deposit ):
		"""
		更新某个订单
		"""
		for index, bill in enumerate( self.pyPagesPanel_.items ):
			if bill[0] == tick and bill[1] == uid:
				bill[3] = deposit
				self.pyPagesPanel_.updateItem( index, bill )
				break
	
	def __onDelBill( self, tick, uid ):
		"""
		删除订单
		"""
		for bill in self.pyPagesPanel_.items:
			if bill[0] == tick and bill[1] == uid:
				self.pyPagesPanel_.removeItem( bill )
	
	def __onFreshBuyList( self ):
		if time.time() - self.lastRefTime >= 10.0:
			self.lastRefTime = time.time()
			self.pyPagesPanel_.clearItems()
			curPageIndex = self.pyPagesPanel_.pageIndex
			BigWorld.player().getBuyBillsInfo( curPageIndex + 1, self.bill_viewCount )
		else:
			showAutoHideMessage( 3.0, labelGather.getText( "SpecialShop:DetailsPanel", "freshWarning" ), "", MB_OK, pyOwner = self )
			return
	
	def __onItemSelected( self, index ):
		self.__pyBtnSell.enable = index != -1
	
	def __onSell( self ):
		"""
		出售元宝请求
		"""
		orderItem = self.pyPagesPanel_.selItem
		if orderItem is None:return 
		tick = orderItem[0]
		uid = orderItem[1]
		BigWorld.player().sellYBRequest( tick, uid )
	
	def __onQueryFrontPage( self ):
		pageIndex = self.pyPagesPanel_.pageIndex
		BigWorld.player().getBuyBillsInfo( pageIndex, self.bill_viewCount )

	def __onQueryNextPage( self ):
		pageIndex = self.pyPagesPanel_.pageIndex
		BigWorld.player().getBuyBillsInfo( pageIndex + 1, self.bill_viewCount )

	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )
	
	def onSelected( self ):
		if not rds.statusMgr.isInWorld():return
		self.pyPagesPanel_.clearItems()
		curPageIndex = self.pyPagesPanel_.pageIndex
		BigWorld.player().getBuyBillsInfo( curPageIndex + 1, self.bill_viewCount )

	def onLeaveWorld( self ):
		TranstPanel.onLeaveWorld( self )
		self.lastRefTime = 0.0

# ----------------------------------------------------------------
# 元宝订单控件
from guis.controls.ListItem import MultiColListItem
from Time import Time
class OrderItem( MultiColListItem ):
	_ITEM = None
	def __init__( self ):
		if OrderItem._ITEM is None :
			OrderItem._ITEM = GUI.load( "guis/general/specialshop/orderitem.gui" )
			uiFixer.firstLoadFix( OrderItem._ITEM )
		item = util.copyGuiTree( OrderItem._ITEM )
		MultiColListItem.__init__( self, item )
		self.setTextes( "", "", "", "" )
		self.commonBackColor = ( 255, 255, 255, 0 )
		self.selectedBackColor = ( 118, 111, 67, 0 )
		self.highlightBackColor = ( 118, 111, 67, 0 )
		self.focus = False
	
	def __getRemainText( self, remainTime ):
		remainDays = remainTime/( 24*3600 )
		remainHours = ( remainTime%( 24*3600 ) )/3600
		remainMins = ( ( remainTime%( 24*3600 ) )%3600 )/60
		remianText = ""
		if int( remainDays ) >0:
			remianText = labelGather.getText( "SpecialShop:TranstPanel","remainDays" )%( remainDays, remainHours )
		else:
			if remainHours >0:
				remianText = labelGather.getText( "SpecialShop:TranstPanel","remainHours" )%( remainHours, remainMins )
			else:
				remianText = labelGather.getText( "SpecialShop:TranstPanel","remainMins" )% remainMins
		return remianText
	
	def setOrderInfo( self, pyViewItem ):
		"""
		更新订单信息
		"""
		bill = pyViewItem.pageItem
		pyViewItem.visible = bill is not None
		pyViewItem.crossFocus = bill is not None
		pyViewItem.focus = bill is not None
		orderNumber = ""
		unitPrice = ""
		goldNumber = ""
		remainText = ""
		if bill:
			orderNumber = str( bill[1] )
			unitPrice = str( bill[4] )
			goldNumber = str( bill[3]*100 )
			remainTime = int( bill[1]/1000 ) + 259200 - Time.time()
			remainText = self.__getRemainText( remainTime )
		self.selected = pyViewItem.selected
		if pyViewItem.selected :
			self.setState( UIState.SELECTED )
		elif self.isMouseHit() :
			self.setState( UIState.HIGHLIGHT )
		else :
			self.setState( UIState.COMMON )
		self.setTextes( orderNumber, unitPrice, goldNumber, remainText )
