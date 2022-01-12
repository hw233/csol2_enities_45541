# -*- coding: gb18030 -*-
#
# $Id: SkillList.py,v 1.23 2008-08-26 02:19:28 huangyongwei Exp $

"""
implement skilllist window class
"""

import csdefine
from guis import *
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPage
from SkTreePanel import SkTreePanel
from SkillsPanel import SkillsPanel, LiveSkillsPanel, TongSkillsPanel,ChallengePanel
from Helper import courseHelper
from ItemsFactory import SkillItem
from LabelGather import labelGather
from guis.tooluis.CSRichText import CSRichText
from LivingConfigMgr import LivingConfigMgr
lvcMgr = LivingConfigMgr.instance()
from TongSkillResearchData import TongSkillResearchData
tongSkillResearch = TongSkillResearchData.instance()
from SkillUpgradeConfigLoader import chSkillLoader
import skills
import csdefine
import csstring

SKILL_TYPE_COMMON	= 0			# 通用技能
SKILL_TYPE_TONG		= 1			# 帮会技能
SKILL_TYPE_LIVE		= 2			# 生活技能
SKILL_TYPE_ACTION	= 3			# 行为技能
SKILL_TYPE_CHALLENGE = 4		# 挑战副本技能

SKILL_TYPE_POSTURE1 = 1
SKILL_TYPE_POSTURE2 = 2

POSTURE_2_SKILLTYPE = {
	csdefine.ENTITY_POSTURE_NONE 		: ( SKILL_TYPE_COMMON, "skillGeneral" ),		# 通用
	csdefine.ENTITY_POSTURE_DEFENCE 	: ( SKILL_TYPE_POSTURE1, "skillDefence" ),		# 防御
	csdefine.ENTITY_POSTURE_VIOLENT 	: ( SKILL_TYPE_POSTURE2, "skillViolent" ),		# 狂暴
	csdefine.ENTITY_POSTURE_DEVIL_SWORD	: ( SKILL_TYPE_POSTURE1, "skillDevilSword" ),	# 魔剑
	csdefine.ENTITY_POSTURE_SAGE_SWORD 	: ( SKILL_TYPE_POSTURE2, "skillSageSword" ),	# 圣剑
	csdefine.ENTITY_POSTURE_SHOT 		: ( SKILL_TYPE_POSTURE1, "skillShot" ),			# 神射
	csdefine.ENTITY_POSTURE_PALADIN 	: ( SKILL_TYPE_POSTURE2, "skillPaladin" ),		# 游侠
	csdefine.ENTITY_POSTURE_MAGIC 		: ( SKILL_TYPE_POSTURE1, "skillMagic" ),		# 法术
	csdefine.ENTITY_POSTURE_CURE 		: ( SKILL_TYPE_POSTURE2, "skillCure" ),			# 医术
	}

CLASS_2_POSTURE = {
	csdefine.CLASS_FIGHTER 	: ( csdefine.ENTITY_POSTURE_DEFENCE, csdefine.ENTITY_POSTURE_VIOLENT ),
	csdefine.CLASS_SWORDMAN	: ( csdefine.ENTITY_POSTURE_DEVIL_SWORD, csdefine.ENTITY_POSTURE_SAGE_SWORD ),
	csdefine.CLASS_ARCHER 	: ( csdefine.ENTITY_POSTURE_SHOT, csdefine.ENTITY_POSTURE_PALADIN ),
	csdefine.CLASS_MAGE 	: ( csdefine.ENTITY_POSTURE_MAGIC, csdefine.ENTITY_POSTURE_CURE ),
	}

def _getSkillType( skillInfo ) :
	"""
	获取技能类型
	"""
	if lvcMgr.isLivingSkill( skillInfo.id ) :
		return SKILL_TYPE_LIVE
	elif skillInfo.id == 1 :
		return SKILL_TYPE_COMMON
	elif skillInfo.isNormalSkill :
		return SKILL_TYPE_ACTION
	elif _isTongSkType( skillInfo.id ):
		return SKILL_TYPE_TONG
	elif _isChaSkType( skillInfo.id ):
		return SKILL_TYPE_CHALLENGE
	else :
		posture = skillInfo.baseItem.getPosture()
		if posture in POSTURE_2_SKILLTYPE:
			return SKILL_TYPE_COMMON

