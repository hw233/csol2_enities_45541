# -*- coding: gb18030 -*-
#
from event.EventCenter import *
from guis import *
from guis.common.PyGUI import PyGUI
from LabelGather import labelGather
from guis.common.TrapWindow import UnfixedTrapWindow
from guis.controls.Control import Control
from guis.tooluis.CSRichText import CSRichText
from guis.controls.BaseObjectItem import BaseObjectItem
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.controls.SelectableButton import HSelectableButtonEx
from guis.controls.SelectorGroup import SelectorGroup
from guis.tooluis.inputbox.InputBox import AmountInputBox
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.CSTextPanel import CSTextPanel
from SpecialGoodsItem import LolCopyItem
from ItemsFactory import ObjectItem
from gbref import rds
import ItemAttrClass
import csconst
import csdefine
import csstatus
import GUIFacade

TYPES_MAP = {"magAttack":28, "phyAttack":29, "magDefen":30, "phyDefen":31, "HPCeiling":32, "moveSpeed":33}

class LolTradeWnd( UnfixedTrapWindow ):
	"""
	英雄联盟购买界面
	"""
	_cc_items_rows = ( 2, 2 )

	def __init__( self ):
		wnd = GUI.load( "guis/general/specialMerchantWnd/loltrade.gui" )
		uiFixer.firstLoadFix( wnd )
		UnfixedTrapWindow.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.__triggers = {}
		self.__registerTriggers()
		self.__itemInfos = {}
		self.selIndex = -1
		self.__initialize( wnd )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initialize( self, wnd ):
		self.__pyEquips = {}
		self.__pyTypeSlectors = SelectorGroup()
		for name, item in wnd.equipPanel.children:
			if name.startswith( "eqItem_" ):
				index = int( name.split("_")[1] )
				pyEquip = EquipItem( item, index )
				self.__pyEquips[index] = pyEquip
		for name, item in wnd.typesPanel.children:
			if name.startswith( "typeBtn_" ):
				type = name.split("_")[1]
				pyTypeBtn = HSelectableButtonEx( item )
				pyTypeBtn.setExStatesMapping( UIState.MODE_R3C1 )
				pyTypeBtn.itemType = TYPES_MAP[type]
				labelGather.setPyBgLabel( pyTypeBtn, "lolTradeWnd:main", type )
				self.__pyTypeSlectors.addSelector( pyTypeBtn )
		self.__pyTypeSlectors.onSelectChanged.bind( self.__onTypeSelected )

		self.__pyRtSoulCoins = CSRichText( wnd.equipPanel.rtSoulCoin )
		self.__pyRtSoulCoins.align = 'R'
		self.__pyRtSoulCoins.text = ""

		self.__pyEquipPanel = ODPagesPanel( wnd.listPanel.panel, wnd.listPanel.control )
		self.__pyEquipPanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pyEquipPanel.onDrawItem.bind( self.__drawListItem )
		self.__pyEquipPanel.selectable = True
		self.__pyEquipPanel.onItemSelectChanged.bind( self.__onEquipSelChange )
		self.__pyEquipPanel.viewSize = self._cc_items_rows

		self.__pyInfoPanel = CSTextPanel( wnd.listPanel.infoPanel, wnd.listPanel.infoBar )
		self.__pyInfoPanel.text = ""

		self.__pyBtnSell = HButtonEx( wnd.equipPanel.btnSell )
		self.__pyBtnSell.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSell.onLClick.bind( self.__onSellEquip )
		labelGather.setPyBgLabel( self.__pyBtnSell, "lolTradeWnd:main", "sellEquip" )

		self.__pyBtnQuit = HButtonEx( wnd.typesPanel.btnQuit )
		self.__pyBtnQuit.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnQuit.onLClick.bind( self.__onQuit )
		labelGather.setPyBgLabel( self.__pyBtnQuit, "lolTradeWnd:main", "quit" )

		self.__pyBtnBuy = HButtonEx( wnd.listPanel.btnBuy )
		self.__pyBtnBuy.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnBuy.onLClick.bind( self.__onBuyEquip )
		labelGather.setPyBgLabel( self.__pyBtnBuy, "lolTradeWnd:main", "buyEquip" )

		labelGather.setPyLabel( self.pyLbTitle_, "lolTradeWnd:main", "lbTitle" )
		labelGather.setLabel( wnd.equipPanel.title.stTitle, "lolTradeWnd:main","hasEquip" )
		labelGather.setLabel( wnd.typesPanel.title.stTitle, "lolTradeWnd:main","equipTypes" )
		labelGather.setLabel( wnd.listPanel.title.stTitle, "lolTradeWnd:main","equipList" )


	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_LOLCOPY_TRADE_WND_SHOW"] = self.__onWndShow
		self.__triggers["EVT_ON_YXLM_EQUIP_INFO_CHANGED"] = self.__onAddItemInfo
		self.__triggers["EVT_ON_ROLE_ADD_YXLM_EQUIP"] = self.__onRoleAddEquip
		self.__triggers["EVT_ON_ROLE_REMOVE_YXLM_EQUIP"] = self.__onRoleRemEquip
		self.__triggers["EVT_ONTRADE_STATE_LEAVE"] = self.__onStateLeave
		self.__triggers["EVT_ON_PLAYERROLE_ACCUMPOINT_CHANGE"] = self.__onSoulCoinsChange
		self.__triggers["EVT_ON_LOLCOPY_ROLEEQUIP_SLECTED"] = self.__onEquipSelected

		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( key, self )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onTrapTriggered_( self, entitiesInTrap ) :
		"""
		陷阱触发
		@param	entitiesInTrap		: 陷阱里的ENTITY
		@type	entitiesInTrap		: LIST
		"""
		if self.trappedEntity not in entitiesInTrap :
			GUIFacade.tradeOverWithNPC()
			self.hide()

	def __initListItem( self, pyViewItem ) :
		"""
		初始化添加的商品列表项
		"""
		item = GUI.load( "guis/general/tradewindow/item.gui" )
		uiFixer.firstLoadFix( item )
		pyLolItem = LolCopyItem( item, DragMark.LoLCOPY_TRADE_WND, self )
		pyViewItem.pyLolItem = pyLolItem
		pyViewItem.addPyChild( pyLolItem )
		pyViewItem.focus = True
		pyLolItem.left = 0
		pyLolItem.top = 0

	def __drawListItem( self, pyViewItem ) :
		"""
		重画商品列表项
		"""
		invoice = pyViewItem.pageItem
		pyLolItem = pyViewItem.pyLolItem
		pyLolItem.selected = pyViewItem.selected
		pyLolItem.update( invoice )
		curPageIndex = self.__pyEquipPanel.pageIndex
		totalPageIndex = self.__pyEquipPanel.maxPageIndex

	def __onWndShow( self, chapman ):
		"""
		接收装备数据并显示
		"""
		self.setTrappedEntID( chapman.id )
		self.show()

	def __onAddItemInfo( self, index, itemInfo ):
		"""
		添加物品
		"""
		invoiceItem = InvoiceItem( index, itemInfo )
		invoice = GUIFacade.getInvoice( index )
		type = invoice.itemType 									# 物品类型
		if type in self.__itemInfos:
			self.__itemInfos[type].append( invoiceItem )
		else:
			self.__itemInfos[type] = [invoiceItem]
		selSelector = self.__pyTypeSlectors.pyCurrSelector
		if selSelector is None:return
		selType = selSelector.itemType
		if selType == type and \
		not invoiceItem in self.__pyEquipPanel.items:
			self.__pyEquipPanel.addItem( invoiceItem )

	def __onRoleAddEquip( self, equip ):
		"""
		购买成功回调
		"""
		equipInfo = ObjectItem( equip )
		for index, pyEquip in self.__pyEquips.items():
			if pyEquip.itemInfo is None:
				pyEquip.update( equipInfo )
				break

	def __onRoleRemEquip( self, eqUid ):
		"""
		移除装备
		"""
		for index, pyEquip in self.__pyEquips.items():
			itemInfo = pyEquip.itemInfo
			if itemInfo is None:continue
			if itemInfo.uid == eqUid:
				pyEquip.update( None )

	def __onStateLeave( self, state ):
		"""
		离开交易状态
		"""
		if state == csdefine.TRADE_CHAPMAN:
			GUIFacade.tradeOverWithNPC()
			self.hide()
			BigWorld.player().tradeState = csdefine.TRADE_NONE

	def __onSoulCoinsChange( self, soulCoins ):
		"""
		灵魂币改变
		"""
		self.__pyRtSoulCoins.text = labelGather.getText( "lolTradeWnd:main", "soulCoins" )%soulCoins + \
		PL_Image.getSource( "guis/general/specialMerchantWnd/soulcoin.gui" )

	def __onEquipSelected( self, selIndex ):
		"""
		选取装备
		"""
		self.selIndex = selIndex
		for index, pyEquip in self.__pyEquips.items():
			pyEquip.selected = index == selIndex
		self.__pyBtnSell.enable = True

	def __onSellEquip( self, pyBtn ):
		"""
		出售装备
		"""
		if pyBtn is None:return
		pyEquip = self.__pyEquips.get( self.selIndex, None )
		if pyEquip and pyEquip.itemInfo:
			uid = pyEquip.itemInfo.uid
			chapman = GUIFacade.getChapMan()
			if chapman is None:return
			player = BigWorld.player()
			if player.actionSign( csdefine.ACTION_FORBID_TALK ):				#判断是否能跟NPC对话 完成操作
				player.statusMessage( csstatus.ROLE_DEAD_FORBID_CONTROLE )
				return
			chapman.cell.buyFrom( uid, 1 )

	def __onQuit( self, pyBtn ):
		"""
		退出购买
		"""
		self.hide()

	def __onBuyEquip( self, pyBtn ):
		"""
		购买装备
		"""
		selItem = self.__pyEquipPanel.selItem
		if selItem is None:return
		GUIFacade.buyYXLMEquipFromNPC( selItem.index )

	def __onEquipSelChange( self, selIndex ):
		"""
		选取装备
		"""
		player = BigWorld.player()
		self.__pyBtnBuy.enable = selIndex >= 0
		selItem = self.__pyEquipPanel.selItem
		if selItem is None:return
		attrMap = ItemAttrClass.m_itemAttrMap
		itemInfo = selItem.itemInfo
		item = itemInfo.baseItem
		nameDes = attrMap["name"].description( item, player )
		nameDes = PL_Font.getSource( nameDes, fc = item.getQualityColor() )
		des1 = PL_Font.getSource( attrMap["describe1"].description( item, player ), fc = "c4" )
		des2 = PL_Font.getSource( attrMap["describe2"].description( item, player ), fc = "c40" )
		self.__pyInfoPanel.text = labelGather.getText( "lolTradeWnd:main","itemDsp" )%( nameDes, des1, des2 )

	def __onTypeSelected( self, pyBtn ):
		"""
		选择装备类型
		"""
		if pyBtn is None:return
		self.__pyEquipPanel.clearItems()
		itemType = pyBtn.itemType
		invoices = self.__itemInfos.get( itemType, [] )
		self.__pyEquipPanel.addItems( invoices )
		if len( invoices ):
			self.__onEquipSelChange( 0 )

	def __clearEquips( self ):
		"""
		清空所有购买到的装备
		"""
		for pyEq in self.__pyEquips.itervalues():
			pyEq.update(None)

	# ----------------------------------------------------------------
	# public
	#-----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.__clearEquips()
		self.hide()

	def show( self ):
		UnfixedTrapWindow.show( self )
		self.__pyTypeSlectors.pyCurrSelector = self.__pyTypeSlectors.pySelectors[0]
		soulCoins = BigWorld.player().accumPoint
		self.__pyRtSoulCoins.text = labelGather.getText( "lolTradeWnd:main", "soulCoins" )%soulCoins + \
		PL_Image.getSource( "guis/general/specialMerchantWnd/soulcoin.gui" )

	def hide( self ):
		self.__itemInfos = {}
		if rds.statusMgr.isInWorld() :
			GUIFacade.tradeOverWithNPC()
			BigWorld.player().tradeState = csdefine.TRADE_NONE
		UnfixedTrapWindow.hide( self )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )
		self.__pyEquipPanel.clearItems()
		self.__pyInfoPanel.text = ""
		self.__pyRtSoulCoins.text = ""

