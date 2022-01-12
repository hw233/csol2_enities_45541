# -*- coding: gb18030 -*-
#
# $Id: AutoFightBar.py,v 1.15 2008-08-26 02:18:33 huangyongwei Exp $

import event.EventCenter as ECenter
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from AutoFightItem import AutoFightItem
from LabelGather import labelGather
from ItemsFactory import SkillItem
import skills as Skills
import csconst
import csdefine
import csstatus

class GuardsBar( PyGUI ):
	
	def __init__( self, qb ):
		PyGUI.__init__( self, qb )
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyItems = {}
		self.__spellingItems = []
		self.__invalidItems = []
		self.__cancelCoverCBID = 0
		self.__initialize( qb )

	def __initialize( self, qb ) :
		for name, item in qb.children :
			if "item_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyItem = GuardItem( item.icon, self )
			pyItem.index = index
			description = labelGather.getText( "quickbar:guardsBar", "tipsGuardItem" )
			pyItem.description = description
			pyItem.onLMouseDown.bind( self.__onBarMouseDown )
			pyItem.onMouseEnter.bind( self.__onBarMouseEnter )
			pyItem.onMouseLeave.bind( self.__onBarMouseLeave )
			self.__pyItems[index] = pyItem

	# -------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_SPELLING_COVER"]	= self.__onShowSpellingCover		# 高亮显示正在施放的技能
		self.__triggers["EVT_ON_HIDE_SPELLING_COVER"]	= self.__onHideSpellingCover		# 隐藏技能的高亮显示
		self.__triggers["EVT_ON_SHOW_INVALID_COVER"]	= self.__onShowInvalidCover			# 点击不可用技能时显示红色边框
		self.__triggers["EVT_ON_PLAYER_ADD_MAPSKILL"]	= self.__onRoleAddMapSkill			# 增加守护技能
		self.__triggers["EVT_ON_PLAYER_REMOVE_MAPSKILL"]	= self.__onRoleRemoveMapSkill	# 移除守护技能
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __onUpdateItem( self, gbIndex, itemInfo ) :
		player = BigWorld.player()
		if self.__pyItems.has_key( gbIndex ):
			pyItem = self.__pyItems[gbIndex]
			pyItem.update( itemInfo )
			pyItem.updateIconState()
			
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

	def __hideInvalidItemCovers( self ) :
		"""
		隐藏不可用技能的红色边框
		"""
		for pyItem in self.__invalidItems :
			toolbox.itemCover.hideItemCover( pyItem )
		self.__invalidItems = []

	def __onBarMouseDown( self ) :
		"""
		鼠标点击则浮动框消失
		"""
		toolbox.infoTip.hide()

	def __onBarMouseEnter( self, pyItem ) :
		"""
		鼠标进入则浮动框出现
		"""
		toolbox.infoTip.showItemTips( self, pyItem.description )

	def __onBarMouseLeave( self ) :
		"""
		鼠标离开则浮动框消失
		"""
		toolbox.infoTip.hide()
	
	def __onRoleAddMapSkill( self, index, skillID ):
		"""
		增加守护技能
		"""
		if index in self.__pyItems:
			skill = Skills.getSkill( skillID )
			skInfo = SkillItem( skill )
			pyItem = self.__pyItems[index]
			pyItem.update( skInfo )
	
	def __onRoleRemoveMapSkill( self, index ):
		"""
		移除守护技能
		"""
		if index in self.__pyItems:
			pyItem = self.__pyItems[index]
			pyItem.update( None )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.visible = False
		self.__onHideSpellingCover()
		for index, pyItem in self.__pyItems.iteritems() :
			pyItem.gbIndex = index
			self.__onUpdateItem( index, None )

	def onEnterWorld( self ) :
		self.__pyOpenBtn.visible = True
		self.__pyCloseBtn.visible = False
	
	def initMapSkills( self, skills ):
		for index, skillID in skills.items():
			pyItem = self.__pyItems.get( index, None )
			if pyItem is None:continue
			skill = Skills.getSkill( skillID )
			skInfo = SkillItem( skill )
			pyItem.update( skInfo )
	
	def reset( self ):
		for index, pyItem in self.__pyItems.iteritems() :
			self.__onUpdateItem( index, None )

# ----------------------------------------------------------------------
# 守护图标
# ----------------------------------------------------------------------
from guis.controls.Item import Item as BOItem
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from guis.otheruis.AnimatedGUI import AnimatedGUI
from guis.controls.StaticText import StaticText

