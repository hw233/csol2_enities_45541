# -*- coding: gb18030 -*-
#
#gjx 2009-1-5
#
from event.EventCenter import *
from guis import *
from guis.common.Window import Window
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.inputbox.InputBox import AmountInputBox
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from gbref import rds
import csconst
import csdefine
import GUIFacade
import utils
import event.EventCenter as ECenter
from SpecialGoodsItem import SpecialGoodsItem
from SpecialGoodsItem import DarkMerchantItem
from SpecialGoodsItem import DarkGoodsItem
from config.client import GoodsType
from config.item import A_DarkTraderDatas
from LabelGather import labelGather
from Function import Functor
import Timer

GOODSNAME = eval( labelGather.getText( "SpecialMerchantWnd:main", "miGoodsName" ) )
AREAS = eval( labelGather.getText( "SpecialMerchantWnd:main", "miAreas" ) )

# -------------------------------------------------------------------
# implement MerchantWindow
# -------------------------------------------------------------------
class MerchantWindow( Window ):
	"""
	卖特产的NPC界面的基类
	"""
	def __init__( self, wnd ):
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.__triggers = {}
		self.__registerTriggers()
		self.__trapID = 0


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initialize_( self, buyPanel ):
		self.__pyBuyPanel = buyPanel
		self.__pyBuyPanel.onDrop.bind( self.__onItemDrop )

	def showWindow_( self, npc ) :
		player = BigWorld.player()
		#ECenter.fireEvent("EVT_ONTRADE_STATE_LEAVE", player.tradeState )	# 注释掉（在这里发送这个消息是有问题的。因为本函数是向服务器申请交易返回来后再触发的，hyw--2008.09.17）
		player.tradeState = csdefine.TRADE_CHAPMAN
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		self.__trapID = player.addTrapExt( csconst.COMMUNICATE_DISTANCE, self.__onEntitiesTrapThrough )#打开窗口后为玩家添加对话陷阱
		self.show()

	def registerTriggers_( self, key, evt ):
		"""
		给继承的子类添加新触发事件
		"""
		self.__triggers[key] = evt

	def getBuyPanel_( self ):
		return self.__pyBuyPanel


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_END_WITHNPC_TRADE"] = self.hide
		self.__triggers["EVT_ONTRADE_STATE_LEAVE"] = self.__onStateLeave
		self.__triggers["EVT_ON_ROLE_DEAD"] = self.hide						# 角色死亡后隐藏窗口
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )									# 删除玩家的对话陷阱
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		gossiptarget = GUIFacade.getGossipTarget()							# 获取当前对话NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:				# 如果NPC离开玩家对话陷阱
			GUIFacade.tradeOverWithNPC()
			self.hide()														# 隐藏当前交易窗口

	def __onItemDrop( self, pyTarget, pyDropped ):
		dragMark = rds.ruisMgr.dragObj.dragMark
		if dragMark == DragMark.KITBAG_WND :
			uid = pyDropped.itemInfo.baseItem.uid
			num = pyDropped.amount
			if num == 1:
				GUIFacade.sellToNPC( uid, num )
			else:
				def sell( result, amount ) :
					if result == DialogResult.OK :
						GUIFacade.sellToNPC( uid, amount )
				rang = ( 1, num )
				AmountInputBox().show( sell, self, rang )
		return True

	def __onShowBuyPanel( self ):
		pass


	# ----------------------------------------------------------------
	# public
	#-----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.hide()

	def show( self ):
		Window.show( self )

	def hide( self ):
		self.__itemInfos = {}
		if rds.statusMgr.isInWorld() :
			GUIFacade.tradeOverWithNPC()
			BigWorld.player().tradeState = csdefine.TRADE_NONE
		Window.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		self.__pyBuyPanel.clearItems()

	def __onStateLeave( self, state ):
		if state == csdefine.TRADE_CHAPMAN:
			GUIFacade.tradeOverWithNPC()
			self.hide()
			BigWorld.player().tradeState = csdefine.TRADE_NONE


