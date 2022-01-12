# -*- coding: gb18030 -*-
# $Id: EquipIntensifyPanel.py

from guis import *
from LabelGather import labelGather
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.controls.RichText import RichText
from ItemsFactory import ObjectItem
from guis.general.kitbag.Animation import Animation
from guis.tooluis.CSTextPanel import CSTextPanel
from CastKitItem import CastKitEquip, CastKitStuff
from ItemSystemExp import EquipIntensifyExp
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
g_equipIntensify = EquipIntensifyExp.instance()
import csconst
import csdefine
import csstatus
import Const

class EquipIntensifyPanel( TabPanel ):
	"""
	装备强化面板
	"""
	_item_dsp = {}
	
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyMsgBox = None
		self.__pyEqItem = CastKitEquip( panel.eqPanel.eqItem, self, "equip" )
		
		self.__pyStuffItems = {}
		for name, item in panel.stuffPanel.children:
			if not name.startswith( "item_" ):continue
			tag = name.split( "_" )[1]
			pyStuffItem = CastKitStuff( item, self, tag )
			self.__pyStuffItems[tag] = pyStuffItem
		
		self.__pyBtnBuy = HButtonEx( panel.stuffPanel.btnBuy )
		self.__pyBtnBuy.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnBuy, "CasketWindow:EquipBuildPanel", "buy" )
		self.__pyBtnBuy.onLClick.bind( self.__onBuy )
		
		self.__pyRtSucRate = RichText( panel.rtSucRate )
		self.__pyRtSucRate.align = "C"
		self.__pyRtSucRate.text = ""
		self.__pyRtSucRate.foreColor = ( 0, 255, 0, 255 )
		
		self.__pyInfoPanel = CSTextPanel( panel.infoPanel.spanel, panel.infoPanel.sbar )
		self.__pyInfoPanel.opGBLink = True
		self.__pyInfoPanel.spacing = 2.0
		self.__pyInfoPanel.text = labelGather.getText( "CasketWindow:EquipIntensifyPanel", "instInfo" )
		
		self.__pyBtnOk = HButtonEx( panel.btnOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R3C1 )
		labelGather.setPyBgLabel( self.__pyBtnOk, "CasketWindow:main", "btnOk" )
		self.__pyBtnOk.onLClick.bind( self.__onIntensify )

		# 动画初始化
		succeedWnd = GUI.load( "guis/general/kitbag/casketwindow/succeed.gui" )
		self.__succeedAnimGui = Animation( succeedWnd )
		self.__succeedAnimGui.initAnimation( "succeedWnd",1.3 )

		failedWnd = GUI.load( "guis/general/kitbag/casketwindow/failed.gui" )
		self.__failedAnimGui = Animation( failedWnd )
		self.__failedAnimGui.initAnimation( "fieldWnd", 1.3 )

		self.__pyCost = MoneyBar( panel.costBox )
		self.__pyCost.readOnly = True
		self.__pyCost.money = 0

		labelGather.setLabel( panel.eqPanel.title.stTitle, "CasketWindow:EquipIntensifyPanel", "inputEquip" )
		labelGather.setLabel( panel.stuffPanel.dragonTitle.stTitle, "CasketWindow:EquipIntensifyPanel", "reqDragon" )
		labelGather.setLabel( panel.stuffPanel.symbolTitle.stTitle, "CasketWindow:EquipIntensifyPanel", "putSymbol" )
		labelGather.setLabel( panel.infoPanel.title.stTitle, "CasketWindow:EquipIntensifyPanel", "insTitle" )
		labelGather.setLabel( panel.costText, "CasketWindow:AttrExtractPanel", "reqMoney" )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onKitbagUpdateItem
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onKitbagRemoveItem
		self.__triggers["EVT_ON_ITEM_EQUIPED"] = self.__onKitbagRemoveItem
		self.__triggers["EVT_ON_PLAY_SUCCEED"] = self.__playSucceedAnim
		self.__triggers["EVT_ON_PLAY_FAILED"] = self.__playFailedAnim
		self.__triggers["EVT_ON_ROLE_UPDATE_INTENSIFY_ITEM"] = self.__onUpdateIntensifyItem
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
			self.__calcRate()
			self.__calcCost()

	def __onKitbagRemoveItem( self, itemInfo ) :
		"""
		背包移除物品
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			self.__lockItem( itemInfo, False )
			pyItem.update( None )
			self.__calcRate()
			self.__calcCost()

	def __getPyItemByUID( self, uid ) :
		"""
		根据UID查找界面上是否有该物品
		"""
		pyItems = self.__pyStuffItems.values()
		pyItems.extend( [ self.__pyEqItem ] )
		for pyItem in pyItems :
			if pyItem.itemInfo is None : continue
			if pyItem.itemInfo.uid == uid : return pyItem
	
	def __onBuy( self, pyBtn ):
		"""
		购买道具
		"""
		if pyBtn is None:return
		specShop = rds.ruisMgr.specialShop
		specShop.show( self.pyTopParent )
	
	def __onIntensify( self, pyBtn ):
		"""
		确定强化
		"""
		if pyBtn is None:return
		self.pyParent.clearIndications()
		player = BigWorld.player()
		eqInfo = self.__pyEqItem.itemInfo
		drgInfo = self.__pyStuffItems["dragon"].itemInfo
		symInfo = self.__pyStuffItems["symbol"].itemInfo
		if eqInfo is None:
			player.statusMessage( csstatus.CASKET_PLAEASE_INPUT_EQUIP )
			return
		if drgInfo is None:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return
		equip = eqInfo.baseItem
		dragon = drgInfo.baseItem
		elemUIDs = [ equip.uid, dragon.uid ]
		if symInfo:
			symbol = symInfo.baseItem
			elemUIDs.append( symbol.uid )
		if not equip.canIntensify():
			player.statusMessage( csstatus.CASKET_INTENSIFY_NO_SUPPORT )
			return
		# 每一种龙珠对应30级的装备
		equipLevel = equip.getReqLevel()
		minLevel = g_equipIntensify.getMinLevel( dragon.id )
		maxLevel = g_equipIntensify.getMaxLevel( dragon.id )
		if equipLevel < minLevel or equipLevel > maxLevel:
			player.statusMessage( csstatus.CASKET_MATIRAL_IS_WRONG )
			return
		intensifyLevel = equip.getIntensifyLevel()
		if intensifyLevel >= csdefine.EQUIP_INTENSIFY_MAX_LEVEL:
			player.statusMessage( csstatus.CASKET_INTENSIFY_MAXLEVEL )
			return
		player.cell.doEquipIntensify( elemUIDs )

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

	def onEquipDrop__( self, pyTarget, pyDropped ) :
		"""
		拖放到装备格
		"""
		itemInfo = pyDropped.itemInfo
		equip = itemInfo.baseItem
		if not ( equip.isEquip() and equip.canIntensify() and \
		equip.getIntensifyLevel() < csdefine.EQUIP_INTENSIFY_MAX_LEVEL ) :
				# "请放入可以强化且已强化等级不到9的装备。"
				self.__showMessage( 0x0eb3 )
				return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyParent = pyTarget.pyParent
		if pyParent.pyRtName_:
			pyTarget = pyParent
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcRate()
		self.__calcCost()
		self.pyParent.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","casketWindow" ) )
	
	def onStoneDrop__( self, pyTarget, pyDropped ) :
		"""
		拖放龙珠和幸运符格
		"""
		itemInfo = pyDropped.itemInfo
		trgTag = pyTarget.tag
		item = itemInfo.baseItem
		if trgTag == "dragon":						#龙珠
			if not g_equipIntensify.isDragonGem( item ):
				self.__showMessage( 0x0eb4 )
				return
		elif not g_equipIntensify.isLuckGem( item ):		# 幸运符
			self.__showMessage( 0x0eb5 )
			return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyParent = pyTarget.pyParent
		if pyParent.pyRtName_:
			pyTarget = pyParent
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcRate()
		self.__calcCost()
		self.pyParent.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","casketWindow" ) )

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
		self.__calcRate()
		self.__calcCost()

	def __lockItem( self, itemInfo, locked ) :
		"""
		通知背包锁定/解锁某个物品
		"""
		kitbagID = itemInfo.kitbagID
		if kitbagID > -1 :
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, locked )
	
	def __calcRate( self ):
		"""
		计算成功率
		"""
		rateText = labelGather.getText( "CasketWindow:EquipIntensifyPanel", "sucRate" )
		rate = 0
		eqInfo = self.__pyEqItem.itemInfo
		drnInfo = self.__pyStuffItems["dragon"].itemInfo
		if eqInfo and drnInfo:
			equip = eqInfo.baseItem
			dragon = drnInfo.baseItem
			equipLevel = equip.getReqLevel()
			intensifyLevel = equip.getIntensifyLevel()
			minLevel = g_equipIntensify.getMinLevel( dragon.id )
			maxLevel = g_equipIntensify.getMaxLevel( dragon.id )
			if equipLevel < minLevel or equipLevel > maxLevel:
				rate = 0
			elif intensifyLevel >= csdefine.EQUIP_INTENSIFY_MAX_LEVEL:
				rate = 0
			else:
				excOdds = 0
				symbolInfo = self.__pyStuffItems["symbol"].itemInfo
				if symbolInfo:
					symbol = symbolInfo.baseItem
					excOdds += g_equipIntensify.getExtraOdds( symbol.id )
				odds = g_equipIntensify.getOdds( intensifyLevel + 1 )
				rate = min( odds + excOdds, 100 )
		self.__pyRtSucRate.text = rateText%rate

	def __calcCost( self ):
		"""
		计算花费
		"""
		cost = 0 #需要花费
		eqInfo = self.__pyEqItem.itemInfo
		drnInfo = self.__pyStuffItems["dragon"].itemInfo
		if eqInfo and drnInfo:
			equip = eqInfo.baseItem
			dragon = drnInfo.baseItem
			equipLevel = equip.getReqLevel()
			intensifyLevel = equip.getIntensifyLevel()
			minLevel = g_equipIntensify.getMinLevel( dragon.id )
			maxLevel = g_equipIntensify.getMaxLevel( dragon.id )
			if equipLevel < minLevel or equipLevel > maxLevel:
				cost = 0
			elif intensifyLevel >= csdefine.EQUIP_INTENSIFY_MAX_LEVEL:
				cost = 0
			else:
				cost = int( g_equipIntensify.getReqMoney( equipLevel, intensifyLevel + 1 ) )
		self.__pyCost.money = cost

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

	def __playSucceedAnim( self ):
		"""
		播放成功的动画
		"""
		left = self.pyTopParent.center - self.__failedAnimGui.width/2.0
		top = self.pyTopParent.middle - self.__failedAnimGui.height/2.0
		self.__succeedAnimGui.playAnimation( ( left, top ), self )

	def __playFailedAnim( self ):
		"""
		播放失败的动画
		"""
		left = self.pyTopParent.center - self.__failedAnimGui.width/2.0
		top = self.pyTopParent.middle - self.__failedAnimGui.height/2.0
		self.__failedAnimGui.playAnimation( ( left, top ), self )
	
	def __onUpdateIntensifyItem( self, uid ):
		"""
		更新强化物品信息
		"""
		equip = BigWorld.player().getItemByUid_( uid )
		if equip is None:return
		equipInfo = ObjectItem( equip )
		self.__pyEqItem.update( equipInfo )
		self.__lockItem( equipInfo, True )
		self.__calcRate()
		self.__calcCost()
	
	def __lockItems( self, locked ) :
		"""
		打开/关闭界面时改变背包中对应物品的颜色
		"""
		pyItems = self.__pyStuffItems.values()
		pyItems.extend( [ self.__pyEqItem ] )
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
		pyItems = self.__pyStuffItems.values()
		pyItems.extend( [ self.__pyEqItem ] )
		for pyItem in pyItems:
			pyItem.update( None )
	
	def showDragItemIndication( self, idtId, itemType ):
		if itemType == Const.CASKET_WINDOW_EQUIP :#装备格
			equip = self.__pyEqItem.itemInfo
			if equip is None :
				toolbox.infoTip.showHelpTips( idtId, self.__pyEqItem.pyItemBg )
				self.pyParent.addVisibleOpIdt( idtId )
		elif itemType == Const.CASKET_WINDOW_STONE:#石头
			stone = self.__pyStuffItems["dragon"].itemInfo
			if stone is None:
				toolbox.infoTip.showHelpTips( idtId, self.__pyStuffItems["dragon"].pyItemBg )
				self.pyParent.addVisibleOpIdt( idtId )
				
	def showOkIndication( self, idtId ):
		equip = self.__pyEqItem.itemInfo
		if equip is None:return
		stone = self.__pyStuffItems["dragon"].itemInfo
		if stone is not None :	
			toolbox.infoTip.showHelpTips( idtId, self.__pyBtnOk )
			self.pyParent.addVisibleOpIdt( idtId )
		
			