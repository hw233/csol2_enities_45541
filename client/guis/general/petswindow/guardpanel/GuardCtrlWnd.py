# -*- coding: gb18030 -*-
#
# $Id: GuardCtrlWnd.py

import GUIFacade
from guis import *
from AbstractTemplates import Singleton
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.RichText import RichText
from guis.controls.ODComboBox import ODComboBox
from guis.controls.StaticLabel import StaticLabel
from guis.controls.StaticText import StaticText
from guis.controls.Icon import Icon
from guis.otheruis.AnimatedGUI import AnimatedGUI
from guis.controls.CircleCDCover import CircleCDCover as CDCover
import csdefine

class GuardCtrlWnd( Singleton, Window ):
	
	__cc_triggers = {}
	
	__cc_start_pos = 20,100
	
	_format_maps = { csdefine.PG_FORMATION_TYPE_CIRCLE : "circle",
				csdefine.PG_FORMATION_TYPE_SNAKE : "snake",
				csdefine.PG_FORMATION_TYPE_FISH	 : "fish",
				csdefine.PG_FORMATION_TYPE_ARROW : "arrow",
				csdefine.PG_FORMATION_TYPE_GOOSE : "goose",
				csdefine.PG_FORMATION_TYPE_CRANE : "crane",
				csdefine.PG_FORMATION_TYPE_MOON	 : "moon",
				csdefine.PG_FORMATION_TYPE_EIGHT : "eight",
			}

	def __init__( self ):
		Singleton.__init__( self )
		wnd = GUI.load( "guis/general/petswindow/guardctrl.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__initialize( wnd )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "TOP"
		self.escHide_ = False
		self.addToMgr( "guardCtrlWnd" )
	
	def __initialize( self, wnd ):
		self.__pyGuards = {}
		self.__pyModes = {}
		
		self.__pyRtAirTrant = RichText( wnd.airBg.box )
		self.__pyRtAirTrant.text = ""
		
		self.__pyGuardCBox = ODComboBox( wnd.guardCBox )
		self.__pyGuardCBox.autoSelect = False
		self.__pyGuardCBox.ownerDraw = True
		self.__pyGuardCBox.pyBox_.foreColor = ( 236, 215, 157, 255 )
		self.__pyGuardCBox.onViewItemInitialized.bind( self.onInitialized_ )
		self.__pyGuardCBox.onDrawItem.bind( self.onDrawItem_ )
		self.__pyGuardCBox.onItemSelectChanged.bind( self.__onGuardSelected )
		
		self.__pyBtnAuto = Button( wnd.btnAuto )
		self.__pyBtnAuto.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnAuto.onLClick.bind( self.__onAutoLine )
		labelGather.setPyBgLabel( self.__pyBtnAuto, "PetsWindow:GuardPanel", "autoFormat" )
		
		self.pyLbTitle_.text = labelGather.getText( "PetsWindow:GuardPanel", "lbTitle" )
		self.pyCloseBtn_.visible = False
		
		for name, item in wnd.guardsPanel.children:
			if not name.startswith( "guard_" ):continue
			index = int( name.split( "_" )[1] )
			pyGuardItem = GuardItem( item.item )
			self.__pyGuards[index] = pyGuardItem
			
		for name, item in wnd.modesPanel.children:
			if not name.startswith( "mode_" ):continue
			index = int( name.split( "_" )[1] )
			pyModeItem = ModeItem( item.item, index )
			self.__pyModes[index] = pyModeItem

	def onInitialized_( self, pyViewItem ):
		pyLabel = StaticLabel()
		pyLabel.crossFocus = True
		pyLabel.foreColor = 236, 218, 157
		pyLabel.h_anchor = "CENTER"
		pyViewItem.addPyChild( pyLabel )
		pyViewItem.pyLabel = pyLabel

	def onDrawItem_( self, pyViewItem ):
		pyLabel = pyViewItem.pyLabel
		pyLabel.width = pyViewItem.width
		pyLabel.foreColor = 236, 218, 157
		pyLabel.left = 1.0
		pyLabel.top = 1.0
		cbItem = pyViewItem.listItem
		pyLabel.text = cbItem.name
	
	def __onGuardSelected( self, selIndex ):
		"""
		选择某个守护
		"""
		if selIndex < 0:return
		selItem = self.__pyGuardCBox.selItem
		if selItem is None:return
		player = BigWorld.player()
		formatType = selItem.formatType
		player.cell.setStarMapFormation( formatType )
		self.__pyGuardCBox.pyBox_.text = selItem.name
	
	def __onAutoLine( self, pyBtn ):
		"""
		自动布阵
		"""
		player = BigWorld.player()
		formation = 0
		player.cell.autoSetStarMapFormation( formation )
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		Window.show( self )
		player = BigWorld.player()
		self.__pyRtAirTrant.text = labelGather.getText( "PetsWindow:GuardPanel", "airTrant" )%player.accumPoint
		for formatType, name in self._format_maps.items():
			formatName = labelGather.getText( "PetsWindow:GuardPanel", name )
			name = labelGather.getText( "PetsWindow:GuardPanel", "format" )%formatName
			obcItem = OCBItem( formatType, name )
			self.__pyGuardCBox.addItem( obcItem )
		self.__pyGuardCBox.selItem = self.__pyGuardCBox.items[0]
		self.pos = self.__cc_start_pos

	def hide( self ) :
		Window.hide( self )
		self.dispose()
		self.__class__.releaseInst()
	
	def onRoleAccumChange( self, accumPoint ):
		self.__pyRtAirTrant.text = labelGather.getText( "PetsWindow:GuardPanel", "airTrant" )%accumPoint

	def onLeaveWorld( self ) :
		Window.onLeaveWorld( self )
		self.hide()
	
	def onUpateSkill( self, oldSkillID, skillInfo ):
		for index, pyGuard in self.__pyGuards.items():
			itemInfo = pyGuard.itemInfo
			if itemInfo is None:continue
			if itemInfo.id == oldSkillID:
				pyGuard.upate( skillInfo )
	
	def onRemoveSkill( self, skillInfo ):
		for index, pyGuard in self.__pyGuards.items():
			itemInfo = pyGuard.itemInfo
			if itemInfo is None:continue
			if itemInfo.id == skillInfo.id:
				pyGuard.upate( None )
	
	def onResolutionChanged( self, preReso ):
		self.pos = self.__cc_start_pos
	
	@classmethod
	def registerTriggers( SELF ) :
#		SELF.__cc_triggers[ "EVT_ON_TRIGGER_PG_CONTROL_PANEL" ] = SELF.__triggerVisible
#		SELF.__cc_triggers[ "EVT_ON_HIDE_PG_CONTROL_PANEL" ] = SELF.__triggerHide
		SELF.__cc_triggers[ "EVT_ON_PLAYERROLE_ACCUMPOINT_CHANGE" ] = SELF.__onRoleAccumChange
		SELF.__cc_triggers[ "EVT_ON_PLAYERROLE_UPDATE_SKILL" ] = SELF.__onUpateSkill
		SELF.__cc_triggers[ "EVT_ON_PLAYERROLE_REMOVE_SKILL" ] = SELF.__onRemoveSkill
		SELF.__cc_triggers[ "EVT_ON_RESOLUTION_CHANGED"] = SELF.__onResolutionChanged
		for key in SELF.__cc_triggers.iterkeys() :
			ECenter.registerEvent( key, SELF )

	@classmethod
	def onEvent( SELF, evtMacro, *args ) :
		handler = SELF.__cc_triggers.get( evtMacro )
		if handler is None and SELF.insted :
			handler = SELF.inst.__triggers.get( evtMacro )
		if handler is not None : handler( *args )

	@classmethod
	def __triggerVisible( SELF ) :
		SELF.inst.show()

	@classmethod
	def __triggerHide( SELF ) :
		SELF.inst.hide()
		
	@classmethod
	def __onRoleAccumChange( SELF, accumPoint ):
		"""
		角色起运点改变
		"""
		SELF.inst.onRoleAccumChange( accumPoint )

	@classmethod
	def __onUpateSkill( SELF, oldSkillID, skillInfo ):
		"""
		
		"""
		SELF.inst.onUpateSkill( oldSkillID, skillInfo )

	@classmethod
	def __onRemoveSkill( SELF, skillInfo ):
		"""
		
		"""
		SELF.inst.onRemoveSkill( skillInfo )
		
	@classmethod
	def __onResolutionChanged( SELF, preReso ):
		"""
		"""
		SELF.inst.onResolutionChanged( preReso )

# ----------------------------------------------------------------------
# 守护图标
# ----------------------------------------------------------------------
from guis.controls.Item import Item as BOItem
		
class GuardItem( BOItem ):
	
	def __init__( self, item ):
		BOItem.__init__( self, item )
		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.visible = False
		
		self.__pyLbAmount = StaticText( item.lbAmount )
		self.__pyLbAmount.text = ""
		
		self.__pyOverCover = AnimatedGUI( item.overCover )
		self.__pyOverCover.visible = False
		
		self.focus = True
		self.__itemInfo = None
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

	def onDrop_( self,  pyTarget, pyDropped ) :
		if pyDropped.dragMark != DragMark.GUARD_LIST_PANEL : return
		itemInfo = pyDropped.itemInfo
		self.update( itemInfo )
		BOItem.onDrop_( self, pyTarget, pyDropped )
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BOItem.update( self, itemInfo )
		if itemInfo :
			self.itemInfo = itemInfo

	def _getItemInfo( self ):

		return self.__itemInfo

	def _setItemInfo( self, itemInfo ):
		self.__itemInfo = itemInfo

	itemInfo = property( _getItemInfo, _setItemInfo )

# --------------------------------------------------------------------
# 攻击模式图标
# --------------------------------------------------------------------
class ModeItem( Icon ):
	
	_action_maps = { csdefine.PGNAGUAL_ACTION_MODE_FOLLOW:{ "dsp": "follow", "icon": "skill_physics_031" },
					csdefine.PGNAGUAL_ACTION_MODE_ATTACK:{ "dsp": "attack", "icon": "skill_physics_009" },
					csdefine.PGNAGUAL_ACTION_MODE_NEAR_GROUP:{ "dsp": "nearGroup", "icon": "skill_physics_051" },
					csdefine.PGNAGUAL_ACTION_MODE_NEAR_SINGLE:{ "dsp": "nearSingle", "icon": "skill_physics_044" },
					csdefine.PGNAGUAL_ACTION_MODE_FAR_PHYSIC:{ "dsp": "farPhysic", "icon": "skill_shoot_003" },
					csdefine.PGNAGUAL_ACTION_MODE_FAR_MAGIC:{ "dsp": "farMagic", "icon": "skill_mystery_025" },
					}
					
	def __init__( self, item, index ):
		Icon.__init__( self, item )
		self.focus = True
		self.crossFocus = True
		self.mode = index
		
		self.__pyLbAmount = StaticText( item.lbAmount )
		self.__pyLbAmount.text = ""

		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False
		
		iconTexure = self._action_maps[index]["icon"]
		self.icon = ( "icons/%s.dds"%iconTexure,((0.0, 0.0), (0.0, 0.5625), (0.5625, 0.5625), (0.5625, 0.0)))

		self.__pyOverCover = AnimatedGUI( item.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )					# 动画播放一次，共8帧
		self.__pyOverCover.cycle = 0.4										# 循环播放一次的持续时间，单位：秒
		self.__pyCDCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onMouseEnter_( self ) :
		Icon.onMouseEnter_( self )
		text = self._action_maps[self.mode]["dsp"]
		dsp = labelGather.getText( "PetsWindow:GuardPanel", text )
		toolbox.infoTip.showToolTips( self, dsp )

	def onMouseLeave_( self ) :
		Icon.onMouseLeave_( self )
		toolbox.infoTip.hide()
	
	def onLClick_( self, mods ) :
		Icon.onLClick_( self, mods )
		self.__pyCDCover.unfreeze( 1.0 )
		BigWorld.player().cell.setPGActionMode( self.mode )

class OCBItem:
	def __init__( self, formatType, name ):
		self.formatType = formatType
		self.name = name

GuardCtrlWnd.registerTriggers()