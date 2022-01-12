# -*- coding: gb18030 -*-
#
# $Id: ObjectItem.py,v 1.60 2008-09-02 10:28:10 fangpengjun Exp $

"""
implement objectitem
－－2005/08/12 : writen by huangyongwei
"""

import Language
import BigWorld
import csdefine
import csstatus
import csconst
import ItemTypeEnum
import GUIFacade
from gbref import rds
from ChatFacade import chatFacade, chatObjTypes
from event import EventCenter as ECenter
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.otheruis.AnimatedGUI import AnimatedGUI
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.tooluis.richtext_plugins.PL_NewLine import g_newLine
from guis.tooluis.richtext_plugins.PL_Align import PL_Align
from guis.tooluis.richtext_plugins.PL_Image import PL_Image
from guis.tooluis.inputbox.InputBox import AmountInputBox
from config.client.msgboxtexts import Datas as mbmsgs
from SplitBox import SplitBox
from guis.MLUIDefine import ItemQAColorMode
from VehicleHelper import isVehicleEquipUseable, isVehicleBook, isVehicleEquip, isOnVehicle

class ObjectItem( PyGUI ):
	def __init__( self, kitbagID, item, index, gbIndex ):
		PyGUI.__init__( self, item )
		self.dragFocus = False
		self.dropFocus = False
		self.focus = True
		self.__pyItem = Item( kitbagID, item.item, self )
		self.__pyItem.index = index
		self.__pyItem.gbIndex = gbIndex
		self.__pyLockIcon = PyGUI( item.lockIcon )
		self.__pyLockIcon.visible = False
		self.itemInfo = None
		if kitbagID != csdefine.KB_COMMON_ID and \
		index >= csdefine.KB_MAX_COLUMN:
			self.__pyItem.top += 1.0

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
			tipItems = rds.ruisMgr.kitBag.tipItems
			for tipid, pyItem in tipItems.iteritems() :
				if self == pyItem :
					toolbox.infoTip.hideOperationTips( tipid )
					del tipItems[ tipid ]
					break
			if self.__pyItem.kitbagID == csdefine.KB_CASKET_ID \
			and self.__pyItem.index == csdefine.KB_CASKET_SPACE:
				ECenter.fireEvent( "EVT_ON_CASKET_CRYSTEQUIP_REMOVE" )

	def unwield_update( self, itemInfo ):
		"""
		当从装备栏上卸下或者从背包中装备物品到装备栏中，更新背包的物品数据。这种情况比较特殊，需要显示闪烁效果，所以必须单独列出，而不能使用原有的接口
		"""
		self.__pyItem.unwield_update( itemInfo )
		self.itemInfo = itemInfo
		if itemInfo is not None :
			quality = itemInfo.quality
			isBinded = itemInfo.baseItem.isBinded()
			self.__pyLockIcon.visible = isBinded
			self.__setItemQuality( self.getGui(), quality )
		else:
			self.__pyLockIcon.visible = False
			self.__setItemQuality( self.getGui(), 1 )
			tipItems = rds.ruisMgr.kitBag.tipItems
			for tipid, pyItem in tipItems.iteritems() :
				if self == pyItem :
					toolbox.infoTip.hideOperationTips( tipid )
					del tipItems[ tipid ]
					break

	def __setItemQuality( self, itemBg, quality ):
		util.setGuiState( itemBg, ( 4, 2 ), ItemQAColorMode[quality] )

	def lock( self ):
		self.__pyItem.lock()

	def unlock( self ):
		self.__pyItem.unlock()

	def successParticle( self ):
		self.__pyItem.successParticle()

	def hideSuParticle( self ):
		self.__pyItem.hideSuParticle()

	def getRepairInfo( self, repairer ):
		return self.__pyItem.getRepairInfo( repairer )

	def _getLock( self ) :
		"""
		获取格子颜色是否被改变
		"""
		return self.__pyItem.isLocked

	def _getLocked( self ):
		return self.__pyItem.locked

	isLocked = property( _getLock )							# 仅用于获取物品是否被改变颜色的信息
	locked = property( _getLocked )							# 获取锁定状态

