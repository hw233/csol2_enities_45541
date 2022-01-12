# -*- coding: gb18030 -*-
#
# $Id: PlayerInfo.py,v 1.42 2008-08-30 09:10:46 huangyongwei Exp $

"""
implement player info window
"""

import csdefine
import csconst
import csstatus
import event.EventCenter as ECenter
from guis import *
import Language
from LabelGather import labelGather
from cscustom import Polygon
from guis.common.PyGUI import PyGUI
from guis.common.RootGUI import RootGUI
from guis.controls.Button import Button
from guis.controls.Icon import Icon
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HProgressBar as ProgressBar
from guis.controls.ContextMenu import ContextMenu
from guis.controls.ContextMenu import DefMenuItem
from SpecMItem import SpecMItem
from SwitchEQPanel import SwitchEQPanel
import reimpl_playerInfo
import ItemTypeEnum
import GUIFacade
import csol
from config.skill.Skill.SkillDataMgr import Datas


# ----------------------------------------------------------------
# 调整属性字体尺寸修饰器
# ----------------------------------------------------------------
from AbstractTemplates import MultiLngFuncDecorator

PK_STATE_COLOR_MAP = {
	csdefine.PK_STATE_PROTECT			: ( 0, 255, 0, 255 ),
	csdefine.PK_STATE_ATTACK			: ( 153, 51, 0, 255 ),
	csdefine.PK_STATE_PEACE				: ( 255, 255, 255, 255 ),
	csdefine.PK_STATE_BLUENAME			: ( 0, 255, 255, 255 ),
	csdefine.PK_STATE_REDNAME			: ( 255, 0, 0, 255 ),
	csdefine.PK_STATE_ORANGENAME		: ( 255, 255, 0, 255 ),	# 原橙名，传说中的小红名，现在为黄名
	}

class deco_PlayerResetPyItems( MultiLngFuncDecorator ) :

	@staticmethod
	def locale_big5( SELF ) :
		"""
		繁体版下重新调整部分属性字体的尺寸
		"""
		SELF._PlayerInfo__pyLbHP.fontSize = 11
		SELF._PlayerInfo__pyLbHP.charSpace = -1

		SELF._PlayerInfo__pyLbMP.fontSize = 11
		SELF._PlayerInfo__pyLbMP.charSpace = -1

		SELF._PlayerInfo__pyLbLevel.fontSize = 11
		SELF._PlayerInfo__pyLbLevel.charSpace = -1


