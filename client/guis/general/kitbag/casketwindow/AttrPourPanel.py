# -*- coding: gb18030 -*-
# $Id: AttrPourPanel.py

from guis import *
from LabelGather import labelGather
from guis.controls.ButtonEx import HButtonEx
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.tooluis.inputbox.MoneyInputBox import MoneyBar
from CastKitItem import ExtractEquipItem, ExtractItem
import csconst
import csdefine
import Const

class AttrPourPanel( TabPanel ):
	"""
	属性灌注面板
	"""
	_item_dsp = { "stone":labelGather.getText( "CasketWindow:AttrPourPanel", "stoneDsp" ),	#物品格说明
					"equip":labelGather.getText( "CasketWindow:AttrPourPanel", "equipDsp" ),
					}
	
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__triggers = {}
		self.__initialize( panel )
		self.__registerTriggers()
		self.__pyMsgBox = None
		
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = self.__onKitbagUpdateItem
		self.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = self.__onKitbagRemoveItem
		self.__triggers["EVT_ON_ITEM_EQUIPED"] = self.__onKitbagRemoveItem
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __unregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )
		self.__triggers = {}
	
	def __initialize( self, panel ):
		self.__pyBtnOk = HButtonEx( panel.btnOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onPour )
		labelGather.setPyBgLabel( self.__pyBtnOk, "CasketWindow:main", "btnOk" )
		
		self.__pyCost = MoneyBar( panel.costBox )
		self.__pyCost.readOnly = True
		self.__pyCost.money = 0

		self.__pyEquip = ExtractEquipItem( panel.equipItem, self, "equip" )
		self.__pyEquip.update( None )

		self.__pyStone = ExtractItem( panel.stoneItem, self, "stone" )
		self.__pyStone.update( None )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		
		labelGather.setLabel( panel.costText, "CasketWindow:AttrExtractPanel", "reqMoney" )
	# -------------------------------------------------
	def __onPour( self ) :
		"""
		灌注属性
		"""
		equip = self.__pyEquip.itemInfo
		if equip is None :
			# "请放入一件装备。"
			self.__showMessage( 0x0ea1 )
			return
		stone = self.__pyStone.itemInfo
		if stone is None :
			# "请放入一个韵灵琥珀。"
			self.__showMessage( 0x0eab )
			return
		elemUIDs = [ equip.uid, stone.uid ]
		if stone.baseItem.isBinded() and not \
			equip.baseItem.isBinded() :
				def confirmToPour( res ) :
					if res != RS_YES : return
					if elemUIDs != self.__getElemUIDs() : 		# 如果跟之前的放入不一致
						self.__onPour()							# 则重新检查一遍
					else :
						BigWorld.player().cell.equipPour( elemUIDs )
				# "使用已绑定的韵灵琥珀灌注装备，装备将会变为绑定的，是否继续？"
				self.__showMessage( 0x0eac, MB_YES_NO, confirmToPour )
		else :
			BigWorld.player().cell.equipPour( elemUIDs )

	def __getElemUIDs( self ) :
		"""
		检查确认后放入的东西是否已变动
		"""
		pyItems = [ self.__pyEquip, self.__pyStone ]
		return [ e.itemInfo.uid for e in pyItems if e.itemInfo is not None ]

	def __calcCost( self ) :
		"""
		计算所需金钱
		"""
		equip = self.__pyEquip.itemInfo
		if equip is None :
			self.__pyCost.money = 0
			return
		stone = self.__pyStone.itemInfo
		if stone is None :
			self.__pyCost.money = 0
			return
		cost = equip.level**2 * equip.quality**2 * 10			# 策划的计算公式
		self.__pyCost.money = cost

	# -------------------------------------------------
	def __onKitbagUpdateItem( self, itemInfo ) :
		"""
		背包更新物品
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			pyItem.update( itemInfo )
			self.__calcCost()

	def __onKitbagRemoveItem( self, itemInfo ) :
		"""
		背包移除物品
		"""
		pyItem = self.__getPyItemByUID( itemInfo.uid )
		if pyItem is not None :
			self.__lockItem( itemInfo, False )
			pyItem.update( None )
			self.__calcCost()

	def __getPyItemByUID( self, uid ) :
		"""
		根据UID查找界面上是否有该物品
		"""
		pyItems = [ self.__pyEquip, self.__pyStone ]
		for pyItem in pyItems :
			if pyItem.itemInfo is None : continue
			if pyItem.itemInfo.uid == uid : return pyItem

	def __lockItems( self, locked ) :
		"""
		打开/关闭界面时改变背包中对应物品的颜色
		"""
		pyItems = [ self.__pyEquip, self.__pyStone ]
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
		self.__pyEquip.update( None )
		self.__pyStone.update( None )
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
		if itemInfo.id not in [ csconst.EQUIP_EXTRACT_PROITEM ] :
			# "请放入韵灵琥珀。"
			self.__showMessage( 0x0ead )
			return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcCost()
		self.pyParent.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","casketWindow" ) )

	def onEquipDrop__( self, pyTarget, pyDropped ) :
		"""
		拖放到装备格
		"""
		itemInfo = pyDropped.itemInfo
		if not ( itemInfo.isEquip and itemInfo.level >= csconst.EQUIP_EXTRACT_LEVEL_MIN \
			and itemInfo.quality in csconst.EQUIP_EXTRACT_QUALITYS ) :
				# "请放入60级以上且品质在粉色以上的装备。"
				self.__showMessage( 0x0ea8 )
				return
		if pyTarget.itemInfo is not None :
			self.__lockItem( pyTarget.itemInfo, False )
		pyTarget.update( itemInfo )
		self.__lockItem( itemInfo, True )
		self.__calcCost()
		self.pyParent.clearIndications()
		rds.opIndicator.fireRegIdtsOfTrigger( ( "gui_sub_panel_visible","casketWindow" ) )

	def onItemRemove__( self, pyItem ) :
		"""
		右击移除物品
		"""
		if pyItem.itemInfo is None : return
		self.__lockItem( pyItem.itemInfo, False )
		pyItem.update( None )
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

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
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
		pyItems = [ self.__pyEquip, self.__pyStone ]
		for pyItem in pyItems:
			pyItem.update( None )

	def showDragItemIndication( self, idtId, itemType ):
		if itemType == Const.CASKET_WINDOW_EQUIP :#装备
			equip = self.__pyEquip.itemInfo
			if equip is None :
				toolbox.infoTip.showHelpTips( idtId, self.__pyEquip )
				self.pyParent.addVisibleOpIdt( idtId )
		elif itemType == Const.CASKET_WINDOW_STONE:#石头
			stone = self.__pyStone.itemInfo
			if stone is None:
				toolbox.infoTip.showHelpTips( idtId, self.__pyStone )
				self.pyParent.addVisibleOpIdt( idtId )
				
	def showOkIndication( self, idtId ):
		equip = self.__pyEquip.itemInfo
		if equip is None:return
		stone = self.__pyStone.itemInfo	
		if pyStone.itemInfo is not None :	
			toolbox.infoTip.showHelpTips( idtId, self.__pyBtnOk )
			self.pyParent.addVisibleOpIdt( idtId )
						