def _isTongSkType( skillID ):
	skillType = skillID/1000
	tongSkTypes = []
	tongTeachDatas = tongSkillResearch.getDatasByType( csdefine.TONG_SKILL_ROLE )
	for tongTeachId in tongTeachDatas.keys():
		spellTeach = skills.getSkill( tongTeachId )._spellTeach
		tongSkTypes.append( spellTeach/1000 )
	return skillType in tongSkTypes

def _isChaSkType( skillID ):
	player = BigWorld.player()
	pclass = player.getClass()
	skillType = skillID/1000
	chaSkDatas = chSkillLoader.getChSkInfos( pclass )
	chaSkTypes = []
	for chaSkId in [ chaSkData.skillID for chaSkData in chaSkDatas]:
		spellTeach = skills.getSkill( chaSkId )._spellTeach
		chaSkTypes.append( spellTeach/1000 )
	return skillType in chaSkTypes

class SkillTree( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/skilltree/wnd.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.__initialize( wnd )

		self.__skillLists = { SKILL_TYPE_COMMON:[],
							SKILL_TYPE_TONG:[],
							SKILL_TYPE_LIVE:[],
							SKILL_TYPE_ACTION:[],
							SKILL_TYPE_CHALLENGE:[],
				}
				
		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, wnd ):
		panelMaps = {0:SkTreePanel, 1:TongSkillsPanel, 2:LiveSkillsPanel, 3:SkillsPanel, 4:ChallengePanel }
		tc = wnd.tc
		self.__pyTCSkills = TabCtrl( tc )
		self.__pyPanels = {}
		index = 0
		while True :											#初始化TabCtrl
			tabName = "btn_%d"%index
			tab = getattr( tc, tabName, None )
			if tab is None : break
			panelName = "panel_%d"%index
			tabPanel = getattr( tc, panelName, None )
			if tabPanel is None : break
			pyBtn = TypeBtn( tab )
			pyBtn.setStatesMapping( UIState.MODE_R1C3 )
			pyBtn.text = labelGather.getText( "SkillList:main", "btn_%d"%index )
			pyPanel = panelMaps[index]( tabPanel )
			pyPanel.skType = index
			self.__pyPanels[index] = pyPanel
			pyPage = TabPage( pyBtn, pyPanel )
			self.__pyTCSkills.addPage( pyPage )
			index += 1
		self.__pyTCSkills.onTabPageSelectedChanged.bind( self.__onPageChange )
		labelGather.setPyLabel( self.pyLbTitle_,"SkillList:main", "rbTitle" )
		

	# ----------------------------------------------------------------------
	# pravite
	# ----------------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TOGGLE_SKILL_WINDOW"] = self.__toggleVisible
		self.__triggers["EVT_ON_PLAYERROLE_ADD_SKILL"] = self.__onAddSkill
		self.__triggers["EVT_ON_PLAYERROLE_REMOVE_SKILL"] = self.__onRemoveSkill
		self.__triggers["EVT_ON_PLAYERROLE_UPDATE_SKILL"] = self.__onUpateSkill
		self.__triggers["EVT_ON_PLAYERROLE_UPDATE_NORMAL_SKILL"] = self.__onNormalSkillUpdate
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------------
	def __toggleVisible( self, tabIndex = None ) :
		if tabIndex is None :
			self.visible = not self.visible
		else :
			pyPages = self.__pyTCSkills.pyPages
			if pyPages.index( self.__pyTCSkills.pySelPage ) == tabIndex :
				self.visible = not self.visible
			else :
				self.__pyTCSkills.pySelPage = pyPages[tabIndex]
				if not self.visible :
					self.show()

	# -------------------------------------------------
	def __onAddSkill( self, skillInfo ) :
		"""
		添加技能
		"""
		skillType = _getSkillType( skillInfo )
		self.__pyPanels[skillType].addSkill( skillInfo )
		self.__skillLists[skillType].append( skillInfo.id )

	def __onRemoveSkill( self, skillInfo ) :
		"""
		删除技能
		"""
		skillType = _getSkillType( skillInfo )
		skillIDs = self.__skillLists[skillType]
		skillID = skillInfo.id
		if skillID in skillIDs :
			self.__pyPanels[skillType].removeSkill( skillID )
			skillIDs.remove( skillID )

	def __onUpateSkill( self, oldSkillID, skillInfo ) :
		"""
		更新技能
		"""
		skillType = _getSkillType( skillInfo )
		skillIDs = self.__skillLists[skillType]
		if oldSkillID in skillIDs :
			self.__pyPanels[skillType].updateSkill( oldSkillID, skillInfo )
			skillIDs.remove( oldSkillID )
			skillIDs.append( skillInfo.id )

	def __onNormalSkillUpdate( self, skillID, baseItem ) :
		"""
		更新普通物理攻击技能
		"""
		skillType = SKILL_TYPE_COMMON
		skillIDs = self.__skillLists[skillType]
		skillInfo = SkillItem( baseItem )
		if skillID in skillIDs:
			self.__pyPanels[skillType].updateSkill( skillID, skillInfo )

	def __onPostureChanged( self, newPosture, oldPosture ) :
		"""
		玩家姿态改变
		"""
		self.__pyPanels[SKILL_TYPE_POSTURE1].refreshSkills()
		self.__pyPanels[SKILL_TYPE_POSTURE2].refreshSkills()
	
	def __onPageChange( self, pyCtrl ):
		titles = { SKILL_TYPE_TONG:labelGather.getText( "SkillList:main", "tongSkill" ),
				SKILL_TYPE_LIVE:labelGather.getText( "SkillList:main", "liveSkill" ),
				SKILL_TYPE_ACTION:labelGather.getText( "SkillList:main", "actSkill" ),
				SKILL_TYPE_CHALLENGE:labelGather.getText( "SkillList:main", "challengeSkill" ),
				}
		pySelPage = pyCtrl.pySelPage
		pyPanel = pySelPage.pyPanel
		if pyPanel.skType == SKILL_TYPE_COMMON:
			return
		title = titles.get( pyPanel.skType, "" )
		pyPanel.setTitle( title )

	# ----------------------------------------------------------------
	# callbacks
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.hide()
		for skType in self.__skillLists :
			self.__skillLists[skType] = []
		for pyPanel in self.__pyPanels.itervalues() :
			pyPanel.clearItems()

	def onEnterWorld( self ) :
		Window.onEnterWorld( self )
		for skillType, pyPanel in self.__pyPanels.items():
			if skillType == SKILL_TYPE_ACTION:continue
			pyPanel.onEnterWorld()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def show( self ) :
		Window.show( self )
		self.__pyTCSkills.pySelPage.pyPanel.show()
		rds.helper.courseHelper.openWindow( "jineng_chuangkou" )

	def hide( self ) :
		BigWorld.player().cancelUpgradeSkill()
		Window.hide( self )

class TypeBtn( TabButton ):
	def __init__( self, btn ):
		TabButton.__init__( self, btn )
		self.__pyRtName = CSRichText( btn.rtName)
		self.__pyRtName.maxWidth = 20.0
		self.__pyRtName.spacing = -1
		self.__pyRtName.foreColor = ( 255,227,184,255 )
		
	def onStateChanged_( self, state ):
		TabButton.onStateChanged_( self, state )
		if state == UIState.SELECTED:
			self.__pyRtName.foreColor = ( 142, 216, 217, 255 )
		else:
			self.__pyRtName.foreColor = ( 255,227,184,255 )

	def _getText( self ):
		return self.__pyRtName.text

	def _setText( self, text ):
		textLen = len( csstring.toWideString( text ) )
		if textLen >= 4:
			self.__pyRtName.spacing = -2.0
		else:
			self.__pyRtName.spacing = 4.0
		self.__pyRtName.text = text

	text = property( _getText, _setText )
