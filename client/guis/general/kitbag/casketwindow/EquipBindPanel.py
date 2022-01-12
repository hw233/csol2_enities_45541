# -*- coding: gb18030 -*-
# $Id: .py

from guis import *
from LabelGather import labelGather
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.controls.RichText import RichText
from ItemsFactory import ObjectItem
from guis.general.kitbag.Animation import Animation
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
from CastKitItem import CastKitEquip, CastKitStuff
from config.client.msgboxtexts import Datas as mbmsgs
from ItemSystemExp import EquipBindExp
g_equipBind = EquipBindExp.instance()
import ItemTypeEnum
import csconst
import csdefine
import csstatus

class EquipBindPanel( TabPanel ):
	"""
	装备认主面板
	"""
	_item_dsp = {}
	
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyMsgBox = None
		self.__pyEqItem = CastKitEquip( panel.eqPanel.eqItem, self, "equip" )
		
		self.__pyChainItem = CastKitStuff( panel.stuffPanel.chainItem, self, "chain" )

		self.__pyBtnBuy = HButtonEx( panel.stuffPanel.btnBuy )
		self.__pyBtnBuy.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnBuy, "CasketWindow:EquipBuildPanel", "buy" )
		self.__pyBtnBuy.onLClick.bind( self.__onBuy )
		
		self.__pyInfoPanel = CSTextPanel( panel.infoPanel.spanel, panel.infoPanel.sbar )
		self.__pyInfoPanel.opGBLink = True
		self.__pyInfoPanel.spacing = 2.0
		self.__pyInfoPanel.text = labelGather.getText( "CasketWindow:EquipBindPanel", "bindInfo" )

		self.__pyCost = MoneyBar( panel.costBox )
		self.__pyCost.readOnly = True
		self.__pyCost.money = 0
		
		self.__pyBtnOk = HButtonEx( panel.btnOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnOk, "CasketWindow:EquipBindPanel", "bind" )
		self.__pyBtnOk.onLClick.bind( self.__onBind )

		labelGather.setLabel( panel.eqPanel.title.stTitle, "CasketWindow:EquipIntensifyPanel", "inputEquip" )
		labelGather.setLabel( panel.stuffPanel.chainTitle.stTitle, "CasketWindow:EquipBindPanel", "putChain" )
		labelGather.setLabel( panel.infoPanel.title.stTitle, "CasketWindow:EquipBindPanel", "bindTitle" )
		labelGather.setLabel( panel.costText, "CasketWindow:AttrExtractPanel", "reqMoney" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onKitbagUpdateItem
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onKitbagRemoveItem
		self.__triggers["EVT_ON_ITEM_EQUIPED"] = self.__onKitbagRemoveItem
		for key in self.__triggers :
			ECenter.registerEvent( key, self )
	# --------------------------------------------------------------------------------
	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
	
	def __onKitbagUpdateItem( self, itemInfo ) :
		"""
		背包更新物品
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			pyItem.update( itemInfo )

	def __onKitbagRemoveItem( self, itemInfo ) :
		"""
		背包移除物品
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			self.__lockItem( itemInfo, False )
			pyItem.update( None )

	def __getPyItemByUID( self, uid ) :
		"""
		根据UID查找界面上是否有该物品
		"""
		pyItems = [ self.__pyEqItem, self.__pyChainItem ]
		for pyItem in pyItems :
			if pyItem.itemInfo is None : continue
			if pyItem.itemInfo.uid == uid : 
				return pyItem
	
	def __onBuy( self, pyBtn ):
		"""
		购买道具
		"""
		if pyBtn is None:return
		specShop = rds.ruisMgr.specialShop
		specShop.show( self.pyTopParent )
	
	def __onBind( self, pyBtn ):
		"""
		确定认主
		"""
		if pyBtn is None:return
		player = BigWorld.player()
		eqInfo = self.__pyEqItem.itemInfo
		chnInfo = self.__pyChainItem.itemInfo
		if eqInfo is None:
			player.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return
		if chnInfo is None:
			player.statusMessage( csstatus.MERGE_ORNAMENT_NEED_MATERIAL )
			return
		equip = eqInfo.baseItem
		chain = chnInfo.baseItem
		elemUIDs = [ equip.uid, chain.uid ]
		if equip.getType() in [ ItemTypeEnum.ITEM_SYSTEM_TALISMAN, \
		ItemTypeEnum.ITEM_SYSTEM_KASTONE, \
		ItemTypeEnum.ITEM_FASHION1, \
		ItemTypeEnum.ITEM_FASHION2, \
		ItemTypeEnum.ITEM_POTENTIAL_BOOK ]:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return
		if equip.isWhite():
			player.statusMessage( csstatus.CASKET_WHITEEQUIP_IS_WRONG )
			return
		if equip.isObey():
			player.statusMessage( csstatus.KIT_EQUIP_OBEY_YET )
			return
		lvm = equip.getLevel()
		if lvm > 0 and lvm <= 50:    #1~50 1.1^道具等级*100*品质/3
			money = 1.1 ** lvm * 100 * equip.getQuality() /3
		else:           #51~150级 1.03^道具等级*2700 *品质/3
			money = 1.03 ** lvm * 2700 * equip.getQuality() /3
		if player.money < int(money):
			player.statusMessage( csstatus.CASKET_BIND_NEED_MONEY )
			return
		isBinded = equip.isBinded()
		if isBinded:
			player.cell.equipBind( elemUIDs )	# 直接认主
		else:
			def query( rs_id ):
				if rs_id == RS_OK:
					player.cell.equipBind( elemUIDs )
			showMessage( mbmsgs[0x00a5], "", MB_OK_CANCEL, query )

	def __showMessage( self, msg, style = MB_OK, cb = None ) :
		"""
		弹出提示框，同时只能弹出一个
		"""
		def callback( res ) :
			self.__pyMsgBox = None
			if callable( cb ) :
				cb( res )
		if self.__pyMsgBox is not None :
			self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", style, callback, self )

	def __getElemUIDs( self ) :
		"""
		检查确认后放入的东西是否已变动
		"""
		pyItems = [ self.__pyEqItem, self.__pyChainItem ]
		return [ e.itemInfo.uid for e in pyItems if e.itemInfo is not None ]

	def __calcCost( self ):
		"""
		计算花费
		"""
		uids = self.__getElemUIDs()
		itemList = [ BigWorld.player().getItemByUid_( uid ) for uid in uids ]
		equips = []
		cost = 0
		for item in itemList:
			if item.isFrozen():
				cost = 0
			if item.isEquip():
				equips += [item]
		if len( equips ) != 1:
			cost = 0
		else:
			equip = equips[0]
			if equip.getType() in [ ItemTypeEnum.ITEM_SYSTEM_TALISMAN, \
			ItemTypeEnum.ITEM_SYSTEM_KASTONE, \
			ItemTypeEnum.ITEM_FASHION1, \
			ItemTypeEnum.ITEM_FASHION2, \
			ItemTypeEnum.ITEM_POTENTIAL_BOOK ]:
				cost = 0
			if equip.isObey():
				cost = 0
			#money = equip.getReqLevel() * g_bind.getPerCost()
			#同步装备认主公式修改 by姜毅
			lvm = equip.getLevel()
			if lvm > 0 and lvm <= 50:    #1~50 1.1^道具等级*100*品质/3
				cost = 1.1 ** lvm * 100 * equip.getQuality() /3
			else:           #51~150 1.03^道具等级*2700 *品质/3
				cost = 1.03 ** lvm * 2700 * equip.getQuality() /3
		self.__pyCost.money = int( cost )

	def onEquipDrop__( self, pyTarget, pyDropped ) :
		"""
		拖放到装备格
		"""
		player = BigWorld.player()
		itemInfo = pyDropped.itemInfo
		equip = itemInfo.baseItem
		if equip.getType() in [ ItemTypeEnum.ITEM_SYSTEM_TALISMAN, \
		ItemTypeEnum.ITEM_SYSTEM_KASTONE, \
		ItemTypeEnum.ITEM_FASHION1, \
		ItemTypeEnum.ITEM_FASHION2, \
		ItemTypeEnum.ITEM_POTENTIAL_BOOK ]:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return
		if equip.isWhite():
			player.statusMessage( csstatus.CASKET_WHITEEQUIP_IS_WRONG )
			return
		if equip.isObey():
			player.statusMessage( csstatus.KIT_EQUIP_OBEY_YET )
			return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyParent = pyTarget.pyParent
		if pyParent.pyRtName_:
			pyTarget = pyParent
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcCost()
		
	def onStoneDrop__( self, pyTarget, pyDropped ) :
		"""
		拖放龙珠和幸运符格
		"""
		itemInfo = pyDropped.itemInfo
		trgTag = pyTarget.tag
		item = itemInfo.baseItem
		if trgTag == "chain":						#灵魂锁链
			stuff = g_equipBind.getStuff()
			if not item.id in stuff:
				player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
				return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyParent = pyTarget.pyParent
		if pyParent.pyRtName_:
			pyTarget = pyParent
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcCost()

	def onItemRemove__( self, pyIcon ) :
		"""
		右击移除物品
		"""
		if pyIcon.itemInfo is None : return
		self.__lockItem( pyIcon.itemInfo, False )
		pyParent = pyIcon.pyParent
		if pyParent and pyParent.pyRtName_:
			pyIcon = pyParent
		pyIcon.update( None )
		self.__calcCost()

	def __lockItem( self, itemInfo, locked ) :
		"""
		通知背包锁定/解锁某个物品
		"""
		kitbagID = itemInfo.kitbagID
		if kitbagID > -1 :
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, locked )

	def __showMessage( self, msg, style = MB_OK, cb = None ) :
		"""
		弹出提示框，同时只能弹出一个
		"""
		def callback( res ) :
			self.__pyMsgBox = None
			if callable( cb ) :
				cb( res )
		if self.__pyMsgBox is not None :
			self.__pyMsgBox.hide()
		self.__pyMsgBox = showMessage( msg, "", style, callback, self )

	def __lockItems( self, locked ) :
		"""
		打开/关闭界面时改变背包中对应物品的颜色
		"""
		pyItems = [ self.__pyEqItem, self.__pyChainItem ]
		for pyItem in pyItems :
			if pyItem.itemInfo is None: continue
			self.__lockItem( pyItem.itemInfo, locked )

	def onItemMouseEnter__( self, pyItem ):
		"""
		显示物品格描述信息
		"""
		tag = pyItem.tag
		dsp = self._item_dsp.get( tag, "" )
		if dsp != "":
			toolbox.infoTip.showToolTips( self, dsp )

	def onItemMouseLeave__( self ):
		"""
		隐藏物品格描述信息
		"""
		toolbox.infoTip.hide()
		
	# ----------------------------------------------------------
	#public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onShow( self ):
		self.__lockItems( True )
	
	def onHide( self ):
		self.__lockItems( False )
	
	def onLeaveWorld( self ):
		self.onHide()
		pyItems = [ self.__pyEqItem, self.__pyChainItem ]
		for pyItem in pyItems:
			pyItem.update( None )