# -*- coding: gb18030 -*-
# $Id: AttrExtractPanel.py

from guis import *
from LabelGather import labelGather
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.tooluis.CSTextPanel import CSTextPanel
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
from CastKitItem import ExtractItem, ExtractEquipItem, CastKitHierogram
import csconst
import csdefine
import Const

class AttrExtractPanel( TabPanel ):
	"""
	属性抽取面板
	"""
	_item_dsp = { "crysItem":labelGather.getText( "CasketWindow:AttrExtractPanel", "crysDsp" ),	#物品格说明
					"equip":labelGather.getText( "CasketWindow:AttrExtractPanel", "equipDsp" ),
					}
					
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyMsgBox = None
		
		self.__pyHierogram = CastKitHierogram( panel.spcPanel.tokenItem, self, "hierogram" )
		self.__pyHierogram.update( None )
		
		self.__pyInfoPanel = CSTextPanel( panel.spcPanel.infoPanel.spanel, panel.spcPanel.infoPanel.sbar )
		self.__pyInfoPanel.opGBLink = True
		self.__pyInfoPanel.spacing = 2.0
		self.__pyInfoPanel.text = labelGather.getText( "CasketWindow:AttrExtractPanel", "tokenInfo" )
		
		self.__pyBtnBuy = HButtonEx( panel.spcPanel.btnBuy )
		self.__pyBtnBuy.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyLabel( self.__pyBtnBuy, "CasketWindow:EquipBuildPanel", "buy" )
		self.__pyBtnBuy.onLClick.bind( self.__onBuy )

		#初始化封灵石物品格
		self.__pyStones = []
		for name, item in panel.crysPanel.children:
			if not name.startswith( "crysItem_" ):continue
			index = int( name.split( "_" )[1] )
			pyStone = ExtractItem( item, self, "crysItem" )
			self.__pyStones.append( pyStone )
		
		self.__pyEquip = ExtractEquipItem( panel.crysPanel.eqItem, self, "equip" )
		self.__pyEquip.update( None )
		
		self.__pyStSucRate = StaticText( panel.sucRateBox.lbSucRate )
		self.__pyStSucRate.text = ""
		
		self.__pyCost = MoneyBar( panel.costBox )
		self.__pyCost.readOnly = True
		self.__pyCost.money = 0
		
		self.__pyBtnOk = HButtonEx( panel.btnOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyLabel( self.__pyBtnOk, "CasketWindow:main", "btnOk" )
		self.__pyBtnOk.onLClick.bind( self.__onExtract )
		
		labelGather.setLabel( panel.sucrateText, "CasketWindow:AttrExtractPanel", "sucRateText" )
		labelGather.setLabel( panel.costText, "CasketWindow:AttrExtractPanel", "reqMoney" )
		labelGather.setLabel( panel.spcPanel.title.stTitle, "CasketWindow:AttrExtractPanel", "specProps" )
	
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onKitbagUpdateItem
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onKitbagRemoveItem
		self.__triggers["EVT_ON_ITEM_EQUIPED"] = self.__onKitbagRemoveItem
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
		self.__triggers = {}
	# ------------------------------------------------------------------
	
	def __onBuy( self, pyBtn ):
		"""
		购买道具
		"""
		if pyBtn is None:return
		specShop = rds.ruisMgr.specialShop
		specShop.show( self.pyTopParent )
	
	def __onExtract( self ) :
		"""
		确定抽取
		"""
		self.pyParent.clearIndications()
		equip = self.__pyEquip.itemInfo
		if equip is None :
			# "请放入一件装备。"
			self.__showMessage( 0x0ea1 )
			return
		elemUIDs = []
		allStoneBinded = True
		for pyStone in self.__pyStones :
			stone = pyStone.itemInfo
			if stone is None : continue
			if not stone.baseItem.isBinded() :
				allStoneBinded = False
			elemUIDs.append( stone.uid )
		stoneAmount = len( elemUIDs )
		if stoneAmount == 0 :
			# "请至少放入一颗封灵石或超级封灵石。"
			self.__showMessage( 0x0ea2 )
			return

		elemUIDs.append( equip.uid )
		hierogram = self.__pyHierogram.itemInfo
		if hierogram is not None : elemUIDs.append( hierogram.uid )

		def checkAttribute() :
			createEft = equip.baseItem.getCreateEffect()
			pourEft = [ i for i in createEft if i[0] != 0 ]
			if len( pourEft ) > 0 :								# 装备有灌注属性
				def cb( res ) :
					if res != RS_YES : return
					if elemUIDs != self.__getElemUIDs() :		# 如果跟之前的放入不一致
						self.__onExtract()						# 则重新检查一遍
					else :
						checkStoneAmount()
				# "灌注的属性不能被抽取，是否继续？"
				self.__showMessage( 0x0ea3, MB_YES_NO, cb )
			else :
				checkStoneAmount()

		def checkStoneAmount() :
			if len( equip.baseItem.getExtraEffect() ) > stoneAmount :
				def cb( res ) :
					if res != RS_YES : return
					if elemUIDs != self.__getElemUIDs() :		# 如果跟之前的放入不一致
						self.__onExtract()						# 则重新检查一遍
					else :
						BigWorld.player().cell.equipExtract( elemUIDs )
				# "您的封灵石数量不足，不能把所有属性都抽取，只能随机抽取其中的属性，是否继续？"
				self.__showMessage( 0x0ea4, MB_YES_NO, cb )
			else :
				BigWorld.player().cell.equipExtract( elemUIDs )

		checkAttribute()

	def __getElemUIDs( self ) :
		"""
		检查确认后放入的东西是否已变动
		"""
		pyItems = self.__pyStones[:]
		pyItems.extend( [ self.__pyEquip, self.__pyHierogram ] )
		return [ e.itemInfo.uid for e in pyItems if e.itemInfo is not None ]

	def __calcRate( self ) :
		"""
		计算成功率
		"""
		if self.__pyEquip.itemInfo is None :
			self.__pyStSucRate.text = "0"
			return
		stone = None
		for pyStone in self.__pyStones :
			if pyStone.itemInfo is None : continue
			stone = pyStone.itemInfo
			break
		if stone is None :
			self.__pyStSucRate.text = "0"
			return
		rate = 0
		if stone.id == csconst.EQUIP_EXTRACT_NEEDITEMS :
			rate = 30
		elif stone.id == csconst.EQUIP_EXTRACT_SUNEEDITEMS :
			rate = 45
		if self.__pyHierogram.itemInfo and rate :
			rate = 100
		self.__pyStSucRate.text = "%i" % rate

	def __calcCost( self ) :
		"""
		计算所需金钱
		"""
		equip = self.__pyEquip.itemInfo
		if equip is None :
			self.__pyCost.money = 0
			return
		stones = [ st.itemInfo for st in self.__pyStones if st.itemInfo is not None ]
		amount = min( len( stones ), len( equip.baseItem.getExtraEffect() ) )
		if amount == 0 :
			self.__pyCost.money = 0
			return
		stQuality = stones[0].quality
		cost = equip.level**2 * equip.quality * 2**stQuality * 2 * amount	# 策划的计算公式
		self.__pyCost.money = cost

	# -------------------------------------------------
	def __onKitbagUpdateItem( self, itemInfo ) :
		"""
		背包更新物品
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			pyItem.update( itemInfo )
			self.__calcRate()
			if pyItem != self.__pyHierogram :
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
			if pyItem != self.__pyHierogram :
				self.__calcCost()

	def __getPyItemByUID( self, uid ) :
		"""
		根据UID查找界面上是否有该物品
		"""
		pyItems = self.__pyStones[:]
		pyItems.extend( [ self.__pyEquip, self.__pyHierogram ] )
		for pyItem in pyItems :
			if pyItem.itemInfo is None : continue
			if pyItem.itemInfo.uid == uid : return pyItem

	def __lockItems( self, locked ) :
		"""
		打开/关闭界面时改变背包中对应物品的颜色
		"""
		pyItems = self.__pyStones[:]
		pyItems.extend( [ self.__pyEquip, self.__pyHierogram ] )
		for pyItem in pyItems :
			if pyItem.itemInfo is None: continue
			self.__lockItem( pyItem.itemInfo, locked )

	def __lockItem( self, itemInfo, locked ) :
		"""
		通知背包锁定/解锁某个物品
		"""
		kitbagID = itemInfo.kitbagID
		if kitbagID > -1 :
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, locked )

	# -------------------------------------------------
	def __reset( self ) :
		for pyStone in self.__pyStones :
			pyStone.update( None )
		self.__pyEquip.update( None )
		self.__pyHierogram.update( None )
		self.__pyStSucRate.text = "0"
		self.__pyCost.money = 0

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


	# ----------------------------------------------------------------
	# friend methods
	# ----------------------------------------------------------------
	def onStoneDrop__( self, pyTarget, pyDropped ) :
		"""
		拖放封灵石物品格
		"""
		itemInfo = pyDropped.itemInfo
		validStones = [ csconst.EQUIP_EXTRACT_NEEDITEMS, csconst.EQUIP_EXTRACT_SUNEEDITEMS ]
		if itemInfo.id not in validStones :
			# "请放入封灵石或超级封灵石。"
			self.__showMessage( 0x0ea6 )
			return
		for pyStone in self.__pyStones :
			if pyStone.itemInfo is None : continue
			if pyStone == pyTarget : continue
			if pyStone.itemInfo.quality != itemInfo.quality :
				# "封灵石不能混用。"
				self.__showMessage( 0x0ea7 )
				return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcRate()
		self.__calcCost()
		
		#指引内容
		self.pyParent.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","casketWindow" ) )


	def onEquipDrop__( self, pyTarget, pyDropped ) :
		"""
		拖放到装备格
		"""
		itemInfo = pyDropped.itemInfo
		if not ( itemInfo.isEquip and itemInfo.level >= csconst.EQUIP_EXTRACT_LEVEL_MIN \
			and itemInfo.quality  in csconst.EQUIP_EXTRACT_QUALITYS ) :
				# "请放入60级以上且品质在粉色以上的装备。"
				self.__showMessage( 0x0ea8 )
				return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcRate()
		self.__calcCost()
		#指引内容
		self.pyParent.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","casketWindow" ) )

	def onHierogramDrop__( self, pyTarget, pyDropped ) :
		"""
		拖放到神符物品格
		"""
		itemInfo = pyDropped.itemInfo
		if itemInfo.id != csconst.EQUIP_EXTRACT_EXCITEM :
			# "只能放入神征令。神征令可将抽取成功率提高到100%，在副本掉落，也可在道具商城购买到。"
			self.__showMessage( 0x0ea9 )
			return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyParent = pyTarget.pyParent
		if pyParent.pyRtName_:
			pyTarget = pyParent
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcRate()
		#指引内容
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
		if pyIcon != self.__pyHierogram :
			self.__calcCost()
	
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
		pyItems = self.__pyStones[:]
		pyItems.extend( [ self.__pyEquip, self.__pyHierogram ] )
		for pyItem in pyItems:
			pyItem.update( None )
			
	def showDragItemIndication( self, idtId, itemType ):
		if itemType == Const.CASKET_WINDOW_EQUIP :#装备，需要定义类型
			equip = self.__pyEquip.itemInfo
			if equip is None :
				toolbox.infoTip.showHelpTips( idtId, self.__pyEquip )
				self.pyParent.addVisibleOpIdt( idtId )
		elif itemType == Const.CASKET_WINDOW_STONE:#石头
			isHasItem = False
			for pyStone in self.__pyStones :
				if pyStone.itemInfo is not None :
					isHasItem = True
			if not isHasItem:
				toolbox.infoTip.showHelpTips( idtId, self.__pyStones[1] )
				self.pyParent.addVisibleOpIdt( idtId )
		elif itemType == Const.CASKET_WINDOW_SHEN:#神征令
			hierogram = self.__pyHierogram.itemInfo
			if hierogram is None:
				toolbox.infoTip.showHelpTips( idtId, self.__pyHierogram.pyItemBg )
				self.pyParent.addVisibleOpIdt( idtId )
				
	def showOkIndication( self, idtId ):
		equip = self.__pyEquip.itemInfo
		if equip is None:return
		hierogram = self.__pyHierogram.itemInfo
		if hierogram is None:return
		for pyStone in self.__pyStones :
			if pyStone.itemInfo is None :continue
			toolbox.infoTip.showHelpTips( idtId, self.__pyBtnOk )
			self.pyParent.addVisibleOpIdt( idtId )
						
		