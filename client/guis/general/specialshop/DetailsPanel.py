# -*- coding: gb18030 -*-
#
# $Id: DetailsPanel.py, fangpengjun Exp $

"""
implement goods panel class

"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.TabCtrl import TabPanel
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.controls.ODPagesPanel import ODPagesPanel
from config.client.msgboxtexts import Datas as mbmsgs

class DetailsPanel( TabPanel ):
	"""
	订单面板基类
	"""
	def __init__( self, panel, panelType ):
		TabPanel.__init__( self, panel )
		self.sortByOrder = False
		self.sortByType = False
		self.sortByYuanBao = False
		self.sortByUnPrice = False
		self.sortByTime = False
		self.pyTaxBtns = {}
		self.lastRefTime = 0.0
		
		for name, item in panel.children:
			if not name.startswith( "colBtn_" ):continue
			index = int( name.split( "_" )[1] )
			pyTaxBtn = HButtonEx( item )
			pyTaxBtn.setExStatesMapping( UIState.MODE_R3C1 )
			pyTaxBtn.isSort = True
			if index == 4:
				if panelType == 0:
					name = "colBtn_trade"
				else:
					name = "colBtn_release"
			labelGather.setPyBgLabel( pyTaxBtn, "SpecialShop:DetailsPanel", name )
			pyTaxBtn.charSpace = -2
			pyTaxBtn.index = index
			self.pyTaxBtns[index] = pyTaxBtn
			pyTaxBtn.onLClick.bind( self.__onSortByIndex )

		self.pyStPages_ = StaticText( panel.stPages )
		self.pyStPages_.text = ""
		
		self.pyPagesPanel_ = ODPagesPanel( panel.itemsPanel, panel.pgIdxBar )
		self.pyPagesPanel_.onViewItemInitialized.bind( self.__initDetailsItem )
		self.pyPagesPanel_.selectable = True
		self.pyPagesPanel_.viewSize = 10, 1
		
		self.pyBtnFresh_ = HButtonEx( panel.btnFresh )
		self.pyBtnFresh_.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.pyBtnFresh_, "SpecialShop:ybPanel", "btnFresh" )

	def __initDetailsItem( self, pyViewItem ):
		pyDetails = DetailsItem()
		pyViewItem.addPyChild( pyDetails )
		pyViewItem.crossFocus = True
		pyDetails.pos = 2, 1
		pyViewItem.pyItem = pyDetails
		pyViewItem.visible = False

	def __onSortByIndex( self, pyTaxBtn ):
		if pyTaxBtn is None:return
		index = pyTaxBtn.index
		sortsMap = {0: self.__sortByOrder,
					1: self.__sortByType,
					2: self.__sortByYuanBao,
					3: self.__sortByUnPrice,
					4: self.__sortByRemainTime,
				}
		sortsMap[index]()
	
	def __sortByOrder( self ):
		"""
		明细号排序
		"""
		flag = self.sortByOrder and True or False
		self.pyPagesPanel_.sort( key = lambda item : item[0], reverse = flag )
		self.sortByOrder = not self.sortByOrder
	
	def __sortByType( self ):
		"""
		明细类型
		"""
		flag = self.sortByType and True or False
		self.pyPagesPanel_.sort( key = lambda item : item[1], reverse = flag )
		self.sortByType = not self.sortByType
	
	def __sortByYuanBao( self ):
		"""
		元宝数量
		"""
		flag = self.sortByYuanBao and True or False
		self.pyPagesPanel_.sort( key = lambda item : item[4], reverse = flag )
		self.sortByYuanBao = not self.sortByYuanBao
	
	def __sortByUnPrice( self ):
		"""
		明细单价
		"""
		flag = self.sortByUnPrice and True or False
		self.pyPagesPanel_.sort( key = lambda item : item[3], reverse = flag )
		self.sortByUnPrice = not self.sortByUnPrice
	
	def __sortByRemainTime( self ):
		"""
		剩余时间
		"""
		flag = self.sortByTime and True or False
		self.pyPagesPanel_.sort( key = lambda item : item[-1], reverse = flag )
		self.sortByTime = not self.sortByTime
	
	def onHide( self ):
		self.pyPagesPanel_.clearItems()
		
	def onLeaveWorld( self ):
		self.pyPagesPanel_.clearItems()

class LogsPanel( DetailsPanel ):
	"""
	交易记录面板
	"""
	def __init__( self, panel ):
		DetailsPanel.__init__( self, panel, 0 )
		self.__triggers = {}
		self.__registerTriggers()
		self.pyPagesPanel_.onDrawItem.bind( self.__drawLogsItem )
		self.pyBtnFresh_.onLClick.bind( self.__onFresh )
		
	def __drawLogsItem( self, pyViewItem ):
		pyItem = getattr( pyViewItem, "pyItem", None )
		if pyItem is not None :
			pyItem.setLogs( pyViewItem )
		curPageIndex = self.pyPagesPanel_.pageIndex
		totalPageIndex = self.pyPagesPanel_.maxPageIndex
		self.pyStPages_.text = "%d/%d"%( curPageIndex + 1, totalPageIndex + 1 )
		
	# ------------------------------------------------------------
	# private
	# ------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_YBT_SHOW_MY_BILL_INFO"] = self.__onRecLogs

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )
	# -----------------------------------------------------------
	def __onRecLogs( self, logs ):
		"""
		订单记录
		"""
		for log in logs:
			if log[4] == 0:continue
			if not log in self.pyPagesPanel_.items:
				self.pyPagesPanel_.addItem( log )
		curPageIndex = self.pyPagesPanel_.pageIndex
		totalPageIndex = self.pyPagesPanel_.maxPageIndex
		self.pyStPages_.text = "%d/%d"%( curPageIndex + 1, totalPageIndex + 1 )
	
	def __onFresh( self ):
		"""
		刷新订单
		"""
		if time.time() - self.lastRefTime >= 10.0:
			self.lastRefTime = time.time()
			self.pyPagesPanel_.clearItems()
			BigWorld.player().getMyBillsInfo()
		else:
			showAutoHideMessage( 3.0, labelGather.getText( "SpecialShop:DetailsPanel", "freshWarning" ),"", MB_OK, pyOwner = self )
			return
			
	def onSelected( self ):
		"""
		请求交易记录
		"""
		BigWorld.player().getMyBillsInfo()

	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onHide( self ):
		DetailsPanel.onHide( self )
		
	def onLeaveWorld( self ):
		DetailsPanel.onLeaveWorld( self )

# ---------------------------------------------------------------------------------
class OperatePanel( DetailsPanel ):
	"""
	订单操作面板
	"""
	def __init__( self, panel ):
		DetailsPanel.__init__( self, panel, 1 )
		self.__triggers = {}
		self.__registerTriggers()
		
		self.pyPagesPanel_.onDrawItem.bind( self.__drawOperateItem )
		self.pyPagesPanel_.onItemSelectChanged.bind( self.__onOperationSelected )

		self.pyBtnFresh_.onLClick.bind( self.__onFresh )
		self.__pyBtnDraw = HButtonEx( panel.btnDraw )
		self.__pyBtnDraw.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnDraw.onLClick.bind( self.__onDrawOrder )
		self.__pyBtnDraw.enable = False
		labelGather.setPyBgLabel( self.__pyBtnDraw, "SpecialShop:DetailsPanel", "btnDraw" )
	
	def __drawOperateItem( self, pyViewItem ):
		pyItem = getattr( pyViewItem, "pyItem", None )
		if pyItem is not None :
			pyItem.setOperates( pyViewItem )
		curPageIndex = self.pyPagesPanel_.pageIndex
		totalPageIndex = self.pyPagesPanel_.maxPageIndex
		self.pyStPages_.text = "%d/%d"%( curPageIndex + 1, totalPageIndex + 1 )

	# ------------------------------------------------------------
	# private
	# ------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_YBT_SHOW_MY_ALL_BILL"]	= self.__onRecAllBill
		self.__triggers["EVT_ON_YBT_CANCLE_BILL_SUCCESS"]	= self.__onCancleBill
		self.__triggers["EVT_ON_YBT_CANCLE_BILL_ENABLE"]	= self.__onRequestSucc

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		"""
		deregister all events
		"""
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )
	# ----------------------------------------------------------------
	def __onRecAllBill( self, bills ):
		"""
		获取角色所有订单信息
		"""
		for bill in bills:
			for tick, billInfo in bill.items():
				forBill = []
				bType = 0
				for uid, billData in billInfo.items():
					if uid == 0:
						bType = billData
					else:
						forBill = [tick, uid, billData["state"], billData["rate"], billData["deposit"]]
				forBill.append( bType )
				if not forBill in self.pyPagesPanel_.items:
					self.pyPagesPanel_.addItem( forBill )
		curPageIndex = self.pyPagesPanel_.pageIndex
		totalPageIndex = self.pyPagesPanel_.maxPageIndex
		self.pyStPages_.text = "%d/%d"%( curPageIndex + 1, totalPageIndex + 1 )
		
	def __onCancleBill( self, tick, uid ):
		"""
		撤销订单回调
		"""
		for bill in self.pyPagesPanel_.items:
			btick = bill[0]
			buid = bill[1]
			if btick == tick and buid == uid:
				self.pyPagesPanel_.removeItem( bill )
		
	def __onRequestSucc( self, tick, uid, bType ):
		"""
		请求撤销回调
		"""
		player = BigWorld.player()
		def query( rs_id ):
			if rs_id == RS_OK:
				player.cancleBill( tick, uid, bType )
		if bType == csdefine.YB_BILL_TYPE_SELL: #寄售元宝
			showMessage( mbmsgs[0x07ed], "", MB_OK_CANCEL, query, self )
		elif bType == csdefine.YB_BILL_TYPE_BUY:
			showMessage( mbmsgs[0x07e3], "", MB_OK_CANCEL, query, self )
		return True
	
	def __onEstablishBill( self, tick, uid, rate, deposit ):
		"""
		建立订单成功回调
		"""
		self.pyPagesPanel_.addItem( [tick, uid, 3, rate, 1000, deposit] )
	
	def __onFresh( self ):
		"""
		刷新订单
		"""
		if time.time() - self.lastRefTime >= 10.0:
			self.lastRefTime = time.time()
			self.pyPagesPanel_.clearItems()
			BigWorld.player().getAllMyBills()
		else:
			showAutoHideMessage( 3.0, labelGather.getText( "SpecialShop:DetailsPanel", "freshWarning" ),"", MB_OK, pyOwner = self )
			return
	
	def __onDrawOrder( self ):
		"""
		撤销订单
		"""
		selItem = self.pyPagesPanel_.selItem
		if selItem is None:return
		tick = selItem[0]
		uid = selItem[1]
		bType = selItem[-1]
		BigWorld.player().cancleBillRequest( tick, uid, bType )
	
	def __onOperationSelected( self, selIndex ):
		"""
		选取某个明细
		"""
		self.__pyBtnDraw.enable = selIndex != -1

	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onSelected( self ):
		if not rds.statusMgr.isInWorld():return
		self.pyPagesPanel_.clearItems()
		BigWorld.player().getAllMyBills()

	def onHide( self ):
		DetailsPanel.onHide( self )
		
	def onLeaveWorld( self ):
		DetailsPanel.onLeaveWorld( self )

# -------------------------------------------------------------
from guis.controls.ListItem import MultiColListItem
from Time import Time
import csdefine
class DetailsItem( MultiColListItem ):
	
	details_states = { csdefine.YB_BILL_STATE_FREE	: "自由",
				csdefine.YB_BILL_STATE_TRADE_LOCK	: "锁定",
				csdefine.YB_BILL_STATE_OVER_DUE		: "过期",
				csdefine.YB_BILL_STATE_SELL_OUT		: "售空"
			}
	
	details_types = { csdefine.YB_RECORD_BUY_BILL	: "求购元宝",
					csdefine.YB_RECORD_SELL_BILL	: "寄售元宝",
					csdefine.YB_RECORD_BUY			: "购买元宝",
					csdefine.YB_RECORD_SELL			: "出售元宝"
					}
				
	bill_types = {
					csdefine.YB_BILL_TYPE_SELL		: "寄售元宝",
					csdefine.YB_BILL_TYPE_BUY		: "求购元宝"
				}
	
	_ITEM = None

	def __init__( self ):
		if DetailsItem._ITEM is None :
			DetailsItem._ITEM = GUI.load( "guis/general/specialshop/detailsitem.gui" )
			uiFixer.firstLoadFix( DetailsItem._ITEM )
		item = util.copyGuiTree( DetailsItem._ITEM )
		MultiColListItem.__init__( self, item )
		self.setTextes( "", "", "", "", "" )
		self.commonBackColor = ( 255, 255, 255, 0 )
		self.selectedBackColor = ( 118, 111, 67, 0 )
		self.highlightBackColor = ( 118, 111, 67, 0 )
		self.focus = False
		self.fontSize = 12
	
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
	
	def setLogs( self, pyViewItem ):
		"""
		更新订单明细
		"""
		details = pyViewItem.pageItem
		pyViewItem.visible = details is not None
		pyViewItem.focus = details is not None
		orderNumber = ""
		typeText = ""
		goldNum = ""
		unitPrice = ""
		timeText = ""
		if details:
			orderNumber = str( details[0])
			tradeState = details[2] #交易状态
			stateText = self.details_states.get( tradeState, "" )
			tradeType = details[1]	#交易类型
			typeText = self.details_types.get( tradeType, "" )
			goldNum = str( details[4]*100 )
			unitPrice = str( details[3] )
			startTime = Time.localtime( details[-1] - 3600*24 )
			timeText = labelGather.getText( "SpecialShop:DetailsPanel", "dateText" )%( startTime[1], startTime[2], startTime[3], startTime[4])
		self.selected = pyViewItem.selected
		if pyViewItem.selected :
			self.setState( UIState.SELECTED )
		elif self.isMouseHit() :
			self.setState( UIState.HIGHLIGHT )
		else :
			self.setState( UIState.COMMON )
		self.setTextes( orderNumber,
						typeText,
						goldNum,
						unitPrice,
						timeText,
						)
	
	def setOperates( self, pyViewItem ):
		"""
		设置订单记录
		"""
		operation = pyViewItem.pageItem
		pyViewItem.visible = operation is not None
		pyViewItem.focus = operation is not None
		orderNumber = ""
		typeText = ""
		goldNum = ""
		unitPrice = ""
		timeText = ""
		if operation:
			orderNumber = str( operation[1])
			tradeState = operation[2] #交易状态
			tradeType = operation[-1]	#交易类型
			typeText = self.bill_types.get( tradeType, "" )
			goldNum = str( operation[4]*100 )
			unitPrice = str( operation[3] )
			startTime = Time.localtime( operation[1]/1000 )
			timeText = labelGather.getText( "SpecialShop:DetailsPanel", "dateText" )%( startTime[1], startTime[2], startTime[3], startTime[4])
		self.selected = pyViewItem.selected
		if pyViewItem.selected :
			self.setState( UIState.SELECTED )
		elif self.isMouseHit() :
			self.setState( UIState.HIGHLIGHT )
		else :
			self.setState( UIState.COMMON )
		self.setTextes( orderNumber,
						typeText,
						goldNum,
						unitPrice,
						timeText,
						)
	