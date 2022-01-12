# -*- coding: gb18030 -*-

from guis import *
from guis.controls.Item import Item
from guis.common.Window import Window
from guis.controls.RichText import RichText
from guis.controls.ButtonEx import HButtonEx
from AbstractTemplates import Singleton
from ItemsFactory import ObjectItem
from LabelGather import labelGather
import GUIFacade
import ItemTypeEnum
from ArrowTip import ArrowTip
from HelpTipsSetting import TipsInfo
from HelpTipsSetting import helpTipsSetting

class UseTipWnd( Window ):

	__triggers = {}
	__cg_pyTipWnds = {}
	__arrowTipsInfo = TipsInfo({"style":0,"direction":2,"unframed":False})

	equips = { ItemTypeEnum.ITEM_WEAPON: "weapon",
				ItemTypeEnum.ITEM_ARMOR: "armor",
				ItemTypeEnum.ITEM_ORNAMENT:"ornament",
			}

	def __init__( self ):
		wnd = GUI.load("guis/tooluis/helptips/tipwnd.gui")
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = False
		self.addToMgr("useTipWnd")
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		self.__pyItem = Item( wnd.item.item )
		self.__pyRtName = RichText( wnd.rtName )
		self.__pyRtName.text = ""

		self.__pyRtWarn = RichText( wnd.rtWarn )
		self.__pyRtWarn.align = "C"
		self.__pyRtWarn.text = ""

		self.__pyBtnFunc = HButtonEx( wnd.btnFunc )
		self.__pyBtnFunc.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnFunc, "UseTipWnd:main", "nowWield" )
		self.__pyBtnFunc.onLClick.bind( self.__onTrigFunc )
		self._arrowTip = ArrowTip.buildArrowByInfo( self.__arrowTipsInfo, self.__pyBtnFunc )

		self.equipItem = None
		self.__mapId = -1

	# ------------------------------------------------------------
	# private
	# ------------------------------------------------------------
	def __onTrigFunc( self, pyBtn ):
		"""
		触发功能
		"""
		if pyBtn is None:return
		if self.equipItem is None:return
		GUIFacade.autoUseKitbagItem( self.equipItem )
		self.hide()

	def setEquipInfos( self, idtId, itemInfo ):
		self.__pyItem.update( itemInfo )
		equip = itemInfo.baseItem
		name = equip.name()
		warning = ""
		itemType = equip.getType()
		if equip.isEquip() and rds.statusMgr.isInWorld():
			self.equipItem = equip
			equipStr = self.equips.get( itemType, "unKnow" )
			typeStr = labelGather.getText( "UseTipWnd:main", equipStr )
			warning = labelGather.getText( "UseTipWnd:main", "betEquip" )%typeStr
			wdOrder = equip.getWieldOrders()[0]
			wdEquip = BigWorld.player().getItem_( wdOrder )
			self.__pyRtWarn.text = warning
			self.__pyRtName.text = name

	def show( self, idtId ):
		self.h_dockStyle = "CENTER"							# 水平居中显示
		self.__mapId = idtId
		self.__cg_pyTipWnds[idtId] = self
		Window.show( self )
		#toolbox.infoTip.showHelpTips( idtId, self.__pyBtnFunc )
		self._arrowTip.show( None, self.__pyBtnFunc, False )
		self._arrowTip.relocate()

	def hide( self ):
		Window.hide( self )
		#toolbox.infoTip.hideHelpTips( self.__mapId )
		self._arrowTip.dispose()
		self.dispose()

	def dispose( self ) :
		if self.__mapId in self.__cg_pyTipWnds :
			self.__cg_pyTipWnds.pop( self.__mapId )
		self.__mapId = -1
		Window.dispose( self )

	def onMove_( self, dx, dy ):
		Window.onMove_( self, dx, dy )
		#toolbox.infoTip.moveHelpTips( self.__mapId )
		self._arrowTip.relocate()

	@classmethod
	def __onTrigTipWnd( SELF, equipId, idtId ):
		"""
		角色背包添加物品触发
		"""
		if idtId in SELF.__cg_pyTipWnds : return
		tipsInfo = helpTipsSetting.getTipInfo( idtId )
		if not tipsInfo : return
		resTop = 230.0
		pyTipsWnd = SELF.__createTipsWnd( equipId, idtId )
		if pyTipsWnd is None:return
		pyTipsWnd.top = resTop + len( SELF.__cg_pyTipWnds )*(pyTipsWnd.height + 5.0 )
		pyTipsWnd.show( idtId )
		
	@classmethod
	def __onLeaveWorld( SELF ):
		pyTipsWnds = SELF.__cg_pyTipWnds.copy()
		for pyTipsWnd in pyTipsWnds.itervalues():
			pyTipsWnd.hide()
			

	@staticmethod
	def __createTipsWnd( equipId, idtId ):
		player = BigWorld.player()
		equip = player.findItemFromNKCK_( equipId )
		if equip is None:return
		itemInfo = ObjectItem( equip )
		pyTipWnd = UseTipWnd()
		pyTipWnd.setEquipInfos( idtId, itemInfo )
		return pyTipWnd

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def registerEvents( SELF ) :
		SELF.__triggers["EVT_ON_TRIGGER_WIELDTIP_WND"] = SELF.__onTrigTipWnd
		SELF.__triggers["EVT_ON_TRIGGER_PLAYER_LEAVE_WORLD"] = SELF.__onLeaveWorld

		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.__triggers[ evtMacro ]( *args )

UseTipWnd.registerEvents()