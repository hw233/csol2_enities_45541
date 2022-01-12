# -*- coding: gb18030 -*-
#
# $Id: PickupBox.py Exp $

"""
implement pickup box
"""

from guis import *
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.ODPagesPanel import ODPagesPanel
from PickupItem import PickupItem
from PickupItem import PickupQuestItem
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from LabelGather import labelGather
import BigWorld
import Timer
import csdefine
import csconst
import GUIFacade

class PickupBox( Window ):

	_cc_views = ( 4, 1 )

	def __init__( self ):
		box = GUI.load( "guis/tooluis/pickupbox/box.gui" )
		uiFixer.firstLoadFix( box )
		Window.__init__( self, box )
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ 	= True
		self.__initialize( box )
		self.trapID_ = None										# 添加到玩家身上的陷阱ID
		self.triggers_ = {}
		self.registerTriggers_()

	def __initialize( self, box ):
		self.pyPicksPage_ = ODPagesPanel( box.itemsPanel, box.pgIdxBar )
		self.pyPicksPage_.onViewItemInitialized.bind( self.initListItem_ )
		self.pyPicksPage_.onDrawItem.bind( self.drawListItem_ )
		self.pyPicksPage_.rMouseSelect = True
		self.pyPicksPage_.onItemSelectChanged.bind( self.onPickItemSelected_ )
		self.pyPicksPage_.onItemRClick.bind( self.pickupItem_ )
		self.pyPicksPage_.selectable = True
		self.pyPicksPage_.viewSize = self._cc_views

		self.pyPickAllBtn_ = Button( box.pickBtn )
		self.pyPickAllBtn_.setStatesMapping( UIState.MODE_R4C1 )
		self.pyPickAllBtn_.onLClick.bind( self.onPickupAll )

		self.pyAllcateMenu_ = None

		# ---------------------------------------------
		# 设置标签
		# ---------------------------------------------
		labelGather.setLabel( box.lbTitle, "PickupBox:main", "miRbTitle" )				# 拾取
		labelGather.setPyBgLabel( self.pyPickAllBtn_, "PickupBox:main", "btnPickAll" )	# 全部拾取

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def initListItem_( self, pyViewItem ):
		pyPickup = PickupItem()
		pyViewItem.pyPickup = pyPickup
		pyViewItem.addPyChild( pyPickup )
		pyViewItem.dragFocus = False
		pyViewItem.focus = False
		pyPickup.left = 2.0
		pyPickup.top = 1.0
	
	def drawListItem_( self, pyViewItem ):
		pickData = pyViewItem.pageItem
		pyPickup = pyViewItem.pyPickup
		pyViewItem.focus = pickData is not None
		pyPickup.selected = pyViewItem.selected
		pyPickup.update( pickData )
	
	def __createMenu( self, index ) :
		"""
		创建右键战利品分配菜单
		"""
		pyMenu = ContextMenu()
		player = BigWorld.player()
		members = [ player ]
		teamMember = player.teamMember
		rangeMembers = player.entitiesInRange( 30, cnd = lambda ent : ( ent.__class__.__name__ == "Role" and ent.id in teamMember.keys() ) )
		members.extend( rangeMembers )
		manuList = []
		for m in members:
			playerID = m.id	# 组队成员ID
			playerName = m.playerName		# 组队成员名字
			pyItem = DefMenuItem( playerName, MIStyle.COMMON )
			pyItem.memberID = playerID
			pyItem.index = index
			pyItem.handler = self.__allocateItem
			manuList.append( pyItem )
		pyMenu.pyItems.adds( manuList )
		return pyMenu

	def __allocateItem( self, pyItem ):
		"""
		点击菜单上的名字，分配物品
		"""
		player = BigWorld.player()
		memberID = pyItem.memberID
		if BigWorld.entities.has_key( memberID ) and BigWorld.entities.has_key( player.currentItemBoxID ):
			BigWorld.entities[player.currentItemBoxID].cell.assignDropItem( pyItem.index, memberID )
		self.pyAllcateMenu_ = None

	def __onMenuItemClick( self, pyItem ) :
		if hasattr( pyItem, "handler" ) :
			pyItem.handler( pyItem )
	
	def onPickItemSelected_( self, index ):
		if index < 0:return
		selPickItem = self.pyPicksPage_.selItem
		for pyViewItem in self.pyPicksPage_.pyViewItems:
			itemIndex = pyViewItem.itemIndex
			pyPickup = pyViewItem.pyPickup
			pickData = pyViewItem.pageItem
			if pickData is None:continue
			pyPickup.selected = itemIndex == index
	
	def pickupItem_( self, pyViewItem ):
		if pyViewItem is None:return
		pyPickup = pyViewItem.pyPickup
		if pyPickup.limited:return
		player = BigWorld.player()
		pyPickup.selected = pyViewItem.pageItem is not None
		itemIndex = pyPickup.pyPickItems.index
		if BigWorld.entities.has_key( player.currentItemBoxID ):
			BigWorld.entities[player.currentItemBoxID].pickUpItemByIndex( itemIndex )
					
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ):
		self.triggers_["EVT_ON_GET_DROP_ITEMS"] = self.onGetDropItems_		# 获取掉落物品列表
		self.triggers_["EVT_ON_PICKUP_ONE_ITEM"] = self.onPickOneItem_		# 获取某一个物品的回调
		self.triggers_["EVT_ON_ROLE_PICKUP_DISTURBED"] = self.onHide_		# 隐藏掉落窗口
		self.triggers_["EVT_ON_CAPTAIN_ALLOCATE_ITEM"] = self.onShowAllocateMenu_
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )

	def deregisterTriggers_( self ) :
		"""
		deregister all events
		"""
		for key in self.triggers_.iterkeys() :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	def addTrap_( self ) :
		if self.trapID_ is not None:
			self.delTrap_()
		self.trapID_ = BigWorld.addPot(BigWorld.player().matrix,csconst.COMMUNICATE_DISTANCE, self.onEntitiesTrapThrough_ )#打开窗口后为玩家添加陷阱

	def delTrap_( self ) :
		if self.trapID_ is not None:
			BigWorld.delPot( self.trapID_ )									# 删除陷阱
			self.trapID_ = None

	def onEntitiesTrapThrough_( self, isEnter,handle ):
		if not isEnter:
			self.hide()
			
	# -------------------------------------------------
	def onGetDropItems_( self, itemBox ):
		self.pyPicksPage_.clearItems()
		for itemDict in itemBox:
			if not itemDict in self.pyPicksPage_.items:
				self.pyPicksPage_.addItem( itemDict )
		self.addTrap_()
		self.show()

	def onPickOneItem_( self, index ):
		for itemDict in self.pyPicksPage_.items:
			if itemDict['order'] == index:
				self.pyPicksPage_.removeItem( itemDict )
				break
		if len( self.pyPicksPage_.items ) <= 0:
			self.hide()

	def onHide_( self ):
		if self.visible:
			self.hide()

	def onClose_( self ):
		"""
		"""
		return Window.onClose_( self )

	def onShowAllocateMenu_( self, index ):
		self.pyAllcateMenu_ = self.__createMenu( index )
		self.pyAllcateMenu_.onItemClick.bind( self.__onMenuItemClick )
		self.pyAllcateMenu_.addBinder( self )
		self.pyAllcateMenu_.show()
	
	def onMove_( self, dx, dy ):
		Window.onMove_( self, dx, dy )
