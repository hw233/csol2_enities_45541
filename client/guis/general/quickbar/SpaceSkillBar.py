# -*- coding: gb18030 -*-
#
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.FrameEx import HFrameEx
from guis.common.RootGUI import RootGUI
from guis.controls.StaticText import StaticText
from LabelGather import labelGather
import csdefine
import Timer
from ItemsFactory import SkillItem
import skills


class SpaceSkillBar( HFrameEx ):
	"""
	空间副本技能快捷条
	"""
		
	def __init__( self, bar, pyBinder = None ):
		HFrameEx.__init__( self, bar )
		self.moveFocus = False
		self.focus = True
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyItems = {}
		self.pyBinder = pyBinder
		self.__initialize( bar )

	def __initialize( self, bar ):
		pass

	# -------------------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ENTER_TOWER_DEFENCE_SPACE"] = self.__onEnterTowerDefenceSpace	#进入塔防副本
		self.__triggers["EVT_ON_ADD_TOWER_DEFENCE_SPACE_SKILL"] = self.__onAddTowerDefenceSpaceSkill 	#塔防副本增加技能
		self.__triggers["EVT_ON_END_TOWER_DEFENCE_SPACE_SKILL"] = self.__onEndTowerDefenceSpaceSkill	#清除塔防副本技能
		
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	# --------------------------------------------------			
	def __onEnterTowerDefenceSpace( self, skillNum ):
		self.__layoutItems( skillNum )
		self.pyBinder.autoFightBar.visible = False
		self.visible = True
			
	def __onAddTowerDefenceSpaceSkill( self, skillID, spaceType ):	
		pyItem = self.__getFreeItem()
		if pyItem is None:return
		skillInfo  = SkillItem( skills.getSkill( skillID ) )
		pyItem.update( skillInfo )
	
	def __onEndTowerDefenceSpaceSkill( self ):
		if self.pyBinder.autoBarShow:
			self.pyBinder.autoFightBar.visible = True
		for index in self.__pyItems.keys():
			pyItem = self.__pyItems.pop( index )
			self.delPyChild( pyItem )
		self.visible = False
		
	def __getFreeItem( self ):
		pyItem = None
		for pyItem in self.__pyItems.itervalues():
			if pyItem.itemInfo is None:
				return  pyItem
		return pyItem
		
	def __layoutItems( self, num ):
		"""
		排序技能格
		"""
		offset = 48.0
		for index in range( num ):
			item = GUI.load( "guis/general/quickbar/racebag/item.gui" )
			uiFixer.firstLoadFix( item )
			pySpaceSkillItem = SpaceSkillItem( item )
			self.addPyChild( pySpaceSkillItem, "item_%d"%index )
			pos = offset + index*40.0, 14.0
			pySpaceSkillItem.pos = pos
			gbIndex = index+1
			pySpaceSkillItem.gbIndex = gbIndex
			self.__pyItems[gbIndex] = pySpaceSkillItem
		self.width = offset + num*40.0 + 18.0

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.update( None )

	def onRoleEnterWorld( self ):
		pass

# ---------------------------------------------------
from guis.controls.Item import Item as BOItem
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from guis.otheruis.AnimatedGUI import AnimatedGUI
import csdefine


class SpaceSkillItem( PyGUI ):
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pyItem = Item( item.item )
	
	def update( self, itemInfo ):
		self.__pyItem.update( itemInfo )

	def _getGBIndex( self ) :
		return self.__pyItem.gbIndex

	def _setGBIndex( self, index ) :
		self.__pyItem.gbIndex = index

	def _getItemInfo( self ):
		return self.__pyItem.itemInfo

	gbIndex = property( _getGBIndex, _setGBIndex )
	itemInfo = property( _getItemInfo )

class Item( BOItem ):
	def __init__( self, item ):
		BOItem.__init__( self, item )
		self.__gbIndex = 0
		self.focus = True
		self.crossFocus = True
		self.dragFocus = False
		self.dropFocus = False
		self.selectable = True
		self.dragMark = DragMark.SPACE_SKILL

		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False

		self.__pyOverCover = AnimatedGUI( item.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )					# 动画播放一次，共8帧
		self.__pyOverCover.cycle = 0.4										# 循环播放一次的持续时间，单位：秒
		self.__pyCDCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )
		self.__dropEvents = {}
		self.__triggers = {}
		self.__registerTriggers()

	def dispose( self ):
		self.__pyCDCover.dispose()
		self.__deregisterTriggers()
		BOItem.dispose( self )

	def onMouseEnter_( self ):
		self.onDescriptionShow_()
		toolbox.itemCover.highlightItem( self )
		return True

	def onMouseLeave_( self ):
		BOItem.onMouseLeave_( self )
		return True

	def onDescriptionShow_( self ):
		dsp = self.description
		if dsp is None : return
		if dsp == [] : return
		if dsp == "" : return
		toolbox.infoTip.showItemTips( self, dsp )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_ROLE_BEGIN_COOLDOWN"] = self.__beginCooldown
		for trigger in self.__triggers.iterkeys():
			ECenter.registerEvent( trigger, self )

	def __deregisterTriggers( self ):
		for trigger in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( trigger, self )

	# -------------------------------------------------
	def __beginCooldown( self, cooldownType, lastTime ):
		"""
		handle cooldown message
		"""
		if self.itemInfo is None : return
		cdInfo = self.itemInfo.getCooldownInfo()
		self.__pyCDCover.unfreeze( *cdInfo )

	# -------------------------------------------------
	def onRClick_( self, mods ):
		BOItem.onRClick_( self, mods )
		self.onLClick_( mods )
		
	def spellItemToSelf( self ):
		"""
		自身使用法术
		"""
		if self.itemInfo is not None :
			self.itemInfo.spellToSelf()
			
	def spellItem( self ) :
		"""
		spell item
		"""
		if self.itemInfo:
			self.itemInfo.spell()
	
	def onLClick_( self, mods ):
		BOItem.onRClick_( self, mods )
		if self.itemInfo is None : return
		if BigWorld.isKeyDown( KEY_LALT ):
			self.spellItemToSelf()
		else :
			self.spellItem()
		return True
	
	def update( self, itemInfo ):
		BOItem.update( self, itemInfo )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getGBIndex( self ) :
		return self.__gbIndex

	def _setGBIndex( self, index ) :
		self.__gbIndex = index

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	gbIndex = property( _getGBIndex, _setGBIndex )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