# ------------------------------------------------------------------------------------------------
class EquipItem( PyGUI ):
	def __init__( self, item, index ):
		PyGUI.__init__( self, item )
		self.__pyItem = BaseObjectItem( item.item )
		self.__pyItem.onLClick.bind( self.__onEquipSelected )
		self.__pyCover = PyGUI( item.cover )
		self.__pyCover.visible = False
		self.__pyStAmount = StaticText( item.item.lbAmount )
		self.__pyStAmount.text = ""
		self.itemInfo = None
		self.index = index

	def __onEquipSelected( self, pyEquip ):
		if pyEquip.itemInfo is None:return
		ECenter.fireEvent( "EVT_ON_LOLCOPY_ROLEEQUIP_SLECTED", self.index )

	def __select( self ):
		if self.__pyCover:
			self.__pyCover.visible = True

	def __deselect( self ):
		if self.__pyCover:
			self.__pyCover.visible = False

	def update( self, itemInfo ):
		"""
		更新图标
		"""
		if itemInfo is None:
			self.__pyCover.visible = False
		self.__pyItem.update( itemInfo )
		self.itemInfo = itemInfo

	def _getSelected( self ):
		return self.__selected

	def _setSelected( self, selected ):
		if selected:
			self.__select()
		else:
			self.__deselect()
		self.__selected = selected

	selected = property( _getSelected, _setSelected )

class InvoiceItem:
	def __init__( self, index, itemInfo ):
		self.index = index
		self.itemInfo = itemInfo
		self.uid = -1

	def update( self, uid, itemInfo ):
		self.uid = uid
		self.itemInfo = itemInfo