#		toolbox.infoTip.moveOperationTips( 0x0071 )
	# --------------------------------------------------
	# public
	# --------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.triggers_[eventMacro]( *args )

	def onLeaveWorld( self ):
		self.pyPicksPage_.clearItems()
		Window.hide( self )

	def onPickupAll( self ):
		player = BigWorld.player()
		if BigWorld.entities.has_key( player.currentItemBoxID ):
			for itemDict in self.pyPicksPage_.items:
				BigWorld.entities[player.currentItemBoxID].pickUpItemByIndex( itemDict["order"] )

	# -------------------------------------------------
	def show( self ):
		Window.show( self )
		pyPickup = self.pyPicksPage_.pyViewItems[0].pyPickup
		if pyPickup is None:return
#		toolbox.infoTip.showOperationTips( 0x0071, pyPickup.pyPickItems )

	def hide( self ):
		player = BigWorld.player()
		currItemBox = BigWorld.entities.get( player.currentItemBoxID, None )
		if currItemBox is not None :
			currItemBox.abandonBoxItems()
		self.pyPicksPage_.clearItems()
		player.currentItemBoxID = 0
		self.delTrap_()
		Window.hide( self )
		toolbox.infoTip.hideOperationTips( 0x0071 )

# --------------------------------------------------------------------
class PickupQuestBox( PickupBox ):
	"""
	"""
	def __init__( self ) :
		PickupBox.__init__( self )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __onGetCollectPointItems( self, itemDatas ):
		"""
		拾取采集物品 by 姜毅
		"""
		self.pyPicksPage_.clearItems()
		for itemData in itemDatas:
			if not itemData in self.pyPicksPage_.items:
				self.pyPicksPage_.addItem( itemData )
		self.show()

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def registerTriggers_( self ):
		"""
		"""
		self.triggers_["EVT_ON_GET_QUEST_ITEMS"] = self.onGetDropItems_
		self.triggers_["EVT_ON_PICKUP_ONE_QUEST_ITEM"] = self.onPickOneItem_
		self.triggers_["EVT_ON_ROLE_QUEST_PICKUP_DISTURBED"] = self.onHide_
		self.triggers_["EVT_ON_CAPTAIN_ALLOCATE_ITEM"] = self.onShowAllocateMenu_
		self.triggers_["EVT_ON_GET_COLLECT_POINT_ITEMS"] = self.__onGetCollectPointItems
		for key in self.triggers_ :
			ECenter.registerEvent( key, self )

	# -------------------------------------------------
	def initListItem_( self, pyViewItem ):
		pyPickup = PickupQuestItem()
		pyViewItem.pyPickup = pyPickup
		pyViewItem.addPyChild( pyPickup )
		pyViewItem.dragFocus = False
		pyViewItem.focus = False
		pyPickup.left = 2.0
		pyPickup.top = 1.0

	def drawListItem_( self, pyViewItem ):
		pickData = pyViewItem.pageItem
		pyPickup = pyViewItem.pyPickup
		pyViewItem.focus = pickData is not None
		pyPickup.selected = pyViewItem.selected
		pyPickup.update( pickData )

	def pickupItem_( self, pyViewItem ):
		if pyViewItem is None:return
		pyPickup = pyViewItem.pyPickup
		if pyPickup.limited:return
		player = BigWorld.player()
		pyPickup.selected = pyViewItem.pageItem is not None
		itemIndex = pyPickup.pyPickItems.index
		if BigWorld.entities.has_key( player.currentQuestItemBoxID ):
			BigWorld.entities[player.currentQuestItemBoxID].pickUpItemByIndex( itemIndex )
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onPickupAll( self ):
		bid = BigWorld.player().currentQuestItemBoxID
		if BigWorld.entities.has_key( bid ):
			for itemDict in self.pyPicksPage_.items:
				BigWorld.entities[bid].pickUpItemByIndex( itemDict["order"] )

	def hide( self ):
		player = BigWorld.player()
		currQuestItemBox = BigWorld.entities.get( player.currentQuestItemBoxID, None )
		if currQuestItemBox is not None :
			currQuestItemBox.abandonBoxQuestItems()
		player.currentQuestItemBoxID = 0
		PickupBox.hide( self )