class GuardItem( BOItem ):
	
	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.dragMark = DragMark.GUARD_QUICK_BAR
		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.visible = False
		
		self.__pyLbAmount = StaticText( item.lbAmount )
		self.__pyLbAmount.text = ""
		
		self.__pyOverCover = AnimatedGUI( item.overCover )
		self.__pyOverCover.visible = False
		
		self.focus = True
		self.__itemInfo = None
		self.index = -1
		self.__triggers = {}
		self.__registerTriggers()
	
	def __clearItem( self ):
		self.update( None )

	# ----------------------------------------------------------------
	# about event
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_BEGIN_COOLDOWN"] = self.__beginCooldown
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )
		self.__triggers = {}

	def __beginCooldown( self, cooldownType, lastTime ) :
		"""
		when cooldown triggered, it will be called
		"""
		itemInfo = self.itemInfo
		if itemInfo is None :
			return
		if itemInfo.isCooldownType( cooldownType ) :
			cdInfo = itemInfo.getCooldownInfo()
			self.__pyCover.unfreeze( *cdInfo )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
		
	def onRClick_( self, mods ) :
		BOItem.onRClick_( self, mods )
		if self.itemInfo:
			self.itemInfo.spell()
		return True

	def onLClick_( self, mods ) :
		BOItem.onLClick_( self, mods )
		if self.itemInfo:
			self.itemInfo.spell()
		return True

	def onDragStop_( self, pyDrogged ) :
		BOItem.onDragStop_( self, pyDrogged )
		if ruisMgr.isMouseHitScreen():
			self.update( None )
		return True

	def onDrop_( self, pyTarget, pyDropped ) :
		player = BigWorld.player()
		if pyDropped.dragMark == DragMark.GUARD_LIST_PANEL:
			itemInfo = pyDropped.itemInfo
			index = pyTarget.index
			skillID = itemInfo.id
			player.addMapSkill( index, skillID )
		elif pyDropped.dragMark == DragMark.GUARD_QUICK_BAR :
			if pyTarget.itemInfo:
				tIndex = pyTarget.index
				tSkillID = pyTarget.itemInfo.id
				dIndex = pyDropped.index
				dSkillID = pyDropped.itemInfo.id
				player.addMapSkill( tIndex, dSkillID )
				player.addMapSkill( dIndex, tSkillID )
			else:
				tIndex = pyTarget.index
				dIndex = pyDropped.index
				dSkillID = pyDropped.itemInfo.id
				player.addMapSkill( tIndex, dSkillID )
				player.removeMapSkill( dIndex )
		BOItem.onDrop_( self, pyTarget, pyDropped )
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BOItem.update( self, itemInfo )
		self.itemInfo = itemInfo

	def updateIconState( self ):
		"""
		written by kebiao
		更新快捷栏图标的状态  红色,蓝色
		"""
		itemInfo = self.itemInfo
		if itemInfo is not None :
			# 快捷栏图标根据对该物品或者技能对目标使用的相关状态决定变色
			state = itemInfo.validTarget()
			if state in [ csstatus.SKILL_INTONATING, csstatus.SKILL_ITEM_INTONATING ]:
				# 为了提高效率 技能底层最先判断的是这些条件, 而我们这里除了下面几个条件以外全部视为技能合法
				# 这里需要指定去过滤这个条件才能够避免一些问题的所在
				pass
			elif state in [ csstatus.SKILL_NOT_READY, csstatus.SKILL_ITEM_NOT_READY ]:
				# 看看技能条件判断的先后顺序就明白了
				# 技能能够出这个提示表明 距离判断已经合法了
				itemInfo.activeState_ = 0
				self.color = ( 255, 255, 255, 255 )
			elif state == csstatus.SKILL_GO_ON:
				itemInfo.activeState_ = 0
				self.color = ( 255, 255, 255, 255 )
			elif state == csstatus.SKILL_OUTOF_MANA:
				# 到这里一般为法力不够 或者缺乏材料 显示蓝色
				itemInfo.activeState_ = 1
				self.color = ( 0.0, 80.0, 255.0, 255.0 )
			elif state == csstatus.SKILL_MISSING_ITEM:
				# 到这里一般为法力不够 或者缺乏材料 显示蓝色
				itemInfo.activeState_ = 2
				self.color = ( 0.0, 80.0, 255.0, 255.0 )
			else:
				# 到这里一般为距离不够 或者缺乏材料 显示红色
				itemInfo.activeState_ = 3
				self.color = ( 100, 100, 100, 250 )

	def onDetectorTrigger( self ) :
		"""目标距离侦测回调"""
		self.updateIconState()

	def _getItemInfo( self ):

		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	itemInfo = property( _getItemInfo, _setItemInfo )