# -------------------------------------------------------------------
# implement SpecialMerchantWindow
# -------------------------------------------------------------------
class SpecialMerchantWindow( MerchantWindow ):
	"""
	帮会跑商任务商品交易界面
	"""
	def __init__( self ):
		wnd = GUI.load( "guis/general/specialMerchantWnd/specialmerchantwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		MerchantWindow.__init__( self, wnd )
		self.__initialize( wnd )
		self.__registerTriggers()
		self.__reqTimerID = 0

	def __initialize( self, wnd ):
		buyPanel = SpecialMerchantPanel( wnd.infosPanel )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		lbIncTitle = wnd.infosPanel.incPricePanel.bgTitle.stTitle
		lbDecTitle = wnd.infosPanel.decPricePanel.bgTitle.stTitle
		labelGather.setLabel( wnd.lbTitle, "SpecialMerchantWnd:SpecialMerchantWindow", "miRbTitle" )	# 商品交易
		labelGather.setLabel( lbIncTitle, "SpecialMerchantWnd:SpecialMerchantWindow", "miIncTitle" )	# 价格提升
		labelGather.setLabel( lbDecTitle, "SpecialMerchantWnd:SpecialMerchantWindow", "miDecTitle" )	# 价格下降

		self.initialize_( buyPanel )

	def __registerTriggers( self ):
		myTriggers = {}
		myTriggers["EVT_ON_TRADE_WITH_MERCHANT"] = self.showWindow_
		for key, evt in myTriggers.iteritems():
			GUIFacade.registerEvent( key, self )
			self.registerTriggers_( key, evt )
	
	def showWindow_( self, merchant ):
		MerchantWindow.showWindow_( self, merchant )
		Timer.cancel( self.__reqTimerID )
		self.__reqTimerID = Timer.addTimer( 0, csdefine.TRADE_REQUIRE_AMOUNT_TIME, Functor( self.__reqAmount, merchant ) )
	
	def __reqAmount( self, merchant ):
		if merchant is None:return
		GUIFacade.reqInvoceAmount( merchant )
	
	def hide( self ):
		MerchantWindow.hide( self )
		Timer.cancel( self.__reqTimerID )
		self.__reqTimerID = 0

# -------------------------------------------------------------------
# implement DarkMerchantWindow
# -------------------------------------------------------------------
class DarkMerchantWindow( MerchantWindow ):
	"""
	黑市商人交易界面
	"""
	def __init__( self ):
		wnd = GUI.load( "guis/general/specialMerchantWnd/specialmerchantwnd.gui" )
		uiFixer.firstLoadFix( wnd )
		MerchantWindow.__init__( self, wnd )
		self.__initialize( wnd )
		self.__registerTriggers()

	def __initialize( self, wnd ):
		buyPanel = DarkMerchantPanel( wnd.infosPanel )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		lbIncTitle = wnd.infosPanel.incPricePanel.bgTitle.stTitle
		lbDecTitle = wnd.infosPanel.decPricePanel.bgTitle.stTitle
		labelGather.setLabel( wnd.lbTitle, "SpecialMerchantWnd:SpecialMerchantWindow", "miRbTitle" )	# 商品交易
		labelGather.setLabel( lbIncTitle, "SpecialMerchantWnd:SpecialMerchantWindow", "miIncTitle" )	# 价格提升
		labelGather.setLabel( lbDecTitle, "SpecialMerchantWnd:SpecialMerchantWindow", "miDecTitle" )	# 价格下降

		self.initialize_( buyPanel )

	def __registerTriggers( self ):
		myTriggers = {}
		myTriggers["EVT_ON_TRADE_WITH_DARK_MERCHANT"] = self.showWindow_
		for key, evt in myTriggers.iteritems():
			GUIFacade.registerEvent( key, self )
			self.registerTriggers_( key, evt )


# -------------------------------------------------------------------
# implement DarkTradeWindow
# -------------------------------------------------------------------
class DarkTradeWindow( MerchantWindow ):
	"""
	投机商人交易窗口
	"""
	def __init__( self ):
		wnd = GUI.load( "guis/general/speculatorwindow/speculatorwindow.gui" )
		uiFixer.firstLoadFix( wnd )
		MerchantWindow.__init__( self, wnd )
		self.__initialize( wnd )
		self.__registerTriggers()

	def __initialize( self, wnd ):
		self.currentGoodID = 0
		self.currentBuyPercent = 0.0
		self.itemInfoDict = A_DarkTraderDatas.Datas
		buyPanel = DarkBuyPanel( wnd.infosPanel )

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		lbPurTitle = wnd.infosPanel.purchasePanel.bgTitle.stTitle
		labelGather.setLabel( wnd.lbTitle, "SpecialMerchantWnd:DarkTradeWindow", "miRbTitle" )	# 商品交易
		labelGather.setLabel( lbPurTitle, "SpecialMerchantWnd:DarkTradeWindow", "miPurTitle" )	# 商品收购

		self.initialize_( buyPanel )


	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def __registerTriggers( self ) :
		myTriggers = {}
		myTriggers["EVT_ON_TRADE_WITH_DARK_TRADER" ] = self.__showWindow									#角色死亡后隐藏窗口
		for key, evt in myTriggers.iteritems() :
			GUIFacade.registerEvent( key, self )
			self.registerTriggers_( key, evt )

	# -----------------------------------------------------------
	def __showWindow( self, npc ) :
		self.currentGoodID = npc.currentGoodID
		self.currentBuyPercent = npc.currentBuyPercent
		self.showWindow_( npc )

	# -----------------------------------------------------------
	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )							# 删除玩家的对话陷阱
			self.__trapID = 0


	# --------------------------------------------------------
	# public
	# --------------------------------------------------------
	def show( self ):
		"""
		"""
		try:
			itemPrice = int( self.itemInfoDict.values()[0][str( self.currentGoodID )][0] )
			floatPrice = self.darkPriceCarry( itemPrice * self.currentBuyPercent )
			convertedPrice = utils.currencyToViewText( floatPrice )
			itemCommand = self.itemInfoDict.values()[0][str( self.currentGoodID )][1] % convertedPrice
			self.getBuyPanel_().setCommandRichText( itemCommand )
		except KeyError:
			ERROR_MSG( "投机商人列表中没有商品'%s',是否是在base上创建的？" % ( self.currentGoodID ) )
		MerchantWindow.show( self )

	def darkPriceCarry( self, price ):
		"""
		四舍五入取整
		这边同服务器那边的RoleTradeWithNPC里是一致的
		"""
		return int( price + 0.5 )

