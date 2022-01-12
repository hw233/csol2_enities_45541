# -*- coding: gb18030 -*-
#
# $Id: HideBar.py,v 1.3 2008-08-26 02:18:33 huangyongwei Exp $

"""
implement HideBar
"""

import gbref
import csconst
from guis import *
import event.EventCenter as ECenter
from guis.common.RootGUI import RootGUI
from guis.controls.StaticText import StaticText
from guis.controls.Control import Control
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
import csdefine
from ItemsFactory import SkillItem
import skills as Skill
from config.ChallengeAvatarSkills import MapDatas as challengeMapDatas
from LabelGather import labelGather
from cscustom import Polygon

KEYS_MAP = {"MINUS":"-","EQUALS":"=","BACKSLASH":"\\"}

class HideBar( RootGUI ):
	def __init__( self ):
		hbar = GUI.load( "guis/general/quickbar/hidebar/bar.gui" )
		uiFixer.firstLoadFix( hbar )
		RootGUI.__init__( self, hbar )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "BOTTOM"
		self.moveFocus = True
		self.crossFocus = True
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ 		 = False
		self.__triggers = {}
		self.__pyItems = {}
		self.__spellingItems = []
		self.__invalidItems = []											# 选中的不可用技能
		self.__cancelCoverCBID = 0
		self.__registerTriggers()
		self.__initialize( hbar )
		self.lackitems = []
		

	def __initialize( self, hbar ):
		for name, item in hbar.children:
			if "hideItem_" not in name:continue
			index  = int( name.split( "_" )[1] )
			pyHItem = HBItem( index, item )
			pyHItem.onDragEnter.bind( self.__onItemDragEnter )
			pyHItem.onDragLeave.bind( self.__onItemDragLeave )
			pyHItem.update( None )
			scTag = "R_QB_GRID_" + str( ( index + 1 ) % 10 )
			scInfo = shortcutMgr.getShortcutInfo( scTag )
			scKeyStr = scInfo.shortcutString
			if scKeyStr in KEYS_MAP:
				scKeyStr = KEYS_MAP[scKeyStr]
			pyHItem.scTag = scTag
			pyHItem.setScKeyStr( scKeyStr )
			pyHItem.bindShortcut( scTag ) # 绑定快捷键
			self.__pyItems[index] = pyHItem

		self.__pyBtnDrag = Button( hbar.btnDrag )
		self.__pyBtnDrag.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnDrag.crossFocus = False
		self.__pyBtnDrag.moveFocus = False
		self.__pyBtnDrag.focus = False

	# -------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_QUICKBAR_UPDATE_ITEM"] = self.__onUpdateItem					# 当某个物品格被更新时触发
		self.__triggers["EVT_ON_VIEWINFO_CHANGED"] = self.__onOpenHideBar
		self.__triggers["EVT_ON_SHOW_SPELLING_COVER"]	= self.__onShowSpellingCover		# 高亮显示正在施放的技能
		self.__triggers["EVT_ON_HIDE_SPELLING_COVER"]	= self.__onHideSpellingCover		# 隐藏技能的高亮显示
		self.__triggers["EVT_ON_SHOW_INVALID_COVER"]	= self.__onShowInvalidCover			# 点击不可用技能时显示红色边框
		self.__triggers["EVT_ON_ENTER_SPECIAL_COPYSPACE"] = self.__onEnterSpaceCopy
		self.__triggers["EVT_ON_CLOSE_COPY_INTERFACE"] = self.__onLeaveSpaceCopy
		self.__triggers["EVT_ON_TEMP_SHORTCUT_TAG_SET"] = self.__onOnShortcutSet
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	# -----------------------------------------------------
	def __onShowSpellingCover( self, skillID ) :
		"""
		用高亮图标标识正在施放的技能
		@param		skillID	:	技能ID
		@type		skillID	:	SKILLID( INT64 )
		"""
		self.__onHideSpellingCover()
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is None : continue
			if pyItem in self.__spellingItems : continue
			if not hasattr( pyItem.itemInfo.baseItem, "getID" ) : continue
			if pyItem.itemInfo.baseItem.getID() == skillID :
				self.__spellingItems.append( pyItem )
				toolbox.itemCover.showSpellingItemCover( pyItem )

	def __onHideSpellingCover( self ) :
		"""
		隐藏图标的高亮显示状态
		"""
		for pyItem in self.__spellingItems :
			toolbox.itemCover.hideItemCover( pyItem )
		self.__spellingItems = []

	def __onShowInvalidCover( self, skillID ) :
		"""
		点击不可用技能时用红色边框显示
		"""
		BigWorld.cancelCallback( self.__cancelCoverCBID )
		self.__hideInvalidItemCovers()
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is None : continue
			if pyItem in self.__invalidItems : continue
			if not hasattr( pyItem.itemInfo.baseItem, "getID" ) : continue
			if pyItem.itemInfo.baseItem.getID() == skillID :
				self.__invalidItems.append( pyItem )
				toolbox.itemCover.showInvalidItemCover( pyItem )
		self.__cancelCoverCBID = BigWorld.callback( 1, self.__hideInvalidItemCovers )		# 标记在1秒后自动隐藏
	
	def __onEnterSpaceCopy( self, skills, spaceType ):
		isChallengeSpace = spaceType == csdefine.SPACE_TYPE_CHALLENGE
		if isChallengeSpace and len( skills ):
			player = BigWorld.player()
			itemInfos = player.qb_getItems()
			for index, pyItem in self.__pyItems.items():
				itemInfo = itemInfos.get( index, None )
				if itemInfo:
					itemId = itemInfo.id
					chMapSkill = self.__getChMapSkill( itemId, skills )
					if chMapSkill <= 0:continue
					skill = Skill.getSkill( chMapSkill )
					itemInfo = SkillItem( skill )
				pyItem.update( itemInfo )
				pyItem.updateIconState()
	
	def __onLeaveSpaceCopy( self ):
		itemInfos = BigWorld.player().qb_getItems()
		for index, pyItem in self.__pyItems.iteritems():	
			itemInfo = itemInfos.get( index, None )
			pyItem.update( itemInfo )
			pyItem.updateIconState()
			if not pyItem.dragFocus:
				pyItem.dragFocus = True
			if not pyItem.dropFocus:
				pyItem.dropFocus = True

	def __hideInvalidItemCovers( self ) :
		"""
		隐藏不可用技能的红色边框
		"""
		for pyItem in self.__invalidItems :
			toolbox.itemCover.hideItemCover( pyItem )
		self.__invalidItems = []

	def __onUpdateItem( self, gbIndex, itemInfo ):
		pyHBItem = self.__pyItems.get( gbIndex )
		if pyHBItem :
			pyHBItem.update( itemInfo )
			pyHBItem.updateIconState()
		self.__setBtnDragVisible()

	def __onOpenHideBar( self, infoKey, itemKey, oldValue, value ):
		if infoKey != "hideQuickBar":return
		if itemKey == "valid":
			self.visible = value

	def __onItemMouseEnter( self ):
		"""
		鼠标进入时显示底板
		"""
		self.__enterShow()

	def __onItemMouseLeave( self ):
		"""
		鼠标离开时隐藏底板
		"""
		if not self.isMouseHit():
			self.__leaveShow()

	def __onItemDragEnter( self, pyDragged ) :
		self.enterShow()

	def __onItemDragLeave( self, pyDragged ) :
		dragObj = rds.ruisMgr.dragObj
		if self.isMouseHit() or dragObj.dragMark == DragMark.QUICK_BAR:
			return
		self.leaveShow()

	def __getChMapSkill( self, itemId, skills ):
		"""
		根据当前快捷栏技能查找副本技能
		"""
		skillType = itemId/1000
		skLvStr = str(itemId)[6:]
		for key, value in challengeMapDatas.items():
			if value == skillType and key in skills:
				mapStr = str( key ) + skLvStr
				return int( mapStr )
		return 0

	def __onOnShortcutSet( self, tag, keyStr ):
		for pyItem in self.__pyItems.values():
			if pyItem.scTag == tag:
				if keyStr in KEYS_MAP:
					keyStr = KEYS_MAP[keyStr]
				pyItem.setScKeyStr( keyStr )
	
	def __setBtnDragVisible( self ):
		itemInfos = self.__getItemInfos()
		self.__pyBtnDrag.visible = len( itemInfos ) > 0
	
	def __getItemInfos( self ):
		itemInfos = []
		for pyItem in self.__pyItems.values():
			itemInfo = pyItem.itemInfo
			if itemInfo:
				itemInfos.append( itemInfo )
		return itemInfos

	def isMouseHit( self ) :
		return self.__isSubItemsMouseHit() or \
		self.__pyBtnDrag.isMouseHit()
	
	def __isSubItemsMouseHit( self ):
		for pyItem in self.__pyItems.values():
			if pyItem.isMouseHit() and pyItem.itemInfo:
				return True
		return False

	def onLClick_( self,mods ):
		if not self.isMouseHit():
			return False
		RootGUI.onLClick_( self,mods )
		return True

	def onDragStart_( self, pyDragged ) :
		return RootGUI.onDragStart_( self,pyDragged )

	def onDragStop_( self, pyDragged ) :
		return RootGUI.onDragStop_( self,pyDragged )

	def onMouseMove_( self, dx, dy ):
		itemInfos = self.__getItemInfos()
		return RootGUI.onMouseMove_( self, dx, dy )
	
	def onMouseEnter_( self ) :
		RootGUI.onMouseEnter_(self)
		return True

	def onMouseLeave_( self ):
		isMouseHit = False
		for pyItem in self.__pyItems.values():
			if pyItem.isMouseHit():
				isMouseHit = True
		if isMouseHit or self.__pyBtnDrag.isMouseHit() or \
		uiHandlerMgr.getCapUI() == self :
			return False
		for pyItem in self.__pyItems.values():
			if pyItem.itemInfo: continue
			pyItem.frameState = False
		self.__pyBtnDrag.visible = False
		RootGUI.onMouseLeave_(self)
		return True
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def enterShow( self ):
		for pyItem in self.__pyItems.itervalues():
			if pyItem.itemInfo:continue
			pyItem.frameState = True
		self.__pyBtnDrag.visible = True

	def leaveShow( self ):
		for pyItem in self.__pyItems.itervalues():
			if pyItem.itemInfo:continue
			pyItem.frameState = False
		self.__pyBtnDrag.visible = False

	def onLeaveWorld( self ) :
		"""
		角色离开世界时被调用
		"""
		self.hide()
		self.__onHideSpellingCover()
		for index, pyItem in self.__pyItems.iteritems():
			pyItem.update( None )

	def onEnterWorld( self ):
		"""
		角色进入世界时被调用
		"""
		self.visible = visible = rds.viewInfoMgr.getSetting( "hideQuickBar", "valid" )
		for pyItem in self.__pyItems.values():
			scTag = pyItem.scTag
			scInfo = shortcutMgr.getShortcutInfo( scTag )
			scKeyStr = scInfo.shortcutString
			if KEYS_MAP.has_key( scKeyStr ):
				scKeyStr = KEYS_MAP[scKeyStr]
			pyItem.setScKeyStr( scKeyStr )
		self.__pyBtnDrag.visible = False

	def hightlightLack( self ) :
		self.lackitems = [ pyItem for pyItem in self.__pyItems.values() if pyItem.itemInfo is None  ] 
		for pyItem in self.lackitems:
			if pyItem.itemInfo is None :
				toolbox.itemCover.showItemCover( pyItem )
	
	def hidelightLack( self ) :
		for pyItem in self.lackitems:
			if pyItem.itemInfo is None :
				toolbox.itemCover.hideItemCover( pyItem )
	