# -----------------------------------------------------
class Item( BOItem ) :

	def __init__( self, kitbagID, item = None, pyBinder = None ) :
		BOItem.__init__( self, item, pyBinder )
		self.__initialize( item )
		self.__gbIndex = 0
		self.__kitbagID = kitbagID
		self.focus = True
		self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True
		self.selectable = True
		self.dragMark = DragMark.KITBAG_WND
		self.__success_pName = "equipSuccess"

		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False

		self.__pyOverCover = AnimatedGUI( item.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )					# 动画播放一次，共8帧
		self.__pyOverCover.cycle = 0.4										# 循环播放一次的持续时间，单位：秒
		self.__pyCDCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )

		self.__triggers = {}
		self.__registerTriggers()

	def subclass( self, item ) :
		BOItem.subclass( self, item )
		self.__initialize( item )
		return True

	def __initialize( self, item ) :
		if item is None : return
		self.__dropEvents = {}
		self.__dropEvents[DragMark.KITBAG_WND] = DropHandlers.fromKitbagWindow
		self.__dropEvents[DragMark.ROLES_TRADING_WND] = DropHandlers.fromRolesTradingWindow
		self.__dropEvents[DragMark.BANK_WND_ITEM] = DropHandlers.fromBankWindow
		self.__dropEvents[DragMark.NPC_TRADE_BUY] = DropHandlers.fromTradingWindow
		self.__dropEvents[DragMark.NPC_TRADE_REDEEM] = DropHandlers.fromRedeemWindow
		self.__dropEvents[DragMark.KITBAG_BAG] = DropHandlers.fromKitBagPack
		self.__dropEvents[DragMark.EQUIP_WND] = DropHandlers.fromEquipWindow
		self.__dropEvents[DragMark.VEND_BUY_WND] = DropHandlers.fromVendBuy
		self.__dropEvents[DragMark.SPECIAL_SHOP_WND] = DropHandlers.fromSpecialShop
		self.__dropEvents[DragMark.TONG_STORAGE_ITEM] = DropHandlers.fromTongStorage
		self.__dropEvents[DragMark.TISHOU_SELL_PANEL] = DropHandlers.fromTiShouSellWindow
		self.__dropEvents[DragMark.TISHOU_BUY_PANEL] = DropHandlers.fromTiShouBuyWindow
		self.__dropEvents[DragMark.VEND_SELL_WND] = DropHandlers.fromVendSellWindow

		self.tongStorageOpen = False

	def dispose( self ) :
		self.__pyCDCover.dispose()
		self.__deregisterTriggers()
		BOItem.dispose( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_BEGIN_COOLDOWN"] = self.__beginCooldown
		self.__triggers["EVT_ON_TONG_STORAGE"] = self.__onTongStorage # 帮会仓库开闭 by姜毅
		for trigger in self.__triggers.iterkeys() :
			GUIFacade.registerEvent( trigger, self )

	def __deregisterTriggers( self ):
		for trigger in self.__triggers.iterkeys() :
			GUIFacade.unregisterEvent( trigger, self )
		self.__triggers = {}

	# -------------------------------------------------
	def __splitItem( self ) :
		"""
		if an item is more the one, split it into two
		"""
		if self.itemInfo is None : return
		if self.itemInfo.amount <= 1 : return
		uid = self.itemInfo.baseItem.uid
		def split( result, amount ) :
			if result == DialogResult.OK :
				GUIFacade.splitKitbagItem( uid, amount )
		rang = ( 1, self.amount - 1 )
		AmountInputBox().show( split, self, rang )

	# -------------------------------------------------
	def __beginCooldown( self, cooldownType, lastTime ) :
		"""
		handle cooldown message
		"""
		if self.itemInfo is None : return
		if GUIFacade.isCooldownType( self.itemInfo.baseItem.uid, cooldownType ) :
			cdInfo = self.itemInfo.getCooldownInfo()
			self.__pyCDCover.unfreeze( *cdInfo )

	def __onTongStorage( self, isShow ):
		"""
		通知帮会仓库开闭状态改变 by姜毅
		"""
		self.tongStorageOpen = isShow
		
	#-----------------------------------------------
	def __openNextBag( self ):
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().requestOpenNextBag( True )
		# "您是否要使用金丝木为你的仓库开启下一页空间?"
		showMessage( 0x03e1, "", MB_OK_CANCEL, query, self.pyTopParent )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDescriptionShow_( self ) :
		if self.itemInfo is None : return

		shapeName = rds.ccursor.shape		#如果是在修理状态 那么直接显示修理信息
		if "repair" in shapeName and self.itemInfo.isEquip:
			item = self.itemInfo.baseItem
			selfDsp = item.description(BigWorld.player())
			msg = GUIFacade.calcuOneRepairPrice( self.itemInfo.baseItem, GUIFacade.getRepairType() )
			if msg == "":
				msg = g_newLine + labelGather.getText( "KitBag:main", "noFix" )
			selfDsp.append([msg])
			toolbox.infoTip.showItemTips( self, selfDsp )
			return
		silverIcon = PL_Image.getSource( "guis/general/specialMerchantWnd/silver.gui" )
		selfDsp = self.itemInfo.description
		if  self.itemInfo.baseItem.canSell() and self.itemInfo.baseItem.getType() != ItemTypeEnum.ITEM_EQUIPMAKE_SCROLL :
			money = int( self.itemInfo.price *csconst.INVBUYPERCENT )
			if money < 1: money = 1

			msg = labelGather.getText( "KitBag:main", "unitPrice" ) + utils.currencyToViewText( money )
			msg = PL_Align.getSource( lineFlat = "M" )  + msg + PL_Align.getSource( "L" )
			selfDsp.append( [msg] )
			if self.itemInfo.amount > 1:
				totalAmount = self.itemInfo.amount
				money *= totalAmount
				msg = labelGather.getText( "KitBag:main", "totalPrice" ) + utils.currencyToViewText( money )
				msg = PL_Align.getSource( lineFlat = "M" ) +  msg + PL_Align.getSource( "L" )
				selfDsp.append( [msg] )
		if self.itemInfo.baseItem.reqYinpiao() != 0:

			section = Language.openConfigSection( "config/ItemYinpiaoValue.xml" )
			label = BigWorld.getSpaceDataFirstForKey( BigWorld.player().spaceID, csconst.SPACE_SPACEDATA_KEY )
			
			reqYinpiaoDsp = labelGather.getText( "KitBag:main", "buyUnitPrice" )% ( self.itemInfo.baseItem.reqYinpiao(), silverIcon )
			if self.itemInfo.baseItem.getAmount() > 1:
				reqYinpiaoDsp += labelGather.getText( "KitBag:main", "buyTotalPrice" )% ( self.itemInfo.baseItem.reqYinpiao() * self.itemInfo.baseItem.getAmount(), silverIcon )

			if section[str(self.itemInfo.baseItem.id)].readInt( label ) != 0:
				reqYinpiaoDsp += labelGather.getText( "KitBag:main", "sellUnitPrice" ) % ( section[str(self.itemInfo.baseItem.id)].readInt( label ), silverIcon )
				if self.itemInfo.baseItem.getAmount() > 1:
					reqYinpiaoDsp += labelGather.getText( "KitBag:main", "sellTotalPrice" )% ( section[str(self.itemInfo.baseItem.id)].readInt( label ) * self.itemInfo.baseItem.getAmount(), silverIcon )
			else:
				reqYinpiaoDsp += labelGather.getText( "KitBag:main", "noSpecial" )

			selfDsp.append( [reqYinpiaoDsp] )

		if self.itemInfo.baseItem.yinpiao() != 0:
			yinpiaoDsp = labelGather.getText( "KitBag:main", "totalTaels" )% ( self.itemInfo.baseItem.yinpiao(), silverIcon )
			selfDsp.append( [yinpiaoDsp] )

		equipDsps = GUIFacade.getSameTypeEquipDescriptions( self.__kitbagID, self.gbIndex )
		toolbox.infoTip.showItemTips( self, selfDsp, *equipDsps ) #显示物品的描述，有比较则显示比较

	# -------------------------------------------------
	def onLClick_( self, mods ) :
		if self.itemInfo is None :
			return True
		if mods == MODIFIER_SHIFT :
			if self.itemInfo.baseItem.getAmount() > 1 :
				boxInstance = SplitBox.instance()
				boxInstance.show( self )
				boxInstance.updateSplitItem( self.itemInfo )
		elif mods == MODIFIER_CTRL :
			chatFacade.insertChatObj( chatObjTypes.ITEM, self.itemInfo.baseItem )
		else :
			mouseShape = rds.ccursor.shape
			shapeName = mouseShape[0:len( mouseShape ) -2 ]
		return True

	def onRClick_( self, mods ) :
		BOItem.onRClick_( self, mods )
		if self.itemInfo is None : return
		player = BigWorld.player()
		if player.iskitbagsLocked() : # 如果背包已上锁，则返回
			player.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False
		if self.isLocked:return
		if self.pyBinder :
			tipItems = rds.ruisMgr.kitBag.tipItems
			for tipid, pyItem in tipItems.iteritems() :
				if self.pyBinder == pyItem :
					toolbox.infoTip.hideOperationTips( tipid )
					del tipItems[ tipid ]
					break
		mouseShape = rds.ccursor.shape
		shapeName = mouseShape[0:len( mouseShape ) -2 ]
		if player.tradeState == csdefine.TRADE_CHAPMAN and shapeName != "repair":
			amount = self.amount
			rang = [1, amount]
			def sell( result, amount ) :
				if result == DialogResult.OK :
					GUIFacade.sellToNPC( self.itemInfo.baseItem.uid, amount )
			sell( DialogResult.OK, amount )
		elif player.tradeState == csdefine.TRADE_INVENTORY and shapeName != "repair":

			#dstBank = rds.ruisMgr.storeWindow.curBagIndex
			#dstIndex = rds.ruisMgr.storeWindow.getcurItemsPanels().getEmptyStoreItemIndex()
			#if dstIndex != -1:
			player.bank_storeItem2Bag( self.__kitbagID, self.index, rds.ruisMgr.storeWindow.currBagIndex )
#			player.bank_storeItem2Bank( self.__kitbagID, self.index ) #, dstBank, dstIndex )
		elif player.tradeState&csdefine.TRADE_CASKET and shapeName != "repair":
			if self.__kitbagID == csdefine.KB_CASKET_ID:
				GUIFacade.moveItemFromCKToCommon( self.__kitbagID, self.index )    #神机匣右键取出物品
			else:
				order = player.getFreeOrderFK( csdefine.KB_CASKET_ID )
				if order != -1:
					# 普通包裹到神机匣
					#order = order%csdefine.KB_MAX_SPACE	# 切换为界面用的order
					GUIFacade.moveKbItemToKitTote( self.__kitbagID, self.index, csdefine.KB_CASKET_ID )
		elif player.tradeState == csdefine.TRADE_PRODUCE and shapeName != "repair": #装备打造
			ECenter.fireEvent( "EVT_ON_GET_PRODUCE_STUFF_FROM_KITBAG", self.__kitbagID, self.index )

		elif player.tradeState == csdefine.ENTITY_STATE_VEND and shapeName != "repair": #摆摊
			ECenter.fireEvent( "EVT_ON_VEND_ADD_ITEM", self.__kitbagID, self.index )

		elif player.tradeState == csdefine.TRADE_TISHOU and shapeName != "repair": #寄售物品
			ECenter.fireEvent( "EVT_ON_ADD_TISHOU_ITEM_FROM_KITBAG", self.__kitbagID, self.index )

		elif self.tongStorageOpen and shapeName != "repair": # 帮会仓库 by姜毅
			storageIndex = rds.ruisMgr.storageWindow.getCurStorageIndex()
			player.tong_storeItem2Bag( self.itemInfo.baseItem.getOrder(), storageIndex )

		elif player.tradeState == csdefine.TRADE_NONE and player.state != csdefine.ENTITY_STATE_VEND:
#			if self.itemInfo.id == csdefine.ID_OF_ITEM_OPEN_BAG:
#				self.__openNextBag( )
#				return True
			item = player.getItem_( self.__kitbagID * csdefine.KB_MAX_SPACE + self.index )
			#策划要求 在绑定判定前做使用判定 by姜毅
			if rds.ruisMgr.petEnhance.visible: 	#宠物强化界面
				if self.itemInfo.id in csconst.PET_DIRECT_ITEMS:
					ECenter.fireEvent( "EVT_ON_ENHANCE_UPDATE_SYMBOL", self.itemInfo )
				if item.getType() == ItemTypeEnum.ITEM_SYSTEM_KASTONE:
					baseItem = self.itemInfo.baseItem
					if not baseItem.isFull():
						player.statusMessage( csstatus.STONE_MUST_FULL )
						return False
					ECenter.fireEvent( "EVT_ON_ENHANCE_UPDATE_SOUL", self.itemInfo )
				return True
			isVecEqu = ItemTypeEnum.VEHICLE_EQUIP_LIST #骑宠装备
			if item.getType() in isVecEqu:
				if player.vehicleDBID == 0:
					player.statusMessage( csstatus.VEHICLE_NO_CONJURE )
					return False
				vehicleLevel = player.getVehicleLevel()
				if vehicleLevel < item.getReqLevel():
					player.statusMessage( csstatus.VEHICLE_CANT_WIELD )
					return False
			elif item.getType() in ItemTypeEnum.EQUIP_TYPE_SET:
				if not item.isMetier( player.getClass() ):
					player.statusMessage( csstatus.KIT_EQUIP_NOT_FIT_EQUIP )
					return False
				if player.level <  item.query( "reqLevel", 0 ):
					if item.getType() == ItemTypeEnum.ITEM_POTENTIAL_BOOK: # 使用潜能天书等级不足的话要特别提示
						player.statusMessage( csstatus.KIT_EQUIP_CANT_POTENTIAL_BOOK )
					else:
						player.statusMessage( csstatus.SPACE_MISS_LEVELLACK )
					return False
				reqGender = item.query( "reqGender", [] )
				if len( reqGender ) != 0:
					if not player.getGender() in reqGender:
						player.statusMessage( csstatus.KIT_EQUIP_NOT_FIT_EQUIP )
						return False
				hMax = item.query( "eq_hardinessMax" )
				if hMax > 0:
					if not item.query( "eq_hardiness" ) > 0:
						player.statusMessage( csstatus.CIB_MSG_EQUIP_HARDINESS, item.name() )
						return False
				lifeType = item.getLifeType()
				lifeTime = item.getLifeTime()
				if lifeType and not lifeTime:
					player.statusMessage( csstatus.CIB_MSG_ITEM_NO_USE_TIME )
					return False
			GUIFacade.autoUseKitbagItem( item )

		elif player.tradeState == csdefine.TRADE_SWAP and ( player.si_myState == csdefine.TRADE_SWAP_BEING or player.si_myState == csdefine.TRADE_SWAP_LOCK ):	# 玩家间交易
			ECenter.fireEvent( "EVT_ON_TRADE_SWAP_ADD_ITEM", self.kitbagID, self.index )

			#self.itemInfo.spell()
		if shapeName == "repair":
			rds.ccursor.normal()
		if hasattr( self.pyTopParent,"clearIndications" ):
			self.pyTopParent.clearIndications()
		return True

	# -------------------------------------------------
	def onDragStart_( self, pyDragged ) :
		if self.itemInfo is None: return False
		player = BigWorld.player()
		if player.iskitbagsLocked() : # 如果背包已上锁，则返回
			player.statusMessage( csstatus.CIB_MSG_KITBAG_LOCKED )
			return False
#		if player.tradeState == csdefine.ENTITY_STATE_VEND:
#			showMessage( 0x0aa1, "", MB_OK, None )	
		
		baseItem = self.itemInfo.baseItem
		type = baseItem.getType()
		if type in ItemTypeEnum.EQUIP_TYPE_SET:		#如果拖动的是装备
			self.successParticle()					#那么显示闪烁效果（策划要求拖动装备时也要闪烁）
		if BigWorld.isKeyDown( KEY_LCONTROL ) :
			rds.ruisMgr.dragObj.attach = KEY_LCONTROL
		BOItem.onDragStart_( self, pyDragged )
		GUIFacade.highLightEquipItem( self.__kitbagID, self.gbIndex )
		if not baseItem.isEquip() and baseItem.query( "spell", 0 ):
			rds.ruisMgr.hideBar.enterShow()
			rds.ruisMgr.hideBar.hightlightLack()
			rds.ruisMgr.quickBar.hightlightLack()
		return True

	def onDragStop_( self, pyDragged ) :
		type = self.itemInfo.baseItem.getType()
		if type in ItemTypeEnum.EQUIP_TYPE_SET:		#结束拖动时 如果是装备 那么尝试隐藏闪烁
			self.hideSuParticle()					#隐藏闪烁
		BOItem.onDragStop_( self, pyDragged )
		GUIFacade.dehighLightEquipItem( self.__kitbagID, self.gbIndex )
		rds.ruisMgr.hideBar.leaveShow()
		rds.ruisMgr.hideBar.hidelightLack()
		rds.ruisMgr.quickBar.hidelightLack()
		if pyDragged.itemInfo is None:return
		name = pyDragged.itemInfo.name()
		if not ruisMgr.isMouseHitScreen() : return False
		order = self.__kitbagID * csdefine.KB_MAX_SPACE + self.gbIndex
		preItem = BigWorld.player().itemsBag.getByOrder( order )
		def query( rs_id ):
			if rs_id == RS_OK:
				GUIFacade.destroyKitbagItem( preItem.uid )
		# "确定销毁%s?"
		showMessage( mbmsgs[0x03e2] % name, "", MB_OK_CANCEL, query, pyOwner = rds.ruisMgr.kitBag )
		return True

	def onDrop_( self, pyTarget, pyDropped ) :
		BOItem.onDrop_( self, pyTarget, pyDropped )
		dragMark = rds.ruisMgr.dragObj.dragMark
		if not self.__dropEvents.has_key( dragMark ) : return
		self.__dropEvents[dragMark]( pyTarget, pyDropped )
		return True
		
	def onMouseLeave_( self ) :
		BOItem.onMouseLeave_( self )
		toolbox.itemCover.hideItemCover( self )
	
	def successParticle( self ):
		"""
		更新图标上更换装备成功后的闪烁效果
		"""
		gui = self.getGui()
		if not hasattr( gui, self.__success_pName ):
			textureName = "maps/particle_2d/guanxiao_an_hong/guanxiao_an_hong.texanim"
			toolbox.itemParticle.addParticle( self , textureName, self.__success_pName, 0.99999 )
		else:
			for child in gui.children:
				if child[0] == self.__success_pName:
					child[1].visible = True
					break

	def hideSuParticle( self ):
		"""
		隐藏更换装备成功后闪烁效果
		"""
		gui = self.getGui()
		if not hasattr( gui, self.__success_pName ):
			return
		for child in gui.children:
			if child[0] == self.__success_pName:
				child[1].visible = False
				break

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	# -------------------------------------------------
	def update( self, itemInfo ) :
		BOItem.update( self, itemInfo )
		if itemInfo is None:
			self.noneItemInfoCover()
			return
		cdInfo = itemInfo.getCooldownInfo()
		self.__pyCDCover.unfreeze( *cdInfo )

	def noneItemInfoCover( self ):
		"""
		空ItmeInfo的cover处理 by姜毅
		"""
		if not self.isLocked:		# 如果没有被锁定
			self.color = 255, 255, 255, 255
		self.__pyCDCover.reset( 0 )

	def unwield_update( self, itemInfo ) :
		if self.locked :
			if not itemInfo or not self.itemInfo or \
			itemInfo.uid != self.itemInfo.uid :
				self.unlock()
		BOItem.update( self, itemInfo )
		if itemInfo is not None :
			self.kitbagID = itemInfo.kitbagID
			cdInfo = itemInfo.getCooldownInfo()
			self.__pyCDCover.unfreeze( *cdInfo )
			self.briefSuccessParticle()					#更换装备到装备栏上,到这里已经成功了,显示成功后的效果
		else :
			self.__pyCDCover.reset( 0 )
			self.hideSuParticle()

	def updateUseStatus( self, itemStatus ) :
		"""
		重写的方法
		更新物品可使用状态的表现
		"""
		if self.isLocked :
			self.color = 127, 127, 127, 255
		else :
			BOItem.updateUseStatus( self, itemStatus )

	def briefSuccessParticle( self ):
		"""
		更新图标上更换装备成功后的效果
		"""
		self.successParticle()
		BigWorld.callback( 3, self.hideSuParticle )

	def lock( self ) : #锁定物品,此锁目前为假锁（不锁定物品）
		BOItem.lock( self )
		self.updateUseStatus( self.itemInfo.checkUseStatus() )	# 更新物品的可使用状态

	def unlock( self ) : #解锁物品,此锁目前为假锁（不锁定物品）
		BOItem.unlock( self )
		#self.locked = False
		if self.itemInfo and self.itemInfo.kitbagID != -1 : # 如果等于-1再update会导致相应物品格不可用
			self.update( self.itemInfo )

	def getRepairInfo( self, repairer ) :
		if self.itemInfo is None : return None
		return GUIFacade.getRepairType(), self.kitbagID, self.index

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getKitbag( self ) :
		return self.__kitbagID

	def _setKitbag( self, kitbagID ):
		self.__kitbagID = kitbagID

	# -------------------------------------------------
	def _getGBIndex( self ) :
		return self.__gbIndex

	def _setGBIndex( self, index ) :
		self.__gbIndex = index



	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	kitbagID = property( _getKitbag, _setKitbag )
	gbIndex = property( _getGBIndex, _setGBIndex )

# --------------------------------------------------------------------
# --------------------------------------------------------------------
crystals = [50101173,50101174,50101175,50101176,50101177]
class DropHandlers :
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@staticmethod
	def fromKitbagWindow( pyTarget, pyDropped ) :
		"""
		the item drag from items window
		"""
		def splitItem( dstPyItem, srcPyItem, result, amount ) :
			if result == DialogResult.OK :
				uid = srcPyItem.itemInfo.baseItem.uid
				GUIFacade.splitKitbagItem( uid, amount )

		def exchangeItem( dstPyItem, srcPyItem ) :
			if dstPyItem.isLocked: return #如果目标格子被锁定
			srckitBag = srcPyItem.kitbagID
			dstkitBag = dstPyItem.kitbagID
			srcInfo = srcPyItem.itemInfo
			dstInfo = dstPyItem.itemInfo
			if dstPyItem.gbIndex == srcPyItem.gbIndex and srckitBag == dstkitBag : return
			if dstkitBag == csdefine.KB_CASKET_ID and \
			dstPyItem.gbIndex == csdefine.KB_CASKET_SPACE and not srcInfo.isEquip: #水晶摘除
				showMessage( mbmsgs[0x0ea1],"",MB_OK, None, pyOwner = rds.ruisMgr.kitBag )
				return
			if dstkitBag == csdefine.KB_CASKET_ID and \
			dstPyItem.gbIndex == csdefine.KB_CASKET_SPACE + 1 and not srcInfo.id in crystals: #放置摘除符
				showMessage( mbmsgs[0x03e5],"",MB_OK, None, pyOwner = rds.ruisMgr.kitBag )
				return
			if srckitBag == csdefine.KB_CASKET_ID and \
			srcPyItem.gbIndex == csdefine.KB_CASKET_SPACE:
				if dstInfo and not dstInfo.isEquip:
					showMessage( mbmsgs[0x0ea1],"",MB_OK, None, pyOwner = rds.ruisMgr.kitBag )
					return
			if srckitBag == csdefine.KB_CASKET_ID and \
			srcPyItem.gbIndex == csdefine.KB_CASKET_SPACE + 1: #放置摘除符
				if dstInfo and not srcInfo.id in crystals:
					showMessage( mbmsgs[0x03e5],"",MB_OK, None, pyOwner = rds.ruisMgr.kitBag )
					return
			GUIFacade.autoMoveKitbagItem( srckitBag, srcPyItem.gbIndex, dstkitBag, dstPyItem.gbIndex )
		if rds.ruisMgr.dragObj.attach == KEY_LCONTROL :
			amount = pyDropped.amount
			rang = ( 1, amount - 1 )
			func = Functor( splitItem, pyTarget, pyDropped )
			AmountInputBox().show( func, None, rang )
		else :
			exchangeItem( pyTarget, pyDropped )

	@staticmethod
	def fromEquipWindow( pyTarget, pyDropped ) :
		"""
		the item draged from equipment window
		"""
		dstBagIndex = pyTarget.kitbagID
		srcBagIndex = csdefine.KB_EQUIP_ID
		order = pyDropped.kitbagID * csdefine.KB_MAX_SPACE + pyDropped.gbIndex
		if BigWorld.player().getItem_( order ).getType() == ItemTypeEnum.ITEM_WEAPON_TWOSWORD:
			GUIFacade.autoMoveKitbagItem( srcBagIndex, pyDropped.index, dstBagIndex, 8 )
		GUIFacade.autoMoveKitbagItem( srcBagIndex, pyDropped.index, dstBagIndex, pyTarget.gbIndex )

	@staticmethod
	def fromRolesTradingWindow( pyTarget, pyDropepd ) :	# wsf,从交易栏到背包
		order = pyDropepd.gbIndex
		BigWorld.player().si_removeItem( order )

	@staticmethod
	def fromBankWindow( pyTarget, pyDropped ) : # 从仓库拖放物品到背包
		bankID = pyDropped.bagIndex
		bankOrder = pyDropped.itemOrder
		kitbag = pyTarget.kitbagID
		order = pyTarget.gbIndex
		BigWorld.player().bank_fetchItem2Order( bankOrder, kitbag, order )

	@staticmethod
	def fromTradingWindow( pyTarget, pyDropped ) :
		num = pyDropped.maxNum
		rang = ( 1, num )
		srcIndex = pyDropped.index
		def buy( result, amount ) :
			if result == DialogResult.OK :
				GUIFacade.buyFromNPC( [srcIndex],[amount] )
		if num is None:buy( DialogResult.OK, 1 )
		else: AmountInputBox().show( buy, rds.ruisMgr.tradeWindow, rang )

	@staticmethod
	def fromRedeemWindow( pyTarget, pyDropped ):
		dstkitBagID = pyTarget.kitbagID
		dstIndex = pyTarget.gbIndex
		uid = pyDropped.uid
		GUIFacade.redeemItem( uid )

	@staticmethod
	def fromKitBagPack( pyTarget, pyDropped ):
		dstkitBagID = pyTarget.kitbagID
		dstIndex = pyTarget.index
		kitbagID = pyDropped.kitBagID
		GUIFacade.moveKitbagToKbItem( kitbagID, dstkitBagID, dstIndex )

	@staticmethod
	def fromVendBuy( pyTarget, pyDropped ):
		uid = pyDropped.itemInfo.uid
		name = pyDropped.itemInfo.name()
		player = BigWorld.player()
		def query( rs_id ):
			if rs_id == RS_OK:
				player.vend_buy( uid, player.sellerID )
		costStr = utils.currencyToViewText( pyDropped.itemInfo.price, False )
		# "你要花费%s购买%s个%s么?"
		showMessage( mbmsgs[0x03e3] % ( costStr, pyDropped.itemInfo.amount, pyDropped.itemInfo.name() ), "", MB_OK_CANCEL, query )
		return True

	@staticmethod
	def fromVendSellWindow( pyTarget, pyDropped ) :
		itemUID = pyDropped.itemInfo.uid
		ECenter.fireEvent("EVT_ON_TAKE_BACK_VEND_ITEM", itemUID )

	@staticmethod
	def fromSpecialShop( pyTarget, pyDropped ):
		itemID = pyDropped.itemInfo.id
		price = pyDropped.price
		name = pyDropped.itemInfo.name()
		affirmBuy = rds.ruisMgr.specialShop.affirmBuy
		def split( result, amount ) :
			if result == DialogResult.OK :
				if affirmBuy: #需要确认
					def query( rs_id ):
						if rs_id == RS_OK:
							player = BigWorld.player()
							player.spe_shopping( itemID, amount, player.getSpeMoneyType() )
					# "确定花费%d元宝购买%d个%s?"
					showMessage( mbmsgs[0x03e4] % ( price*amount, amount, name ), "", MB_OK_CANCEL, query, pyOwner = pyTarget )
					return True
				else:
					player = BigWorld.player()
					player.spe_shopping( itemID, amount, player.getSpeMoneyType() )
		rang = ( 1, 100 )
		AmountInputBox().show( split, pyTarget, rang )

	@staticmethod
	def fromTongStorage( pyTarget, pyDropped ):
		player = BigWorld.player()
		srcOrder = pyDropped.gbIndex
		dstOrder = pyTarget.kitbagID*csdefine.KB_MAX_SPACE + pyTarget.gbIndex
		player.tong_fetchItem2Order( srcOrder, dstOrder, 0 )

	@staticmethod
	def fromTiShouSellWindow( pyTarget, pyDropped ) :
		itemUID = pyDropped.itemInfo.uid
		ECenter.fireEvent("EVT_ON_TAKE_BACK_TISHOU_ITEM", itemUID )

	@staticmethod
	def fromTiShouBuyWindow( pyTarget, pyDropped ) :
		ECenter.fireEvent("EVT_ON_BUY_TISHOU_ITEM", pyDropped.itemInfo )