# ------------------------------------------------------------------
# implement MerchantPanel
# ------------------------------------------------------------------
from guis.controls.ODPagesPanel import ODPagesPanel

class MerchantPanel( Control ):
	
	_cc_items_rows = ( 4, 2 )
	_item_dragMark = DragMark.NPC_TRADE_BUY 						# 物品拖放标记
	
	def __init__( self, infosPanel = None ):
		Control.__init__( self, infosPanel )
		self.dropFocus = True
		self.__itemTypies ={}
		self.__triggers = {}
		self.__registerTriggers()
		self.__initPanel( infosPanel )
		self.__goodsType = 22										# 商品类型是特产

	def __initPanel( self, infosPanel ):
		self.pyPagePanel_ = ODPagesPanel( infosPanel.itemsPanel, infosPanel.pgIdxBar )
		self.pyPagePanel_.onViewItemInitialized.bind( self.initListItem_ )
		self.pyPagePanel_.onDrawItem.bind( self.drawListItem_ )
		self.pyPagePanel_.selectable = True
		self.pyPagePanel_.viewSize = self._cc_items_rows

		self.__pyIncPriceInfo = CSRichText( infosPanel.incPricePanel.info )
		self.__pyIncPriceInfo.lineFlat = "M"
		self.__pyDecPriceInfo = CSRichText( infosPanel.decPricePanel.info )
		self.__pyDecPriceInfo.lineFlat = "M"

	def initListItem_( self, pyViewItem ):
		"""
		虚拟函数,由子类实现
		"""
		pass
	
	def drawListItem_( self, pyViewItem ):
		itemInfo = pyViewItem.pageItem
		pyItem = pyViewItem.pyItem
		pyViewItem.focus = itemInfo is not None
		pyItem.crossFocus = itemInfo is not None
		pyItem.selected = pyViewItem.selected
		pyItem.update( itemInfo )		

	# -----------------------------------------------------------
	# protected
	# -----------------------------------------------------------
	def registerTriggers_( self, key, evt ):
		"""
		给继承的子类添加新触发事件
		"""
		self.__triggers[key] = evt

	def onReceivePriceChangeInfo_( self, priceChangeInfo ):
		"""
		@param	priceChangeInfo	价格变动信息
		@type	priceChangeInfo	STRING_ARRAY
		"""
		self.__setPriceChangeInfo( priceChangeInfo )

	def onReceiveGoodsInfoChange_( self, uid, itemInfo ):
		"""
		接受到服务器商品数量改变通知

		@param	uid:		商品ID
		@param	currAmount:	商品剩余数量
		"""
		if uid < 1:
			return
		else:
			for pyViewItem in self.pyPagePanel_.pyViewItems:
				pyItem = pyViewItem.pyItem
				if pyItem.uid == uid:
					invoiceItem = InvoiceItem( uid - 1, itemInfo )
					pyItem.update( invoiceItem )
					break

	def onAddItemInfo_( self, index, itemInfo ):
		"""
		"""
		amount = GUIFacade.getInvoiceAmountByUid( index + 1 )
		if amount < 1:return										# 如果商品已经卖完，则不再显示商品
		if index == 0 and itemInfo is None :
			return
		type = itemInfo.invoiceType 									# 物品类型
		if type != self.__goodsType:
			return
		invoiceItem = InvoiceItem( index, itemInfo )
		if not invoiceItem in self.pyPagePanel_.items:
			self.pyPagePanel_.addItem( invoiceItem )
			
	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def __registerTriggers( self ) :
		pass

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	# -------------------------------------------------
	def __getItemTypeStr( self, type ): # 根据物品类型获得类型名称
		return GoodsType.Datas[ type ]

	# -------------------------------------------------
	def __setPriceChangeInfo( self, priceChangeInfo ):
		"""
		@param	priceChangeInfo:	价格变动信息
		@type	priceChangeInfo:	STRING_ARRAY
		@return :	None
		"""
		self.__pyIncPriceInfo.text = self.__colourKeyWord( priceChangeInfo[0] )
		self.__pyDecPriceInfo.text = self.__colourKeyWord( priceChangeInfo[1] )

	def __colourKeyWord( self, text ):
		"""
		@param	text:	要替换的句子
		@type	text:	STRING
		@return：STRING
		"""
		upText = labelGather.getText( "SpecialMerchantWnd:main", "miUpText" )
		downText = labelGather.getText( "SpecialMerchantWnd:main", "miDownText" )
		if text == "":
			return text
		praResume = resume = text.split("，")[-1]	# 仅替换掉句子中摘要部分(最后一个逗号之后)的关键字
		for name in GOODSNAME:
			if name in resume:
				colourName = PL_Font.getSource( name, fc = ( 13, 218, 183, 255 ) )
				resume = resume.replace( name, colourName )
				break
		for area in AREAS:
			if area in resume:
				colourArea = PL_Font.getSource( area, fc = ( 13, 218, 183, 255 ) )
				resume = resume.replace( area, colourArea )
				break
		if upText in resume:
			colourChange = PL_Font.getSource( upText, fc = ( 200, 240, 129, 255 ) )
			resume= resume.replace( upText, colourChange )
		elif downText in resume:
			colourChange = PL_Font.getSource( downText, fc = ( 255, 0, 0, 255 ) )
			resume= resume.replace( downText, colourChange )

		return text.replace( praResume, resume )

	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )
	
	def clearItems( self ):
		self.pyPagePanel_.clearItems()