# --------------------------------------------------------------
from QBItem import QBItem

class HBItem( QBItem ) :
	def __init__( self, index, item ) :
		QBItem.__init__( self, item.item )
		self.__pyFrame = PyGUI( item.itemFrame )
		self.__pyStIndex = StaticText( item.stLabel )
		self.__pyStIndex.h_anchor = "RIGHT"
		self.__pyStIndex.font = "system_tiny.font"
		self.__pyStIndex.color = 255,255,255,255
		self.gbIndex = index

	def update( self, itemInfo ) :
		QBItem.update( self, itemInfo )
		self.__pyFrame.visible = itemInfo is not None
		self.__pyStIndex.visible = itemInfo is not None
		self.focus = itemInfo is not None

	def _getFrameState( self ):
		return self.__pyFrame.visible

	def _setFrameState( self, state ):
		self.__pyFrame.visible = state

	def onMouseEnter_( self ) :
		if self.itemInfo:
			self.visible = True
			self.pyTopParent.enterShow()
		QBItem.onMouseEnter_( self )

	def onMouseLeave_( self ) :
		QBItem.onMouseLeave_( self )
	
	def onDragStart_( self, pyDragged ) :
		QBItem.onDragStart_( self, pyDragged )
		self.pyTopParent.hightlightLack()
		rds.ruisMgr.quickBar.hightlightLack()
		return True
		
	def onDragStop_( self, pyDragged ) :
		QBItem.onDragStop_( self, pyDragged )
		self.pyTopParent.hidelightLack()
		rds.ruisMgr.quickBar.hidelightLack()
		return True
	
	def onLClick_( self, mods ):
		if self.itemInfo:
			QBItem.onLClick_( self, mods )
			
	def setScKeyStr( self, scTag ):

		self.__pyStIndex.text = labelGather.getText( "quickbar:skillBar", "skIndex" )%scTag

	frameState = property( _getFrameState, _setFrameState )