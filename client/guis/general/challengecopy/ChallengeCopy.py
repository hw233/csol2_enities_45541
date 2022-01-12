# -*- coding: gb18030 -*-
# $Id: ChallengeCopy.py, fangpengjun Exp $

from guis import *
from LabelGather import labelGather
from guis.common.RootGUI import RootGUI
from guis.common.PyGUI import PyGUI
from guis.controls.RichText import RichText
from guis.common.FlexExWindow import HVFlexExWindow
from guis.controls.Control import Control
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.SelectableButton import SelectableButton
from guis.controls.SelectorGroup import SelectorGroup
from config.client.msgboxtexts import Datas as mbmsgs
from config.client.ChallengeAvatar import Datas as AvatarDatas
from ItemsFactory import SkillItem as SkillInfo
from guis.controls.SkillItem import SkillItem as SKItem
from guis.ScreenViewer import ScreenViewer
import skills as Skill
import csdefine
import csconst
import random
import Timer
from Time import Time

AVATAR_MAPS = { csdefine.GENDER_MALE:{ "chiyou": "fighter_0",
										"huangdi": "swords_0",
										"houyi": "archer_0",
										"nuwo": "magic_0",
									},
				csdefine.GENDER_FEMALE:{ "chiyou": "fighter_1",
										"huangdi": "swords_1",
										"houyi":"archer_1",
										"nuwo":"magic_1"
									}
			}

RANK_DSP = 	{ csdefine.CHALLENGE_RANK_EASY: labelGather.getText( "challengecopy:main", "easy" ),
			csdefine.CHALLENGE_RANK_HARD: labelGather.getText( "challengecopy:main", "hard" ),
		}