# ------------------------------------------------------------------
# implement SpecialMerchantPanel
# ------------------------------------------------------------------
class SpecialMerchantPanel( MerchantPanel ):
	def __init__( self, infosPanel = None ):
		MerchantPanel.__init__( self, infosPanel )
		self.__registerTriggers()
	
	def initListItem_( self, pyViewItem ):
		item = GUI.load( "guis/general/specialMerchantWnd/specialitem.gui" )
		uiFixer.firstLoadFix( item )
		pyItem = SpecialGoodsItem( item, self._item_dragMark, self )
		pyViewItem.pyItem = pyItem
		pyViewItem.addPyChild( pyItem )
		pyItem.left = 0
		pyItem.top = 0		
		
	def __registerTriggers( self ):
		myTriggers = {}
		myTriggers["EVT_ON_RECEIVE_PRICE_CHANGE_INFO"] = self.onReceivePriceChangeInfo_
		myTriggers["EVT_ON_MERCHANT_RECEIVE_GOODS_INFO_CHANGE"] = self.onReceiveGoodsInfoChange_
		myTriggers["EVT_ON_SPECIAL_BAG_INFO_CHANGED"] = self.onAddItemInfo_ 	# 添加物品
		for key, evt in myTriggers.iteritems():
			GUIFacade.registerEvent( key, self )
			self.registerTriggers_( key, evt )

# ------------------------------------------------------------------
# implement DarkMerchantPanel
# ------------------------------------------------------------------
class DarkMerchantPanel( MerchantPanel ):
	def __init__( self, infosPanel = None ):
		MerchantPanel.__init__( self, infosPanel )
		self.__registerTriggers()

	def initListItem_( self, pyViewItem ):
		item = GUI.load( "guis/general/specialMerchantWnd/specialitem.gui" )
		uiFixer.firstLoadFix( item )
		pyItem = DarkMerchantItem( item, self._item_dragMark, self )
		pyViewItem.pyItem = pyItem
		pyViewItem.addPyChild( pyItem )
		pyItem.left = 0
		pyItem.top = 0

	def __registerTriggers( self ):
		myTriggers = {}
		myTriggers["EVT_ON_RECEIVE_PRICE_CHANGE_INFO"] = self.onReceivePriceChangeInfo_
		myTriggers["EVT_ON_DARK_MERCHANT_RECEIVE_GOODS_INFO_CHANGE"] = self.onReceiveGoodsInfoChange_
		myTriggers["EVT_ON_DARK_MERCHANT_BAG_INFO_CHANGED"] = self.onAddItemInfo_ 	# 添加物品
		for key, evt in myTriggers.iteritems():
			GUIFacade.registerEvent( key, self )
			self.registerTriggers_( key, evt )

