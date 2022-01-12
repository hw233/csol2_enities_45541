# -*- coding: gb18030 -*-
# $Id: ArtiRefine.py $

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from ContentPanel import ContentPanel
from AbstractTemplates import Singleton
from config.client.msgboxtexts import Datas as mbmsgs
import GUIFacade
import csconst
import ItemTypeEnum

class ArtiRefine( Singleton, Window ):

	__triggers = {}

	def __init__( self ):
		wnd = GUI.load( "guis/general/npctalk/artirefine.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.canBeUpgrade_ 	 = True
		self.escHide_ 		 = True
		self.__trapID = 0
		self.__initialize( wnd )
		self.addToMgr( "artiRefine" )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_ArtiRefine :
			INFO_MSG( str( self ) )

	def __initialize( self, wnd ):
		self.__pyContentPanel = ContentPanel( wnd.contentPanel.clipPanel, wnd.contentPanel.sbar )
		self.__pyContentPanel.spacing = 8.0

		self.__pyBtnRefine = HButtonEx( wnd.btnRefine )
		self.__pyBtnRefine.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnRefine.enable = False
		self.__pyBtnRefine.onLClick.bind( self.__onArtiRefine )
		labelGather.setPyBgLabel( self.__pyBtnRefine, "NPCTalkWnd:ArtiRefine", "btnRefine" )

		self.__pyBtnCancel = HButtonEx( wnd.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancel )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "NPCTalkWnd:ArtiRefine", "btnCancel" )

		self.__pyRefItem = RefItem()

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setLabel( wnd.lbTitle, "NPCTalkWnd:ArtiRefine", "lbTitle" )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	@classmethod
	def __onShow( SELF ) :
		player = BigWorld.player()
		distance = csconst.COMMUNICATE_DISTANCE
		if hasattr( GUIFacade.getGossipTarget(), "getRoleAndNpcSpeakDistance" ):
			distance = GUIFacade.getGossipTarget().getRoleAndNpcSpeakDistance()
		SELF.inst.__trapID = player.addTrapExt( csconst.COMMUNICATE_DISTANCE, SELF.inst.__onEntitiesTrapThrough )#打开窗口后为玩家添加对话陷阱
		SELF.inst.show()

	def __delTrap( self ) :
		player = BigWorld.player()
		if self.__trapID :
			player.delTrap( self.__trapID )									#删除玩家的对话陷阱
			self.__trapID = 0

	def __onEntitiesTrapThrough( self, entitiesInTrap ):
		player = BigWorld.player()
		gossiptarget = GUIFacade.getGossipTarget()						#获取当前对话NPC
		if gossiptarget and gossiptarget not in entitiesInTrap:				#如果NPC离开玩家对话陷阱
			self.hide()														#隐藏当前窗口
			self.__delTrap()

	@classmethod
	def __onAddItem( SELF, itemInfo ):
		"""
		更新炼化物品格
		"""
		SELF.inst.__pyRefItem.updateInfo( itemInfo )
		SELF.inst.__pyBtnRefine.enable = itemInfo is not None
		kitbagID = itemInfo.kitbagID
		if kitbagID > -1 :
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, True )

	@classmethod
	def __onRemoveItem( SELF, itemInfo ):
		"""
		移除炼化装备
		"""
		if itemInfo is None:return
		uid = itemInfo.uid
		refineInfo = SELF.inst.__pyRefItem.itemInfo
		kitbagID = itemInfo.kitbagID
		if kitbagID > -1 :
			orderID = itemInfo.orderID
			ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, False )
		if refineInfo is None:return
		if refineInfo.uid == uid:
			SELF.inst.__pyRefItem.updateInfo( None )
			SELF.inst.__pyBtnRefine.enable = False

	@classmethod
	def __onUpdateItems( SELF, itemInfo ):
		if itemInfo is None:return
		uid = itemInfo.uid
		refineInfo = SELF.inst.__pyRefItem.itemInfo
		if refineInfo is None:return
		if refineInfo.uid == uid:
			SELF.inst.__pyRefItem.updateInfo( itemInfo )

	@classmethod
	def __onHide( SELF ):
		SELF.inst.hide()

	def __onArtiRefine( self ):
		itemInfo = self.__pyRefItem.itemInfo
		if itemInfo is None:return
		baseItem = itemInfo.baseItem
		GUIFacade.equipGodWeapon( baseItem )

	def __onCancel( self ):
		self.hide()
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@classmethod
	def registerEvents( SELF ) :
		SELF.__triggers["EVT_ON_SHOW_GOD_WEAPON_MAKER"] = SELF.__onShow
		SELF.__triggers["EVT_ON_ADD_REFINE_ITEM"] = SELF.__onAddItem
		SELF.__triggers["EVT_ON_ITEM_EQUIPED"] = SELF.__onRemoveItem
		SELF.__triggers["EVT_ON_REFINE_REMOVE_ITEM"] = SELF.__onRemoveItem
		SELF.__triggers["EVT_ON_KITBAG_REMOVE_ITEM"] = SELF.__onRemoveItem
		SELF.__triggers["EVT_ON_KITBAG_UPDATE_ITEM"] = SELF.__onUpdateItems
		SELF.__triggers["EVT_ON_GOD_WEAPON_MAKER_SUCCESS"] = SELF.__onHide
		SELF.__triggers["EVT_OPEN_GOSSIP_WINDOW"] = SELF.__onHide
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		SELF.__triggers[ evtMacro ]( *args )

	def show( self ) :
		self.__pyContentPanel.clear()
		explain = labelGather.getText( "NPCTalkWnd:ArtiRefine", "explain" )
		self.__pyContentPanel.appendText( explain )
		self.__pyContentPanel.appendGodWeapon( self.__pyRefItem )
		Window.show( self )

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()

	def hide( self ) :
		Window.hide( self )
		self.__pyContentPanel.clear()
		refineInfo = self.__pyRefItem.itemInfo
		if refineInfo:
			kitbagID = refineInfo.kitbagID
			if kitbagID > -1 :
				orderID = refineInfo.orderID
				ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, False )
		self.dispose()

	def onLeaveWorld( self ) :
		self.hide()

