# -*- coding: gb18030 -*-
#
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.FrameEx import HFrameEx
from guis.common.RootGUI import RootGUI
from AbstractTemplates import Singleton
from ItemsFactory import SkillItem
import skills as Skill
import csconst
import csdefine

ITEM_WIDTH = 39.0

SPACE_TYPES = [csdefine.SPACE_TYPE_BEFORE_NIRVANA, csdefine.SPACE_TYPE_CHALLENGE,csdefine.SPACE_TYPE_TEACH_KILL_MONSTER, csdefine.SPACE_TYPE_PLOT_LV40, csdefine.SPACE_TYPE_DANCECOPY_CHALLENGE, csdefine.SPACE_TYPE_DANCECOPY_PARCTICE]

class MasterSkBar( Singleton, RootGUI, HFrameEx ):
	def __init__( self ):
		bar = GUI.load( "guis/general/quickbar/masterskbar.gui" )
		uiFixer.firstLoadFix( bar )
		RootGUI.__init__( self, bar )
		HFrameEx.__init__( self, bar )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "BOTTOM"
		self.moveFocus = True
		self.focus = True
		self.crossFocus = True
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = False
		self.__pyItems = []
		elements = bar.elements
		self.constWidth = elements["frm_l"].size.x + elements["frm_r"].size.x
		self.minWidth_ =  self.constWidth + ITEM_WIDTH
		self.__initialize( bar )
		self.addToMgr( "masterSkBag" )

	def dispose( self ) :
		RootGUI.dispose( self )

	def __initialize( self, bar ):
		self.position = bar.position
		self.__pyItemsPanel = PyGUI( bar.itemsPanel )
		self.__pyItemsPanel.width = bar.elements["frm_bg"].size.x

	def onShow( self, skills ):
		self.r_top = -0.5052
		self.r_left = -0.1445
		self.v_dockStyle	= "BOTTOM"
		self.h_dockStyle	= "CENTER"
		if not self.visible:
			self.visible = True
		for index, skillID in enumerate( skills ):
			skill = Skill.getSkill( skillID )
			skillInfo = SkillItem( skill )
			item = GUI.load( "guis/general/quickbar/masteritem.gui" )
			uiFixer.firstLoadFix( item )
			pyItem = MasterSkill( item )
			self.__pyItems.append( pyItem )
			self.__pyItemsPanel.addPyChild( pyItem )
			pyItem.top = 0.0
			pyItem.left = ( pyItem.width - 2.0 )*index
			pyItem.update( skillInfo )
		amount = len( self.__pyItems )
		self.__pyItemsPanel.width = self.__pyItems[amount-1].right
		self.width = self.__pyItemsPanel.width + self.constWidth - 1.0

	def onHide( self ):
		if self.visible:
			self.visible = False
		for pyItem in self.__pyItems:
			pyItem.update( None )
			self.__pyItemsPanel.delPyChild( pyItem )
		self.__pyItems = []
		self.width = self.minWidth_
		elements = self.getGui().elements
		self.__pyItemsPanel.width = elements["frm_bg"].size.x

	@classmethod
	def __onEnterMasterSpace( SELF, skills, spaceType ):
		print "------------------------>>__onEnterMasterSpace",spaceType,skills
		if not spaceType in SPACE_TYPES: #10级剧情副本在系统机能栏中显示
			SELF.inst.onShow( skills )

	@classmethod
	def __onLeaveMasterSpace( SELF ):
		SELF.inst.onHide()

	@classmethod
	def __onAddMasterSk( SELF, index, skill ):
		SELF.inst.addSkill( index, skill )

	@classmethod
	def __onRemoveMasterSk( SELF, index ):
		SELF.inst.removeSkill( index )

	__triggers = {}
	@staticmethod
	def registerEvents() :
		SELF = MasterSkBar
		SELF.__triggers["EVT_ON_ENTER_SPECIAL_COPYSPACE"] = SELF.__onEnterMasterSpace
		SELF.__triggers["EVT_ON_CLOSE_COPY_INTERFACE"] = SELF.__onLeaveMasterSpace
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, macroName, *args ) :
		SELF.__triggers[macroName]( *args )

	def onLeaveWorld( self ):
		self.onHide()

	def onRoleEnterWorld( self ):
		pass

MasterSkBar.registerEvents()

# ------------------------------------------------------------------------
from guis.controls.SkillItem import SkillItem as BOItem
from guis.controls.StaticText import StaticText
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from guis.otheruis.AnimatedGUI import AnimatedGUI
import csdefine


class MasterSkill( PyGUI ):
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pySkillItem = Item( item.icon )
		self.__pyFrame = PyGUI( item.itemFrame )

	def update( self, skillInfo ):
		self.__pySkillItem.update( skillInfo )

class Item( BOItem ):
	def __init__( self, item ):
		BOItem.__init__( self, item )
		self.__gbIndex = 0
		self.focus = True
		self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True
		self.selectable = True

		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False

		self.__pyStAmount = StaticText( item.lbAmount )
		self.__pyStAmount.text = ""

		self.__pyOverCover = AnimatedGUI( item.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )					# 动画播放一次，共8帧
		self.__pyOverCover.cycle = 0.4										# 循环播放一次的持续时间，单位：秒
		self.__pyCDCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )

		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( item )

	def subclass( self, item ):
		BOItem.subclass( self, item )
		self.__initialize( item )
		return True

	def __initialize( self, item ):
		if item is None : return

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

	def update( self, itemInfo ):
		BOItem.update( self, itemInfo )
		if itemInfo is not None:
			cdInfo = itemInfo.getCooldownInfo()
			self.__pyCDCover.unfreeze( *cdInfo )
		else:
			self.__pyCDCover.reset( 0 )

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
	def onLClick_( self, mods ):
		BOItem.onLClick_( self, mods )
		if self.itemInfo is None : return
		self.itemInfo.spell()

	def onDragStart_( self, pyDragged ):
		BOItem.onDragStart_( self, pyDragged )
		return True

	def onDragStop_( self, pyDragged ):
		BOItem.onDragStop_( self, pyDragged )
		return True

	def onDrop_( self, pyTarget, pyDropped ) :
		BOItem.onDrop_( self, pyTarget, pyDropped )
		return True

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