class ChallengeCopy( RootGUI ):

	def __init__( self ):
		wnd = GUI.load( "guis/general/challengecopy/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		RootGUI.__init__( self, wnd )
		self.focus = False
		self.moveFocus = False
		self.escHide_ = False
		self.h_dockStyle = "HFILL"
		self.v_dockStyle = "VFILL"
		self.posZSegment = ZSegs.LMAX
		self.activable_ = True
		self.__pySkills = {}
		self.__pyTeamMates = {}
		self.__remainTimerID = 0
		self.endTime = 0.0
		self.__initialize( wnd )
		self.__triggers = {}
		self.__registerTriggers()

		# 添加清屏例外窗口
		ScreenViewer().addResistHiddenRoot(self)

	def __initialize( self, wnd ):
		labelGather.setLabel( wnd.infoPanel.profText,"challengecopy:main", "profText" )
		labelGather.setLabel( wnd.infoPanel.skillText,"challengecopy:main", "skillText" )
		self.__pyTeamPanel = PyGUI( wnd.teamPanel )
		self.__pyTeamPanel.h_dockStyle = "S_RIGHT"
		self.__pyTeamPanel.v_dockStyle = "S_BOTTOM"

		self.__pyInfoPanel = PyGUI( wnd.infoPanel )
		self.__pyInfoPanel.h_dockStyle = "S_CENTER"
		self.__pyInfoPanel.v_dockStyle = "S_TOP"
		self.__pyInfoPanel.focus = False
		self.__pyInfoPanel.moveFocus = False
		self.__pyInfoPanel.escHide_ = False
		self.__pyInfoPanel.visible = True

		self.__pyBottomPanel = PyGUI( wnd.bottomPanel )
		self.__pyBottomPanel.h_dockStyle = "S_CENTER"
		self.__pyBottomPanel.v_dockStyle = "S_BOTTOM"

		self.__pyRtProInfo = RichText( wnd.infoPanel.rtProInfo )
		self.__pyRtProInfo.maxWidth = self.__pyRtProInfo.width
		self.__pyRtProInfo.align = "L"
		self.__pyRtProInfo.lineFlat = "M"
		self.__pyRtProInfo.text = ""

		self.__pyBtnRandom = Button( wnd.infoPanel.btnRandom )
		self.__pyBtnRandom.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnRandom.onLClick.bind( self.__onRandom )

		self.__pyBtnReady = Button( wnd.infoPanel.btnReady )
		self.__pyBtnReady.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnReady.onLClick.bind( self.__onReady )

		self.__pyBtnChange = Button( wnd.infoPanel.btnChange )
		self.__pyBtnChange.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnChange.onLClick.bind( self.__onChange )

		self.__pyRanks = SelectorGroup()

		self.__pyRankCommon = SelectableButton( wnd.infoPanel.btnCommon )
		self.__pyRankCommon.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyRankCommon.rank = csdefine.CHALLENGE_RANK_EASY
		self.__pyRankCommon.visible = False

		self.__pyRankHero = SelectableButton( wnd.infoPanel.btnHero )
		self.__pyRankHero.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyRankHero.rank = csdefine.CHALLENGE_RANK_HARD
		self.__pyRankHero.visible = False

		self.__pyCommTip = Control( wnd.infoPanel.commTip )
		self.__pyCommTip.crossFocus = False
		self.__pyCommTip.rank = self.__pyRankCommon.rank
#		self.__pyCommTip.onMouseEnter.bind( self.__onRankEnter )
#		self.__pyCommTip.onMouseLeave.bind( self.__onRankLeave )

		self.__pyHeroTip = Control( wnd.infoPanel.heroTip )
		self.__pyHeroTip.crossFocus = False
		self.__pyHeroTip.rank = self.__pyRankHero.rank
#		self.__pyHeroTip.onMouseEnter.bind( self.__onRankEnter )
#		self.__pyHeroTip.onMouseLeave.bind( self.__onRankLeave )

		self.__pyRanks.addSelectors( self.__pyRankCommon, self.__pyRankHero )
#		self.__pyRanks.onSelectChanged.bind( self.__onSelRank )

		self.__pyBtnStart = Button( wnd.bottomPanel.btnStart )
		self.__pyBtnStart.setStatesMapping( UIState.MODE_R2C2 )
		self.__pyBtnStart.enable = False
		self.__pyBtnStart.onLClick.bind( self.__onStart )

		self.__pyStWarn = StaticText( wnd.infoPanel.stWarn )
		self.__pyStWarn.text = ""

		self.__pyRtRemain = RichText( wnd.infoPanel.rtRemain )
		self.__pyRtRemain.align = "C"
		self.__pyRtRemain.text = ""

		self.__pyAvatars = SelectorGroup()
		for name, item in wnd.infoPanel.children:
			if name.startswith( "skill_" ):
				index = int( name.split( "_" )[1] )
				pySkill = SkillItem( item )
				self.__pySkills[index] = pySkill
			if name.startswith( "avatar_" ):
				atype = name.split( "_" )[1]
				pyAvatar = SelectableButton( item )
				pyAvatar.setStatesMapping( UIState.MODE_R2C2 )
				pyAvatar.isOffsetText = True
				labelGather.setPyBgLabel( pyAvatar, "challengecopy:main", atype )
				pyAvatar.atype = atype
				pyAvatar.commonForeColor = ( 205, 174, 91, 255 )
				pyAvatar.selectedForeColor = ( 0, 255, 0, 255 )
				self.__pyAvatars.addSelector( pyAvatar )
		self.__pyAvatars.onSelectChanged.bind( self.__onSelAvatar )

		for name, item in wnd.teamPanel.children:
			if name.startswith( "teammate_" ):
				index = int( name.split( "_" )[1] )
				pyTeamMate = TeamMate( item )
				self.__pyTeamMates[index] = pyTeamMate

	# -------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_CHALLENGE_COPY"] = self.__toggleVisible
		self.__triggers["EVT_ON_MEMBER_SET_AVATAR"] = self.__onMemSetAvatar
		self.__triggers["EVT_ON_SET_SPACE_RANK"] = self.__onSetSpaceRank
		self.__triggers["EVT_ON_ENTER_SPECIAL_COPYSPACE"] = self.__onEnterSpaceCopy
		for trigger in self.__triggers :
			ECenter.registerEvent( trigger, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )
	# ------------------------------------------------
	def __toggleVisible( self, enterType ):
		"""
		触发显示
		"""
		if self.__remainTimerID > 0:
			self.__cancelTimer()
			self.__pyRtRemain.text = ""
		ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", False )
		self.visible = True
		rds.ruisMgr.chatWindow.visible = True
		player = BigWorld.player()
		gender = player.getGender()
		for pyAvatar in self.__pyAvatars.pySelectors:
			atype = pyAvatar.atype
			texturePath = "guis/general/challengecopy/avatars/%s.dds"%AVATAR_MAPS[gender][atype]
			pyAvatar.texture = texturePath
		self.__choiceDefAvatar()
		self.endTime = Time.time() + 30.0
		self.__remainTimerID = Timer.addTimer( 0, 1, self.__countdown )
		self.__pyStWarn.text = labelGather.getText( "challengecopy:main", "warn_0" )
		for pyMember in self.__pyTeamMates.values():
			pyMember.randomInfo()
		if enterType == csconst.SPACE_CHALLENGE_SHOW_TYPE_DEFAULT:
			isEnable = player.isCaptain() or len( player.teamMember ) <= 0
			self.__pyBtnStart.enable = isEnable
		else:
			self.__pyBtnStart.enable = True

	def __choiceDefAvatar( self ):
		"""
		默认选取英雄，与角色职业一致
		"""
		PRO_AVATARS = { csdefine.CLASS_FIGHTER: "chiyou",
					csdefine.CLASS_SWORDMAN: "huangdi",
					csdefine.CLASS_ARCHER: "houyi",
					csdefine.CLASS_MAGE: "nuwo"
				}
		player = BigWorld.player()
		pro = player.getClass()
		atype = PRO_AVATARS.get( pro )
		if atype is None:return
		for pyAvatar in self.__pyAvatars.pySelectors:
			if atype == pyAvatar.atype:
				self.__pyAvatars.pyCurrSelector = pyAvatar

	def __onMemSetAvatar( self, memberID, atype ):
		"""
		队友设置职业类型
		"""
		if BigWorld.player().id == memberID: #不显示玩家自己
			return
		sortTeams = sorted(self.__pyTeamMates.items(), key=lambda member:member[0], reverse = False )
		for member in sortTeams:
			pyMember = member[1]
			if pyMember.memberID == memberID: #队友更换英雄类型
				pyMember.updateInfo( atype, memberID )
				return
			if pyMember.atype == "" and pyMember.memberID < 0:
				pyMember.initeInfo( memberID, atype )#初始化队友信息
				break

	def __onSetSpaceRank( self, rank ):
		"""
		设置副本难度回调
		"""
		for pyRank in self.__pyRanks.pySelectors:
			if pyRank.rank == rank:
				self.__pyRanks.pyCurrSelector = pyRank

	def __onEnterSpaceCopy( self, skills, spaceType ):
		if self.__remainTimerID > 0:
			self.__cancelTimer()
		if spaceType == csdefine.SPACE_TYPE_CHALLENGE:
			self.visible = False
			ECenter.fireEvent( "EVT_ON_VISIBLE_ROOTUIS", True )
		for pyMember in self.__pyTeamMates.values():
			pyMember.clearInfo()
		for pyAvatar in self.__pyAvatars.pySelectors:
			pyAvatar.enable = True
			pyAvatar.selected = False

	def __onRandom( self ):
		"""
		随机选择英雄
		"""
		player = BigWorld.player()
		gender = player.getGender()
		avatars = AVATAR_MAPS[gender].keys()
		randType = random.choice( avatars )
		for pyAvatar in self.__pyAvatars.pySelectors:
			if pyAvatar.atype == randType:
				self.__pyAvatars.pyCurrSelector = pyAvatar
		pySelAvatar = self.__pyAvatars.pyCurrSelector
		for pyAvatar in self.__pyAvatars.pySelectors:
			if pyAvatar.atype == pySelAvatar.atype:
				continue
			pyAvatar.enable = False
		player.challengeSpaceSetAvatar( randType )

	def __onReady( self ):
		"""
		准备进入
		"""
		player = BigWorld.player()
		pyCurSelector = self.__pyAvatars.pyCurrSelector
		if pyCurSelector is None:return
		atype = pyCurSelector.atype
		player.challengeSpaceSetAvatar( atype )
		if player.enterType == csconst.SPACE_CHALLENGE_SHOW_TYPE_DEFAULT:
			if player.isCaptain():
				self.__pyStWarn.text = labelGather.getText( "challengecopy:main", "warn_2" )
			if len( player.teamMember ) and not player.isCaptain():
				self.__cancelTimer()
				self.__pyStWarn.text = labelGather.getText( "challengecopy:main", "warn_1" )
				self.__pyRtRemain.text = ""
			else:
				self.__pyStWarn.text = ""
		else:
			self.__pyStWarn.text = labelGather.getText( "challengecopy:main", "warn_0" )
		for pyAvatar in self.__pyAvatars.pySelectors:
			pyAvatar.enable = pyAvatar.atype == atype
		self.__pyBtnRandom.enable = False

	def __onChange( self, pyChange ):
		"""
		更换英雄
		"""
		player = BigWorld.player()
		for pyAvatar in self.__pyAvatars.pySelectors:
			pyAvatar.enable = True
			pyAvatar.selected = False
		player.challengeSpaceSetAvatar( "" )
		self.__pyBtnRandom.enable = True
		self.__pyBtnStart.enable = False

	def __onSelRank( self, pySelRank ):
		"""
		选择英雄难度模式
		"""
		if pySelRank is None:return
		rank = pySelRank.rank
		BigWorld.player().challengeSapceSetRank( rank )

	def __onStart( self, pyStart ):
		"""
		开始进入副本
		"""
		player = BigWorld.player()
		pySelAvatar = self.__pyAvatars.pyCurrSelector
		atype = pySelAvatar.atype
		player.challengeSpaceSetAvatar( atype )
		player.challengeSpaceEnter()

	def __onSelAvatar( self, pyAvatar ):
		"""
		选择英雄
		"""
		self.__pyBtnReady.enable = pyAvatar is not None
		self.__pyBtnStart.enable = pyAvatar is not None
		if pyAvatar is None:return
		atype = pyAvatar.atype
		proInfos = AvatarDatas.get( atype, None )
		if proInfos is None:return
		self.__pyRtProInfo.text = proInfos["info"]
		skills = proInfos["skills"]
		for index, skID in enumerate( skills ):
			pySkill = self.__pySkills.get( index, None )
			if pySkill is None:continue
			skill = Skill.getSkill( skID )
			skillInfo = SkillInfo( skill )
			pySkill.update( skillInfo )

	def __onRankEnter( self, pyTip ):
		"""
		鼠标进入
		"""
		if pyTip is None:return
		rank = pyTip.rank
		dsp = RANK_DSP.get( rank, "" )
		toolbox.infoTip.showToolTips( self, dsp )

	def __onRankLeave( self ):
		"""
		鼠标离开
		"""
		toolbox.infoTip.hide()

	def __countdown( self ):
		"""
		倒计时
		"""
		player = BigWorld.player()
		remain = int( self.endTime - Time.time() )
		self.__pyRtRemain.text = labelGather.getText( "challengecopy:main", "remain" )%remain
		if remain <= 0:
			self.__cancelTimer()
			atype = self.__getDefType()
			pySelAvatar = self.__pyAvatars.pyCurrSelector
			if pySelAvatar is not None:
				atype = pySelAvatar.atype
			player.challengeSpaceSetAvatar( atype )
			self.__pyRtRemain.text = ""
			if player.enterType == csconst.SPACE_CHALLENGE_SHOW_TYPE_DEFAULT:
				if player.isCaptain() or len( player.teamMember ) <= 0: #玩家是队长或者不在队伍
					player.cell.challengeSpaceEnter()
			else:
				player.cell.challengeSpaceEnter()

	def __cancelTimer( self ):
		Timer.cancel( self.__remainTimerID )
		self.__remainTimerID = 0

	def __getDefType( self ):
		"""
		获取默认英雄类型
		"""
		PRO_AVATARS = { csdefine.CLASS_FIGHTER: "chiyou",
					csdefine.CLASS_SWORDMAN: "huangdi",
					csdefine.CLASS_ARCHER: "houyi",
					csdefine.CLASS_MAGE: "nuwo"
				}
		player = BigWorld.player()
		pro = player.getClass()
		atype = PRO_AVATARS.get( pro, "" )
		return atype

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		self.visible = False
		self.__cancelTimer()
		for pyMember in self.__pyTeamMates.values():
			pyMember.clearInfo()

# --------------------------------------------------------------------------
class SkillItem( PyGUI ):
	def __init__( self, item ):
		self.__pySkItem = SKItem( item.skBg.skItem )
		self.__pySkBg = PyGUI( item.skBg )
		self.__pyStName = StaticText( item.skName )
		self.__pyStName.text = ""

	def update( self, skInfo ):
		self.__pySkItem.update( skInfo )
		self.__pyStName.text = skInfo.name

# --------------------------------------------------------------------------

MEMBER_HEADS = { csdefine.GENDER_MALE:{ "chiyou":( ( 1, 1 ), labelGather.getText( "challengecopy:main", "pro_fighter" ) ),
										"huangdi":( ( 1,3 ), labelGather.getText( "challengecopy:main", "pro_swords" ) ),
										"houyi":( ( 2, 2 ), labelGather.getText( "challengecopy:main", "pro_archer" ) ),
										"nuwo":( ( 3, 1 ), labelGather.getText( "challengecopy:main", "pro_magic" ) )
									},
				csdefine.GENDER_FEMALE:{ "chiyou":( ( 1, 2 ), labelGather.getText( "challengecopy:main", "pro_fighter" ) ),
										"huangdi":( ( 2, 1 ),labelGather.getText( "challengecopy:main", "pro_swords" ) ),
										"houyi":( ( 2, 3 ),labelGather.getText( "challengecopy:main", "pro_archer" ) ),
										"nuwo":( ( 3, 2 ),labelGather.getText( "challengecopy:main", "pro_magic" ) ),
									}
				}

class TeamMate( Control ):

	def __init__( self, item ):
		self.__pyHead = PyGUI( item.head )
		self.__pyHead.texture = ""

		self.__pyStName = StaticText( item.stName )
		self.__pyStName.text = ""

		self.__pyRtPro = RichText( item.rtProf )
		self.__pyRtPro.maxWidth = self.__pyRtPro.width
		self.__pyRtPro.text = ""

		self.atype = ""
		self.memberID = -1

	def initeInfo( self, memberID, atype ):
		"""
		初始化队友英雄信息
		"""
		self.memberID = memberID
		self.updateInfo( atype, memberID )

	def updateInfo( self, atype, memberID ):
		"""
		更换英雄信息
		"""
		player = BigWorld.player()
		self.atype = atype
		member = player.teamMember.get( memberID )
		if member is None:return
		if atype != "":
			self.__pyHead.texture = "guis/general/challengecopy/head_online.dds"
			gender = member.gender
			name = member.name
			headInfo = MEMBER_HEADS[gender][atype]
			util.setGuiState( self.__pyHead.getGui(), ( 3, 3 ), headInfo[0] )
			self.__pyRtPro.text = headInfo[1]
			self.__pyStName.color = 255, 255, 255, 255
			self.__pyStName.text = name
		else:
			self.randomInfo()

	def randomInfo( self ):
		"""
		随机生成队友头像
		"""
		gender = BigWorld.player().getGender()
		avatars = MEMBER_HEADS[gender]
		atypes = avatars.keys()
		self.__pyHead.texture = "guis/general/challengecopy/head_offline.dds"
		atype = random.choice( atypes )
		headInfo = avatars[atype]
		self.__pyStName.color = 127, 127, 127, 255
		util.setGuiState( self.__pyHead.getGui(), ( 3, 3 ), headInfo[0] )
		self.__pyStName.text = labelGather.getText( "challengecopy:main", "unknow" )
		self.__pyRtPro.text = ""

	def clearInfo( self ):
		"""
		清除队友信息
		"""
		self.atype = ""
		self.memberID = -1
		self.__pyRtPro.text = ""