# ------------------------------------------------------------------
# implement DarkBuyPanel
# ------------------------------------------------------------------
class DarkBuyPanel( Control ):

	_cc_items_rows = ( 4, 2 )
	_item_dragMark = DragMark.NPC_TRADE_BUY 	# 物品拖放标记

	def __init__( self, infosPanel = None ):
		Control.__init__( self, infosPanel )
		self.dropFocus = True
		self.__itemTypies ={} 					# 商品类型,key为商品类型，values为商品的intemInfo列表
		self.__triggers = {}
		self.__registerTriggers()
		self.__initPanel( infosPanel )

	def __initPanel( self, infosPanel ):
		self.__pyCommandRT = CSRichText( infosPanel.purchasePanel.info )
		self.__pyCommandRT.text = ""

		self.__pyPagePanel = ODPagesPanel( infosPanel.itemsPanel, infosPanel.pgIdxBar )
		self.__pyPagePanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pyPagePanel.onDrawItem.bind( self.__drawListItem )
		self.__pyPagePanel.selectable = True
		self.__pyPagePanel.viewSize = self._cc_items_rows

	def __initListItem( self, pyViewItem ):
		item = GUI.load( "guis/general/specialMerchantWnd/darkitem.gui" )
		uiFixer.firstLoadFix( item )
		pyDarkItem = DarkGoodsItem( item, self._item_dragMark, self )
		pyViewItem.pyDarkItem = pyDarkItem
		pyViewItem.addPyChild( pyDarkItem )
		pyDarkItem.left = 0
		pyDarkItem.top = 0

	def __drawListItem( self, pyViewItem ):
		itemInfo = pyViewItem.pageItem
		pyDarkItem = pyViewItem.pyDarkItem
		pyViewItem.focus = itemInfo is not None
		pyDarkItem.crossFocus = itemInfo is not None
		pyDarkItem.selected = pyViewItem.selected
		pyDarkItem.update( itemInfo )

	# -----------------------------------------------------------
	# private
	# -----------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_DARKTRADER_BAG_INFO_CHANGED"] = self.__onAddItemInfo # 添加物品
		self.__triggers["EVT_ON_DARK_TRADER_RECEIVE_GOODS_INFO_CHANGE"] = self.__onReceiveGoodsInfoChange
		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	# -----------------------------------------------------
	def __onAddItemInfo( self, index, itemInfo ):
		"""
		"""
		amount = GUIFacade.getInvoiceAmountByUid( index + 1 )
		if amount < 1:return						# 如果商品已经卖完，则不再显示商品
		if index == 0 and itemInfo is None :
			return
		type = itemInfo.invoiceType 					# 物品类型
		invoiceItem = InvoiceItem( index, itemInfo )
		if not invoiceItem in self.__pyPagePanel.items:
			self.__pyPagePanel.addItem( invoiceItem )
			
	def __onReceiveGoodsInfoChange( self, uid, itemInfo ):
		"""
		接受到服务器商品数量改变通知

		@param	uid:		商品ID
		@param	currAmount:	商品剩余数量
		"""
		if uid < 1:
			return
		else:
			for pyViewItem in self.__pyPagePanel.pyViewItems:
				pyDarkItem = pyViewItem.pyDarkItem
				if pyDarkItem.uid == uid:
					itemInfo = itemInfo( uid - 1, itemInfo )
					pyDarkItem.update( itemInfo )
					break
	# -------------------------------------------------
	def __getItemTypeStr( self, type ): #根据物品类型获得类型名称
		return GoodsType.Datas[ type ]

	# --------------------------------------------------------
	# public
	# --------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def setCommandRichText( self, text ):
		self.__pyCommandRT.text = text
	
	def clearItems( self ):
		self.__pyPagePanel.clearItems()

	# --------------------------------------------------------

class InvoiceItem:
	def __init__( self, index, itemInfo ):
		self.index = index
		self.itemInfo = itemInfo
		self.uid = -1
	
	def update( self, uid, itemInfo ):
		self.uid = uid
		self.itemInfo = itemInfo