class PlayerInfo( RootGUI ) :
	__cc_pro_states = {}									# 不同职业的状态标记 mapping 位
	__cc_pro_states[csdefine.CLASS_FIGHTER]	 = ( 1, 1 )		# 战士
	__cc_pro_states[csdefine.CLASS_SWORDMAN] = ( 1, 2 )		# 剑客
	__cc_pro_states[csdefine.CLASS_ARCHER]	 = ( 2, 1 )		# 射手
	__cc_pro_states[csdefine.CLASS_MAGE]	 = ( 2, 2 )		# 法师

	_quality_filter = {ItemTypeEnum.CQT_BLUE: ( labelGather.getText( "PlayerInfo:main", "cqt_blue"), ( 0, 229, 233, 255 ) ),
						ItemTypeEnum.CQT_GOLD: ( labelGather.getText( "PlayerInfo:main", "cqt_gold"),( 255, 251, 127, 255 ) ),
						ItemTypeEnum.CQT_PINK: ( labelGather.getText( "PlayerInfo:main", "cqt_pink"),( 245, 16, 199, 255 ) ),
						ItemTypeEnum.CQT_GREEN: ( labelGather.getText( "PlayerInfo:main", "cqt_green"),( 33, 225, 25, 255 ) )
					}

	_pk_modes = { 
			csdefine.PK_CONTROL_PROTECT_RIGHTFUL: ( labelGather.getText( "PlayerInfo:main", "protect_rightful"), ( 0, 254, 102, 255 ) ),
			csdefine.PK_CONTROL_PROTECT_JUSTICE: ( labelGather.getText( "PlayerInfo:main", "protect_justiceful"), ( 180, 255, 0, 255 ) ),
			csdefine.PK_CONTROL_PROTECT_NONE: ( labelGather.getText( "PlayerInfo:main", "protect_none"), ( 254, 1, 0, 255 ) ),
			}

	_pickup_modes = { csdefine.TEAM_PICKUP_STATE_FREE: labelGather.getText( "PlayerInfo:main", "state_free"),
					csdefine.TEAM_PICKUP_STATE_ORDER: labelGather.getText( "PlayerInfo:main", "state_order"),
					csdefine.TEAM_PICKUP_STATE_SPECIFY: labelGather.getText( "PlayerInfo:main", "state_specify")
					}

	__captain_mark_texture_normal = "guis/general/playerinfo/applicantbtn.tga"
	__captain_mark_texture_flash = "guis/general/playerinfo/captainflashmark.texanim"

	def __init__( self ) :
		wnd = GUI.load( "guis/general/playerinfo/window.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "TOP"
		self.__teamProtected = None #组队保护按钮
		self.__initialize( wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ 		 = False
		self.moveFocus		 = False
		self.__time_interval = 0.1
		self.__triggers = {}
		self.__registerTriggers()
		self.__resetPyItems()
		self.__needEnergy = float ( Datas.__getitem__( 322538001 ).get( "param3" ) )  # 获取使用一次冲刺技能所消耗的能量值

	def __initialize( self, wnd ) :
		self.__pyHeader = PyGUI( wnd.head )

		self.__pySuitsPanel = SwitchEQPanel( wnd.pnl_switchEq )

		self.__pyApplicantBtn = Button( wnd.applicantBtn )
		self.__pyApplicantBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyApplicantBtn.onLClick.bind( self.__showTeamApplicant )

		self.__pyCaptainMark = PyGUI( wnd.captainMark )
		self.__pyCaptainMark.visible = False

		self.__pyClassMark = Icon( wnd.classMark )
		self.__pyClassMark.crossFocus = True
		self.__pyClassMark.onMouseEnter.bind( self.__onShowClass )
		self.__pyClassMark.onMouseLeave.bind( self.__onHideClass )
		self.__pyClassMark.visible = False

		self.__pyLbName = StaticText( wnd.lbName )
		self.__pyLbName.text = ""
#		self.__pyLbName.h_anchor = 'CENTER'

		self.__pyLbLevel = StaticText( wnd.lbLevel )
		self.__pyLbLevel.fontSize = 12
		self.__pyLbLevel.text = ""
		self.__pyLbLevel.h_anchor = 'CENTER'

		self.__pyHPBar = ProgressBar( wnd.hpBar,self )

		self.__pyHPBar.value = 0
		self.__pyHPBar.crossFocus = True
		self.__pyLbHP = StaticText( wnd.lbHP )
		self.__pyLbHP.fontSize = 12
		self.__pyLbHP.text = ""
		self.__pyLbHP.h_anchor = 'CENTER'
		self.__pyLbHP.visible = True

		self.__pyMPBar = ProgressBar( wnd.mpBar,self )
		self.__pyMPBar.crossFocus = True
		self.__pyMPBar.value = 0

		self.__pyLbMP = StaticText( wnd.lbMP )
		self.__pyLbMP.fontSize = 12
		self.__pyLbMP.text = ""
		self.__pyLbMP.h_anchor = 'CENTER'
		self.__pyLbMP.visible = True

		self.__pyENBar = ProgressBar( wnd.enBar, self )
		self.__pyENBar.value = 0
		self.__pyENBar.crossFocus = True
		self.__pyENBar.onMouseEnter.bind( self.__onMouseEnter )
		self.__pyENBar.onMouseLeave.bind( self.__onMouseLeave )

		self.__pyPkModeBtn = Button( wnd.pkModeBtn )
		self.__pyPkModeBtn.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyPkModeBtn.onLClick.bind( self.__onPopPkMenu )

		self.__pyPkModesMenu = self.__createPKMenu()
		self.__pyPkModesMenu.addBinder( self.__pyPkModeBtn )

		self.__pyCMenu = self.__createMenu()										# modified by hyw( 2008.04.17 )
		self.__pyCMenu.addBinder( self )
		self.__pyCMenu.onItemClick.bind( self.__onMenuItemClick )
		self.__pyCMenu.onItemCheckChanged.bind( self.__onMenuItemCheckChanged )
		
		self.__pyCamp = PyGUI( wnd.camp )
		self.__pyCamp.visible = False
		
		self.__clipper = wnd.combatCount.clipper
		self.__clipper.value = 0

		self.__rangePolygon = Polygon([
										( 5, 39 ), ( 18, 9 ), ( 33, 0 ), ( 64, 2 ),
										( 80, 14 ), ( 222, 15 ), ( 131, 24 ), ( 233, 48 ),
										( 223, 66 ), ( 83, 61 ), ( 61, 77 ), ( 41, 82 ),
										( 5, 61 ),
									])												# 定义多边形区域

	@deco_PlayerResetPyItems
	def __resetPyItems( self ) :
		"""
		重设部分UI元素的位置、大小、字体等属性
		"""
		pass											# 简体版本不作修改


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		register event triggers
		"""
		# update an item, args: kitBagIndex, itemIndex, itemInfo
		self.__triggers["EVT_ON_ROLE_ENTER_WORLD"] = self.__onRoleEnterWorld		# role enter world trigger
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onUpdateLevel			# level changed trigger
		self.__triggers["EVT_ON_ROLE_HP_CHANGED"] = self.__onUpdateHP				# HP changed trigger
		self.__triggers["EVT_ON_ROLE_MP_CHANGED"] = self.__onUpdateMP				# MP changed trigger
		self.__triggers["EVT_ON_ROLE_EN_CHANGED"] = self.__onUpdateEN				# NP changed trigger
#		self.__triggers["EVT_ON_ROLE_EXP_CHANGED"] = self.__onUpdateEXP				# EXP changed trigger
		self.__triggers["EVT_ON_TEAM_MEMBER_ADDED"] = self.__onMemberJoinIn
		self.__triggers["EVT_ON_TEAM_CAPTAIN_CHANGED"] = self.__onCaptainChanged	# captain state changed trigger
		self.__triggers["EVT_ON_TEAM_DISBANDED"] = self.__onTeamDisbanded			# when the team is disbanded, it it will be triggered
		self.__triggers["EVT_ON_ROLE_PKSTATE_CHANGED"] = self.__onPKStateChanged
		self.__triggers["EVT_ON_ROLE_PICKUPSTATE_CHANGED"] = self.__onPickUpStateChanged
		self.__triggers["EVT_ON_ROLE_PICKUP_QUALITY_CHANGE"] = self.__onPickUpQualityChange #在队长分配模式下品质改变通知
		self.__triggers["EVT_ON_ROLE_PKMODE_CHANGED"] = self.__onPKModeChanged
		self.__triggers["EVT_ON_SHOW_FIGHTFIRE"] = self.__showFightFire
#		self.__triggers["EVT_ON_PLAYER_UP_VEHICLE"] = self.__onVehicleUp				# 玩家上马
#		self.__triggers["EVT_ON_PLAYER_DOWN_VEHICLE"] = self.__onVehicleDown			# 玩家下马
		self.__triggers["EVT_ON_FOLLOW_STATE_CHANGE"] = self.__followStateChange		# 玩家组队跟随状态变化
		self.__triggers["EVT_ON_NOTIFY_NEW_TEAM_APPLICANT"] = self.__onNotifyNewTeamApplicant	# 有玩家申请入队
		self.__triggers["EVT_ON_SET_CAPTAIN_MARK_NORMAL"] = self.__setCaptainMarkNormal		# 队长标记停止闪烁
#		self.__triggers["EVT_ON_ROLE_ROLL_STATE_CHANGE"]	= self.__onRollStateChange	#是否拾取
		self.__triggers["EVT_ON_INIT_SUIT_DATAS"] = self.__onInitSuits		# 初始化角色的套装
		self.__triggers["EVT_ON_ENTER_SPECIAL_COPYSPACE"] = self.__onEnterSpaceCopy
		self.__triggers["EVT_ON_LEAVE_CHALLENGE_COPY"] = self.__onLeaveChalCopy
		self.__triggers["EVT_ON_ROLE_IS_PKMODE_LOCK"] = self.__onIsPkModeLock
		self.__triggers["EVT_ON_COPYMATCHER_SHIELD_TEAM_DISBANDED"] = self.__shieldTeamDisbanded #在副本组队中屏蔽队长解散队伍权利
		self.__triggers["EVT_ON_COPYMATCHER_CANCAL_SHIELD_TEAM_DISBANDED"] = self.__cancelShieldTeamDisbanded #出了副本组队的副本，取消屏蔽队长的解散队伍权利
		self.__triggers["EVT_ON_COMBATCOUNT_CHANGED"] = self.__combatCountChanged		#格斗点改变

		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )
	# -------------------------------------------------------------------

	def __createPKMenu( self ):
		"""
		创建PK模式设置
		"""
		pyMenu = ContextMenu()
		self.__pyModeChecks = {}
		pkModes = self._pk_modes.keys()
		pkModes.sort()
		for mode in pkModes:
			tuple = self._pk_modes.get( mode, None )
			if tuple is None:continue
			pyModeCheck = DefMenuItem( tuple[0], MIStyle.CHECKABLE )
			pyModeCheck.pkMode = mode
			pyModeCheck.clickCheck = False
			pyModeCheck.commonForeColor = tuple[1]
			pyModeCheck.highlightForeColor = tuple[1]
			pyModeCheck.disableForeColor = tuple[1]
			pyModeCheck.onLClick.bind( self.__changePkMode )
			pyMenu.pyItems.add( pyModeCheck )
			self.__pyModeChecks[mode] = pyModeCheck
		return pyMenu

	def __createMenu( self ) :
		"""
		创建右键菜单
		"""
#		menu = GUI.load("guis/general/playerinfo/pkmenue.gui")
		pyMenu = ContextMenu( )

		pyItem0 = SpecMItem( labelGather.getText( "PlayerInfo:main", "commseting") )
		pyItem01 = DefMenuItem( labelGather.getText( "PlayerInfo:main", "refusetrade"), MIStyle.CHECKABLE )
		pyItem01.Handler = self.__refuseTrade
		pyItem02 = DefMenuItem( labelGather.getText( "PlayerInfo:main", "refuseinvite"), MIStyle.CHECKABLE )
		pyItem02.Handler = self.__refuseInvite
		pyItem0.pySubItems.adds( [pyItem01, pyItem02] )

		pyItem1 = SpecMItem( labelGather.getText( "PlayerInfo:main", "distrimode") )
		for pickMode, pickText in self._pickup_modes.iteritems():
			pyPickItem = DefMenuItem( pickText, MIStyle.CHECKABLE )
			pyPickItem.pickMode = pickMode
			pyPickItem.clickCheck = False
			pyPickItem.onLClick.bind( self.__pickModeChange )
			pyItem1.pySubItems.add( pyPickItem )

		pyItem2 = SpecMItem( labelGather.getText( "PlayerInfo:main", "qualitymode") )
		pyItem2.enable = False
		self.__initQualities( pyItem2 )
		for pyQuaItem in pyItem2.pySubItems:
			pyQuaItem.onLClick.bind( self.__qualityPickUp )

#		pyItem3 = SpecMItem( "放弃物品:" )
#		pyItem3.enable = False
#		pyItem31 = DefMenuItem( "是", MIStyle.CHECKABLE )
#		pyItem31.rollState = False							#不需要roll，服务器端rollState为True则拾取，False不拾取，与界面相反
#		pyItem31.checked = False
#		pyItem31.onLClick.bind( self.__setRollState )
#		pyItem32 = DefMenuItem( "否", MIStyle.CHECKABLE )
#		pyItem32.rollState = True							#确定roll
#		pyItem32.checked = False
#		pyItem32.onLClick.bind( self.__setRollState )
#		pyItem3.pySubItems.adds( [pyItem31, pyItem32] )
		pySplitter0 = DefMenuItem( style = MIStyle.SPLITTER )
		pyItem3 = DefMenuItem( labelGather.getText( "PlayerInfo:main", "inviteMateFolllow"), MIStyle.COMMON )
		pyItem3.handler = self.__inviteAllFollow
		pyItem4 = DefMenuItem( labelGather.getText( "PlayerInfo:main", "quitMateFollow"), MIStyle.COMMON  )
		pyItem4.handler = self.__cancelFollow
		pySplitter1 = DefMenuItem( style = MIStyle.SPLITTER )
		pyItem5 = DefMenuItem( labelGather.getText( "PlayerInfo:main", "quitTeam"), MIStyle.COMMON )
		pyItem5.handler = self.__leaveTeam
		pyItem6 = DefMenuItem( labelGather.getText( "PlayerInfo:main", "disbandTeam"), MIStyle.COMMON  )
		pyItem6.handler = self.__disbandTeam

		pyMenu.pyItems.adds( [pyItem0, pyItem1, pyItem2, pySplitter0, pyItem3, pyItem4, pySplitter1, pyItem5, pyItem6] )
		return pyMenu

	@reimpl_playerInfo.deco_playerInfoInit
	def __initQualities( self, pyParent ):
		for quality, quaTuple in self._quality_filter.iteritems():
			pyQuaItem = DefMenuItem( quaTuple[0], MIStyle.CHECKABLE)
			quaColor = quaTuple[1]
			pyQuaItem.commonForeColor = quaColor
			pyQuaItem.highlightForeColor = quaColor
			pyQuaItem.disableForeColor = quaColor
			pyQuaItem.quality = quality
			pyQuaItem.clickCheck = False
#			pyQuaItem.onLClick.bind( self.__qualityPickUp )
			pyParent.pySubItems.add( pyQuaItem )
	# -------------------------------------------------
	def __onRoleEnterWorld( self, player ) :
		"""
		when role enter world, it will be called
		"""
		self.__pyLbName.text = player.getName()
		self.__pyHeader.texture = player.getHeadTexture()
		level = player.getLevel()
		self.__onUpdateLevel( level, level )
		self.__onUpdateHP( player.id, player.getHP(), player.getHPMax() )
		self.__onUpdateMP( player.getMP(), player.getMPMax() )
		self.__onUpdateEN( player.getEnergy(), player.getEnergyMax() )
		classRace = player.getClass()
		if self.__cc_pro_states.has_key( classRace ):
			self.__pyClassMark.visible = True
			util.setGuiState( self.__pyClassMark.getGui(), ( 2, 2 ), self.__cc_pro_states[classRace] )
		self.__combatCountChanged()
		color = PK_STATE_COLOR_MAP.get( player.pkState )
		if color:
			self.__pyLbName.color = color
			
	def __onUpdateLevel( self, oldLevel, level ) :
		"""
		update level
		"""
		player = BigWorld.player()
		profession = csconst.g_chs_class[player.getClass()]
		self.__pyLbLevel.text = str( level )

	def __onUpdateHP( self, entityID, hp, hpMax ) :
		"""
		update hp
		"""
		if BigWorld.player().id != entityID:
			return
		if hpMax <= 0 :
			self.__pyHPBar.value = 0
		else :
			self.__pyHPBar.value = float( hp ) / hpMax
		self.__pyLbHP.text = "%d/%d" % ( hp, hpMax )

	def __cancelFollow( self, pyItem ):
		"""
		退出组队跟随
		"""
		BigWorld.player().team_cancelFollow( csstatus.TEAM_CANCEL_FOLLOW )

	def __onUpdateMP( self, mp, mpMax ) :
		"""
		update mp
		"""
		if mpMax <= 0 :
			self.__pyMPBar.value = 0
		else :
			self.__pyMPBar.value = float( mp ) / mpMax
		self.__pyLbMP.text = "%d/%d" % ( mp, mpMax )

	def __onUpdateEN( self, en, enMax ):
		"""
		update energy
		"""
		if enMax <= 0:
			self.__pyENBar.value = 0
		else:
			value = float( en ) / enMax
			self.__pyENBar.value = value
			color = 255, 255, 255
			if value < self.__needEnergy / enMax:
				color = 255, 0, 0
			elif value == 1.0:
				color = 0, 255, 0
			else:
				color = 255, 255, 128
			self.__pyENBar.color = color

	def __onMouseEnter( self, pyPB ):
		"""
		"""
		player = BigWorld.player()
		en = player.getEnergy()
		enMax = player.getEnergyMax()
		reverValue = int( player.getEnergyReverValue() )
		if pyPB == self.__pyENBar:
			msg = labelGather.getText( "PlayerInfo:main", "energy" ) + "%d/%d" % ( en, enMax )
			msg += labelGather.getText( "PlayerInfo:main", "enBar" ) % reverValue
			toolbox.infoTip.showToolTips( self.__pyENBar, msg )

	def __onMouseLeave( self, pyPB ):
		"""
		"""
		toolbox.infoTip.hide()

	def __shieldTeamDisbanded( self ):
		if BigWorld.player().isCaptain():
			self.__pyCMenu.pyItems[8].enable = False
		
	def __cancelShieldTeamDisbanded( self ):
		if BigWorld.player().isCaptain():
			self.__pyCMenu.pyItems[8].enable = True		
			
	def __combatCountChanged( self ):
		"""
		格斗点数改变
		"""
		combatCount = BigWorld.player().combatCount
		self.__clipper.value = combatCount/ 5.0

	def __onCaptainChanged( self, captainID ) :
		"""
		update caption id
		"""
		player = BigWorld.player()
		isCaptain = player.id == captainID
		self.__pyCaptainMark.visible = isCaptain
		self.__pyCMenu.pyItems[1].enable = isCaptain
		for pyPickItem in self.__pyCMenu.pyItems[1].pySubItems:
			pyPickItem.enable = isCaptain
		self.__pyCMenu.pyItems[2].enable = player.pickUpState in [csdefine.TEAM_PICKUP_STATE_SPECIFY, csdefine.TEAM_PICKUP_STATE_ORDER]
		for pyQuatItem in self.__pyCMenu.pyItems[2].pySubItems:
			pyQuatItem.enable = player.isCaptain()
		self.__pyCMenu.pyItems[4].enable = player.isJoinTeam() and isCaptain
		self.__pyCMenu.pyItems[5].enable = player.isFollowing() or player.isTeamLeading()
		self.__pyCMenu.pyItems[7].enable = player.isJoinTeam()
		self.__pyCMenu.pyItems[8].enable = isCaptain and (not player.insideMatchedCopy)

	# ---------------------------------------
	def __onMemberJoinIn( self, joinner ) :
		"""
		if a teammember is join it will be called
		"""
		player = BigWorld.player()
		self.__pyCMenu.pyItems[0].enable = True
		self.__pyCMenu.pyItems[8].enable = player.isCaptain()
		self.__pyCMenu.pyItems[1].enable = player.isJoinTeam()
		for pyPickItem in self.__pyCMenu.pyItems[1].pySubItems:
			pyPickItem.enable = player.isCaptain()

	def __onTeamDisbanded( self ) :
		"""
		when the team is disbanded, it it will be triggered
		"""
		player = BigWorld.player()
		self.__pyCaptainMark.visible = False
		self.__pyCMenu.pyItems[1].enable = False
		self.__pyCMenu.pyItems[2].enable = False
		self.__pyCMenu.pyItems[4].enable = player.isCaptain()
		self.__pyCMenu.pyItems[5].enable = player.isFollowing() or player.isTeamLeading()
		self.__pyCMenu.pyItems[7].enable = player.isJoinTeam()
		self.__pyCMenu.pyItems[8].enable = player.isCaptain()
		self.__setCaptainMarkNormal()
		for pyPickItem in self.__pyCMenu.pyItems[1].pySubItems:
			pyPickItem.enable = player.isCaptain()

	def __onPKStateChanged( self, pkState ):
		color = PK_STATE_COLOR_MAP.get( pkState )
		if color:
			self.__pyLbName.color = color

	def __checkPKState( self ):
		player = BigWorld.player()

	def __onPKModeChanged( self, role, pkMode ):
		if role.id != BigWorld.player().id:return
		for mode, pyPkCheck in self.__pyModeChecks.iteritems():
			pyPkCheck.checked = pkMode == mode
			if mode == pkMode:
				modeSign = self._pk_modes[pkMode][0][0:2]
				foreColor = self._pk_modes[pkMode][1]
				self.__pyPkModeBtn.text = csol.asWideString( modeSign )
				self.__pyPkModeBtn.commonForeColor = foreColor
				self.__pyPkModeBtn.highlightForeColor = foreColor
				self.__pyPkModeBtn.pressedForeColor = foreColor

	def __changePkMode( self, pyItem ):
		player = BigWorld.player()
		if player is None: return
		if pyItem is None:return
		if pyItem.checked: return
		if player.state == csdefine.ENTITY_STATE_FIGHT:
			player.statusMessage( csstatus.ROLE_PK_NOT_ALLOW_CHANGE )
			return
		if player.isPkModelock:
			for mode, pyModeCheck in self.__pyModeChecks.items():
				pyModeCheck.checked = mode == pyItem.pkMode
				if mode == pyItem.pkMode:
					foreColor = ( 128, 128, 128, 255 )
					modeSign = self._pk_modes[mode][0][0:2]
					self.__pyPkModeBtn.text = csol.asWideString( modeSign )
					self.__pyPkModeBtn.commonForeColor = foreColor
					self.__pyPkModeBtn.highlightForeColor = foreColor
					self.__pyPkModeBtn.pressedForeColor = foreColor
					
			player.statusMessage( csstatus.ROLE_PK_MODE_LOCK_CHANGE, pyItem.text )
			
		player.cell.setPkMode( pyItem.pkMode )

	def __onPickUpStateChanged( self, state ):
		"""
		队伍物品分配模式改变
		"""
		player = BigWorld.player()
		for pySubItem in self.__pyCMenu.pyItems[1].pySubItems:
			pySubItem.enable = BigWorld.player().isCaptain()
			pickMode = pySubItem.pickMode
			pySubItem.checked = pickMode == state
		self.__pyCMenu.pyItems[1].textValue = self._pickup_modes[state]
		self.__pyCMenu.pyItems[2].enable = state in [csdefine.TEAM_PICKUP_STATE_SPECIFY, csdefine.TEAM_PICKUP_STATE_ORDER]
		if state != csdefine.TEAM_PICKUP_STATE_SPECIFY:
			self.__pyCMenu.pyItems[2].textValue = ""
		if state in [csdefine.TEAM_PICKUP_STATE_SPECIFY, csdefine.TEAM_PICKUP_STATE_ORDER] \
			and player.isCaptain(): #在队伍和指定模式下默认为蓝色品质
			player.base.changePickUpQuality( ItemTypeEnum.CQT_BLUE )

	def __onPickUpQualityChange( self, quality ):
		"""
		队长分配模式下，品质改变通知
		"""
		player = BigWorld.player()
		if player.pickUpState in [csdefine.TEAM_PICKUP_STATE_SPECIFY, csdefine.TEAM_PICKUP_STATE_ORDER]: #队伍为队长分配模式
			for pyQuaItem in self.__pyCMenu.pyItems[2].pySubItems:
				pyQuaItem.checked = pyQuaItem.quality == quality
		self.__setCMenuValColor( self.__pyCMenu, quality )

	@reimpl_playerInfo.deco_playerInfoSet
	def __setCMenuValColor( self, pyCMenu, quality ):
		pyCMenu.pyItems[2].textValue = self._quality_filter[quality][0]
		pyCMenu.pyItems[2].textColor = self._quality_filter[quality][1]

	def __onPopPkMenu( self ):
		self.__pyPkModesMenu.popup( self.__pyPkModeBtn )

	def __setRollState( self, pyChecker ):
		if pyChecker is None:return
		rollState = pyChecker.rollState
		BigWorld.player().cell.setRollState( rollState )

	def __showFightFire( self, show ):
		"""
		显示头像下方的火焰
		"""
		self.getGui().fire.visible = show

	def __onInitSuits( self, selIndex, suitDatas ) :
		"""
		服务器通知初始化角色套装数据
		"""
		self.__pySuitsPanel.initSuits( selIndex, suitDatas )
	
	def __onEnterSpaceCopy( self, skills, spaceType ):
		"""
		进入挑战副本，更改角色头像
		"""
		HEAD_MAPPINGS = { csdefine.GENDER_MALE:{"chiyou": "npcm1000",
											"huangdi": "npcm1002",
											"houyi": "npcm1004",
											"nuwo": "npcm1006",
										},
					csdefine.GENDER_FEMALE:{ "chiyou": "npcm1001",
											"huangdi": "npcm1003",
											"houyi": "npcm1005",
											"nuwo": "npcm1007"
										}
						}
		DEFAULT_MAPPINGS = { csdefine.CLASS_FIGHTER: "chiyou", 
							csdefine.CLASS_SWORDMAN: "huangdi", 
							csdefine.CLASS_ARCHER: "houyi", 
							csdefine.CLASS_MAGE: "nuwo" 
						}
		if spaceType == csdefine.SPACE_TYPE_CHALLENGE:
			player = BigWorld.player()
			gender = player.getGender()
			pro = player.getClass()
			avatar = player.avatarType
			if avatar == "":
				avatar = DEFAULT_MAPPINGS.get( pro, "" )
			headText = HEAD_MAPPINGS[gender][avatar]
			self.__pyHeader.texture = "maps/monster_headers/%s.dds"%headText
			
	def __onLeaveChalCopy( self ):
		"""
		离开副本的回调
		"""
		self.__pyHeader.texture = BigWorld.player().getHeadTexture()
		util.setGuiState( self.__pyHeader.getGui(), ( 1, 1 ), ( 1, 1 ) )
	
	def __onIsPkModeLock( self, oldValue, isLocked ):
		"""
		pk模式是否锁定
		"""
		if isLocked:								#被锁定
			lockColor = ( 128, 128, 128, 255 )
			for pyModeCheck in self.__pyModeChecks.values():
				pyModeCheck.commonForeColor = lockColor
				pyModeCheck.highlightForeColor = lockColor
				pyModeCheck.disableForeColor = lockColor
			self.__pyPkModeBtn.commonForeColor = lockColor
			self.__pyPkModeBtn.highlightForeColor = lockColor
			self.__pyPkModeBtn.pressedForeColor = lockColor
		else:
			curMode = csdefine.PK_CONTROL_PROTECT_NONE
			for pyModeCheck in self.__pyModeChecks.values():
				pkMode = pyModeCheck.pkMode
				color = self._pk_modes[pkMode][1]
				pyModeCheck.commonForeColor = color
				pyModeCheck.highlightForeColor = color
				pyModeCheck.disableForeColor = color
				if pyModeCheck.checked:
					curMode = pkMode
					BigWorld.player().cell.setPkMode( pkMode )
			curColor = self._pk_modes[curMode][1]
			self.__pyPkModeBtn.commonForeColor = curColor
			self.__pyPkModeBtn.highlightForeColor = curColor
			self.__pyPkModeBtn.pressedForeColor = curColor
					
			

#	def __onVehicleUp( self ):
#		"""
#		玩家上马
#		"""
#		self.pyItem6.enable = True

#	def __onVehicleDown( self ):
#		"""
#		玩家下马
#		"""
#		self.pyItem6.enable = False

	def __followStateChange( self ):
		"""
		组队跟随状态变化
		@param state : 是否在跟随中，BOOL
		"""
		player = BigWorld.player()
		self.__pyCMenu.pyItems[4].enable = player.isCaptain()								# 邀请组队跟随
		self.__pyCMenu.pyItems[5].enable = player.isFollowing() or player.isTeamLeading()	# 退出组队跟随

	# -------------------------------------------------
	def __onShowClass( self, pyMark ):
		player = BigWorld.player()
		classRace = player.getClass()
		if csconst.g_chs_class.has_key( classRace ):
			classText = csconst.g_chs_class[classRace]
			toolbox.infoTip.showToolTips( self, classText )

	def __onHideClass( self, pyMark ):
		toolbox.infoTip.hide()

	# -------------------------------------------------
	def __onMenuItemClick( self, pyItem ) :
		if hasattr( pyItem, "handler" ) :
			pyItem.handler( pyItem )

	def __onMenuItemCheckChanged( self, pyItem ) :
		if hasattr( pyItem, "Handler" ) :
			pyItem.Handler( pyItem )

	def __isSubItemsMouseHit( self ) :
		if self.__pyApplicantBtn.isMouseHit() :
			return True
		if self.__pyCaptainMark.isMouseHit() :
			return True
		if self.__pyClassMark.isMouseHit() :
			return True
		if self.__pyPkModeBtn.isMouseHit() :
			return True
		if self.__pySuitsPanel.isMouseHit() :
			return True
		if self.__pyENBar.isMouseHit():
			return True
		return False


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onLClick_( self,mods ):
		if not self.isMouseHit() : return False
		RootGUI.onLClick_( self,mods )
		entity = BigWorld.player()
		rds.targetMgr.bindTarget( entity )

	def onLMouseDown_( self, mods ) :
		RootGUI.onLMouseDown_( self, mods )
		return self.isMouseHit()


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def isMouseHit( self ) :
		"""
		判断鼠标是否点在多边形区域上
		"""
		return self.__rangePolygon.isPointIn( self.mousePos ) \
		or self.__isSubItemsMouseHit()

	def beforeStatusChanged( self, oldStatus, newStatus ) :
		"""
		系统状态改变通知
		"""
		if newStatus != Define.GST_IN_WORLD :
			self.__pyCMenu.close()

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onEnterWorld( self ) :
		player = BigWorld.player()
		pkMode = player.pkMode
		self.__pyCMenu.pyItems[7].enable = player.isInTeam()		# 退出队伍
		self.__pyCMenu.pyItems[8].enable = player.isCaptain()		# 解散队伍
		self.__pyCMenu.pyItems[4].enable = player.isCaptain()		# 邀请全队跟随
		self.__pyCMenu.pyItems[5].enable = player.isTeamLeading() or player.isFollowing()	# 退出组队跟随
		self.__pyCMenu.pyItems[1].enable = player.isCaptain() and player.isJoinTeam()		# 自由拾取
		for pyPickItem in self.__pyCMenu.pyItems[1].pySubItems:
			pyPickItem.enable = player.isCaptain()
		self.__pyCMenu.pyItems[2].enable = player.pickUpState == csdefine.TEAM_PICKUP_STATE_SPECIFY
		for pyQuatItem in self.__pyCMenu.pyItems[2].pySubItems:
			pyQuatItem.enable = player.isCaptain()
		self.__pyCMenu.pyItems[0].pySubItems[0].checked = not player.allowTrade #拒绝交易
		self.__pyCMenu.pyItems[0].pySubItems[1].checked = not player.allowInvite #拒绝邀请
		self.__setComiTextValue()
		modeSign = ""
		foreColor = ( 33, 225, 25, 255 )
		try:
			modeSign = self._pk_modes[pkMode][0][0:2]
			foreColor = self._pk_modes[pkMode][1]
			if player.isPkModelock:
				foreColor = ( 128,128,128,255 )
		except:
			pass

		self.__pyPkModeBtn.text = csol.asWideString( modeSign )
		self.__pyPkModeBtn.commonForeColor = foreColor
		self.__pyPkModeBtn.highlightForeColor = foreColor
		self.__pyPkModeBtn.pressedForeColor = foreColor
		for mode, pyPkCheck in self.__pyModeChecks.iteritems():
			pyPkCheck.checked = pkMode == mode
		self.__pySuitsPanel.initSuits( player.oksIndex, player.oksData )
		camp = player.getCamp()
		if camp > 0:
			self.__pyCamp.visible = True
			util.setGuiState( self.__pyCamp.getGui(), ( 1, 2 ), ( 1, camp ) )
		self.show()

	def onLeaveWorld( self ) :
		self.__pyCaptainMark.visible = False
		self.getGui().fire.visible = False
		self.hide()

	# ----------------------------------------------------------------
	# menu item handlers
	# ----------------------------------------------------------------
	def __leaveTeam( self, pyItem ) :
		"""
		离开队伍
		"""
		GUIFacade.leaveTeam()

	def __disbandTeam( self, pyItem ) :
		"""
		解散队伍
		"""
		GUIFacade.disbandTeam()

	def __inviteAllFollow( self, pyItem ):
		"""
		邀请队伍所有成员跟随
		"""
		GUIFacade.inviteAllfollow()

	# -------------------------------------------------
	def __refuseTrade( self, pyItem ) :
		"""
		拒绝交易
		"""

		player = BigWorld.player()
		player.allowTrade = not pyItem.checked
		if pyItem.checked :
			player.statusMessage( csstatus.ROLE_TRADE_REFUSED_TRADE )
		else :
			player.statusMessage( csstatus.ROLE_TRADE_ALLOW_TRADE )
		self.__setComiTextValue()

	def __refuseInvite( self, pyItem ) :
		"""
		拒绝邀请
		"""
		player = BigWorld.player()
		player.allowInvite = not pyItem.checked
		if pyItem.checked :
			player.statusMessage( csstatus.FRIEND_REFUSED_INVATE )
		else :
			player.statusMessage( csstatus.FRIEND_ALLOW_INVATE )
		self.__setComiTextValue()

	def __setComiTextValue( self ):
		amount = 0
		valueText = ""
		checkIndexs = []
		for index, pySubItem in enumerate( self.__pyCMenu.pyItems[0].pySubItems ):
			if pySubItem.checked:
				amount += 1
				checkIndexs.append( index )
		if amount >= self.__pyCMenu.pyItems[0].pySubItems.count:
			valueText = labelGather.getText( "PlayerInfo:main", "allForbid")
		elif amount <= 0:
			valueText = labelGather.getText( "PlayerInfo:main", "allAllow")
		else:
			valueText = self.__pyCMenu.pyItems[0].pySubItems[checkIndexs[0]].text
		self.__pyCMenu.pyItems[0].textValue = valueText

	# -------------------------------------------------
	def __pickModeChange( self, pyItem ):
		"""
		设置组队拾取模式
		"""
		pickMode = pyItem.pickMode
		GUIFacade.setPickUpState( pickMode )

	def __qualityPickUp( self, pyItem ):
		quality = pyItem.quality
		player = BigWorld.player()
		player.base.changePickUpQuality( quality )

	def __disMountVehicle( self, pyItem ):
		"""
		取消共骑
		"""
		player = BigWorld.player()
		if player is None: return
		vehicle = player.vehicle
		if vehicle is None: return
		if vehicle.getHorseMan() is player:
			player.cell.retractVehicle()
		else:
			player.cell.disMountAsPassenger()

	def __onNotifyNewTeamApplicant( self ) :
		"""
		有人申请加入队伍
		"""
		self.__pyApplicantBtn.texture = self.__captain_mark_texture_flash
		self.__pyApplicantBtn.setStatesMapping( UIState.MODE_R1C1 )

	def __setCaptainMarkNormal( self ) :
		self.__pyApplicantBtn.texture = self.__captain_mark_texture_normal
		self.__pyApplicantBtn.setStatesMapping( UIState.MODE_R2C2 )

	def __onRollStateChange( self, rollState ):
		"""
		在轮流拾取是否弹出roll
		"""
		for pyChecker in self.__pyCMenu.pyItems[2].pySubItems:
			pyChecker.checked = pyChecker.rollState == rollState
			if pyChecker.rollState == rollState:
				self.__pyCMenu.pyItems[2].textValue = pyChecker.text

	def __showTeamApplicant( self ) :
		"""
		"""
		ECenter.fireEvent( "EVT_ON_SHOW_TEAM_INFO_WND" )