ArtiRefine.registerEvents()
# -------------------------------------------------------------
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.common.PyGUI import PyGUI

class RefItem( PyGUI ):
	def __init__( self ):
		refItem = GUI.load( "guis/general/npctalk/refitem.gui" )
		uiFixer.firstLoadFix( refItem )
		PyGUI.__init__( self, refItem )
		self.__pyItemBg = PyGUI( refItem.itemBg )
		self.__pyItem = Item( refItem.item, self )
		self.__kitbagID = -1
		self.__orderID = -1
		self.__itemInfo = None

	def updateInfo( self, itemInfo ):
		self.__itemInfo = itemInfo
		self.__pyItem.update( itemInfo )
		if itemInfo:
			util.setGuiState( self.__pyItemBg.getGui(), ( 4, 2 ), ( 3, 1 ) )
		else:
			util.setGuiState( self.__pyItemBg.getGui(), ( 4, 2 ), ( 1, 1 ) )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItemInfo( self ):
		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	itemInfo = property( _getItemInfo, _setItemInfo )

# ----------------------------------------------------------------
class Item( BOItem ):
	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.focus = True
		self.__itemInfo = None
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __clearItem( self ):
		ECenter.fireEvent( "EVT_ON_REFINE_REMOVE_ITEM", self.itemInfo )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ) :
		BOItem.onRClick_( self, mods )
		if self.itemInfo is None:return
		self.__clearItem() # 移除任务提交物品
		return True

	def onDragStop_( self, pyDrogged ) :
		BOItem.onDragStop_( self, pyDrogged )
		if self.itemInfo is None:return
		if ruisMgr.isMouseHitScreen() :
			self.__clearItem( )
		return True

	def onDrop_( self,  pyTarget, pyDropped ) :
		if pyDropped.dragMark != DragMark.KITBAG_WND : return
		itemInfo = pyDropped.itemInfo
		quality = itemInfo.quality
		equipType = itemInfo.itemType
		level = itemInfo.level
		if level < 50 or \
		quality < ItemTypeEnum.CQT_GREEN or \
		not equipType in ItemTypeEnum.WEAPON_LIST:
			showAutoHideMessage( 3.0, mbmsgs[0x0411], "", pyOwner = self )
			return
		if self.itemInfo:
			kitbagID = self.itemInfo.kitbagID
			if kitbagID > -1 :
				orderID = self.itemInfo.orderID
				ECenter.fireEvent( "EVT_ON_ITEM_COLOR_CHANGE", kitbagID, orderID, False )
		ECenter.fireEvent( "EVT_ON_ADD_REFINE_ITEM", itemInfo )
		BOItem.onDrop_( self, pyTarget, pyDropped )
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BOItem.update( self, itemInfo )
		self.itemInfo = itemInfo

	def _getItemInfo( self ):

		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	itemInfo = property( _getItemInfo, _setItemInfo )			# get or set the checking state of the checkbox
