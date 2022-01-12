#-*- coding: gb18030 -*-
#
# $Id: SkillsPanel.py,v 1.13 2008-08-28 01:20:09 songpeifang Exp $

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ODListPanel import ODListPanel
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.common.GUIBaseObject import GUIBaseObject
from guis.common.ScriptObject import ScriptObject
from guis.tooluis.CSRichText import CSRichText
from SkillUpgradeConfigLoader import skUpgradeLoader
from ItemsFactory import SkillItem
from guis.controls.ListPanel import ListPanel
from SkillItem import SkTreeItem, SkillArrow
from guis.controls.ListItem import ListItem
import skills as Skill
import csdefine


SKILL_TYPE_COMMON	= 0			# 通用技能
SKILL_TYPE_POSTURE1 = 1
SKILL_TYPE_POSTURE2 = 2

POSTURE_2_SKILLTYPE = {
	csdefine.ENTITY_POSTURE_NONE 		: ( SKILL_TYPE_COMMON, "skillGeneral" ),		# 通用
	csdefine.ENTITY_POSTURE_VIOLENT 	: ( SKILL_TYPE_POSTURE1, "skillViolent" ),		# 狂暴
	csdefine.ENTITY_POSTURE_DEFENCE 	: ( SKILL_TYPE_POSTURE2, "skillDefence" ),		# 防御
	csdefine.ENTITY_POSTURE_DEVIL_SWORD	: ( SKILL_TYPE_POSTURE1, "skillDevilSword" ),	# 魔剑
	csdefine.ENTITY_POSTURE_SAGE_SWORD 	: ( SKILL_TYPE_POSTURE2, "skillSageSword" ),	# 圣剑
	csdefine.ENTITY_POSTURE_SHOT 		: ( SKILL_TYPE_POSTURE1, "skillShot" ),			# 神射
	csdefine.ENTITY_POSTURE_PALADIN 	: ( SKILL_TYPE_POSTURE2, "skillPaladin" ),		# 游侠
	csdefine.ENTITY_POSTURE_MAGIC 		: ( SKILL_TYPE_POSTURE1, "skillMagic" ),		# 法术
	csdefine.ENTITY_POSTURE_CURE 		: ( SKILL_TYPE_POSTURE2, "skillCure" ),			# 医术
	}

CLASS_2_POSTURE = {
	csdefine.CLASS_FIGHTER 	: ( csdefine.ENTITY_POSTURE_VIOLENT, csdefine.ENTITY_POSTURE_DEFENCE, ( 1, 1 ) ),
	csdefine.CLASS_SWORDMAN	: ( csdefine.ENTITY_POSTURE_DEVIL_SWORD, csdefine.ENTITY_POSTURE_SAGE_SWORD, ( 1, 2 ) ),
	csdefine.CLASS_ARCHER 	: ( csdefine.ENTITY_POSTURE_SHOT, csdefine.ENTITY_POSTURE_PALADIN, ( 2, 1 ) ),
	csdefine.CLASS_MAGE 	: ( csdefine.ENTITY_POSTURE_MAGIC, csdefine.ENTITY_POSTURE_CURE, ( 2, 2 ) ),
	}

# ---------------------------------------------------------------------------------------------
class BaseSkPanel( ScriptObject ):
	"""
	技能树基本面板
	"""
	def __init__( self, panel ):
		ScriptObject.__init__( self, panel )
		self.__spellingItems = []	# 正在施放的技能
		self.__invalidItems = []	# 选中的不可用技能
		self.__cdCoverCBID	= 0
		self.__triggers = {}
		self.__registerTriggers()
		self.__initSkills( panel )
	
	def __initSkills( self, panel ):
		self.listPanel = panel.listPanel
		self.pyListPanel_ = ListPanel( panel.listPanel, panel.listBar )
		self.pyListPanel_.viewCols = 4
		self.pyListPanel_.autoSelect = False
		self.pyListPanel_.colSpace = 7.0
		self.pyListPanel_.onItemSelectChanged.bind( self.__onItemSlected )


	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_SPELLING_COVER"]	= self.__onShowSpellingCover		# 高亮显示正在施放的技能
		self.__triggers["EVT_ON_HIDE_SPELLING_COVER"]	= self.__onHideSpellingCover		# 隐藏技能的高亮显示
		self.__triggers["EVT_ON_SHOW_INVALID_COVER"]	= self.__onShowInvalidCover			# 点击不可用技能时显示红色边框
		self.__triggers["EVT_ON_AUTO_NOR_SKILL_CHANGE"] = self.__onAutoSkChange				# 自动战斗技能
		self.__triggers["EVT_ON_STOP_AUTO_SKILL"]		= self.__onAutoSkStop
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# --------------------------------------------------------
	def __onShowSpellingCover( self, skillID ) :
		"""
		用高亮图标标识正在施放的技能
		@param		skillID	:	技能ID
		@type		skillID	:	SKILLID( INT64 )
		"""
		self.__onHideSpellingCover()
		for pySkItem in self.pyListPanel_.pyItems:
			teachInfo = pySkItem.teachInfo
			if teachInfo is None:continue
			if teachInfo.skillID == 0:continue
			skillInfo = pySkItem.itemInfo
			if skillInfo is not None and skillInfo.baseItem.getID() == skillID :
				self.__spellingItems.append( pySkItem )
				toolbox.itemCover.showSpellingItemCover( pySkItem.pyItem )

	def __onHideSpellingCover( self ) :
		"""
		隐藏图标的高亮显示状态
		"""
		for pySkItem in self.__spellingItems :
			toolbox.itemCover.hideItemCover( pySkItem.pyItem )
		self.__spellingItems = []

	def __onShowInvalidCover( self, skillID ) :
		"""
		点击不可用技能时用红色边框显示
		"""
		BigWorld.cancelCallback( self.__cdCoverCBID )
		self.__hideInvalidItemCovers()
		for pySkItem in self.pyListPanel_.pyItems:
			teachInfo = pySkItem.teachInfo
			if teachInfo is None:continue
			if teachInfo.skillID == 0:continue
			skillInfo = pySkItem.itemInfo
			if skillInfo is not None and skillInfo.baseItem.getID() == skillID :
				self.__invalidItems.append( pySkItem )
				toolbox.itemCover.showInvalidItemCover( pySkItem.pyItem )
		self.__cdCoverCBID = BigWorld.callback( 1, self.__hideInvalidItemCovers )		# 标记在1秒后自动隐藏

	def __onAutoSkChange( self, defaultSkID ):
		"""
		自动战斗技能
		"""
		for pySkItem in self.pyListPanel_.pyItems:
			teachInfo = pySkItem.teachInfo
			if teachInfo is None:continue
			if teachInfo.skillID == 0:continue
			skillInfo = pySkItem.itemInfo
			if skillInfo.baseItem.getID() == defaultSkID :
				pySkItem.showAutoParticle()
			else:
				pySkItem.hideAutoParticle()

	def __onAutoSkStop( self, defaultSkID ):
		for pySkItem in self.pyListPanel_.pyItems:
			teachInfo = pySkItem.teachInfo
			if teachInfo is None:continue
			if teachInfo.skillID == 0:continue
			skillInfo = pySkItem.itemInfo
			if skillInfo.baseItem.getID() == defaultSkID :
				pySkItem.hideAutoParticle()
				break

	def __hideInvalidItemCovers( self ) :
		"""
		隐藏不可用技能的红色边框
		"""
		for pySkillItem in self.__invalidItems :
			toolbox.itemCover.hideItemCover( pySkillItem.pyItem )
		self.__invalidItems = []
	
	def __onItemSlected( self, index ):
		pass

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def refreshSkills( self ) :
		"""
		刷新技能信息
		"""
		for pySkItem in self.pyListPanel_.pyItems:
			skInfo = pySkItem.teachInfo
			if skInfo is None:continue
			if skInfo.skillID == 0:continue
			skillInfo = pySkItem.itemInfo
			if skillInfo is None : continue
			pyViewItem.pySkillItem.description = pyViewItem.pageItem.description

	def addSkill( self, skillInfo ):
		skillID = skillInfo.id
		for pySkItem in self.pyListPanel_.pyItems:
			teachInfo = pySkItem.teachInfo
			if teachInfo is None:continue
			teachSkid = teachInfo.skillID
			if teachSkid == 0:continue
			teachSkill = Skill.getSkill( teachSkid )
			if hasattr( teachSkill, "getTeachSkillMap" ):
				teachSkillMap = teachSkill.getTeachSkillMap()
				if skillID in teachSkillMap:
					pySkItem.update( skillInfo )
			else:
				if teachSkid/1000 == skillID/1000:
					pySkItem.update( skillInfo )

	def updateSkill( self, oldSkillID, newSkillInfo ): # 更新当前页技能信息
		for pySkItem in self.pyListPanel_.pyItems:
			teachInfo = pySkItem.teachInfo
			if teachInfo is None:continue
			teachSkid = teachInfo.skillID
			if teachSkid == 0:continue
			skillInfo = pySkItem.skillInfo
			if skillInfo is None:continue
			if skillInfo.id == oldSkillID:
				pySkItem.update( newSkillInfo )
				break

	def removeSkill( self, skillID, skillType ):
		for pySkItem in self.pyListPanel_.pyItems:
			teachInfo = pySkItem.teachInfo
			if teachInfo is None:continue
			teachSkid = teachInfo.skillID
			if teachSkid == 0:continue
			skillInfo = pySkItem.skillInfo
			if skillInfo.id == skillID:
				pySkItem.updateInfo( teachInfo, skillType )
	
	def onCheckSucc( self, skillInfo ):
		for pySkItem in self.pyListPanel_.pyItems:
			teachInfo = pySkItem.teachInfo
			if teachInfo is None:continue
			teachSkid = teachInfo.skillID
			if teachSkid == 0:continue
			if pySkItem.skillInfo.id == skillInfo.id:
				pySkItem.onCheckSucc()

	def clearItems( self ):
		self.pyListPanel_.clearItems()
		self.__onHideSpellingCover()
	
	def flashSkillsInfo( self ):
		for pySkItem in self.pyListPanel_.pyItems:
			teachInfo = pySkItem.teachInfo
			if teachInfo is None:continue
			teachSkid = teachInfo.skillID
			if teachSkid == 0:continue
			pySkItem.onCheckSucc()

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onEnterWorld( self, type ):
		"""
		进入游戏，初始化技能树面板
		"""
		player = BigWorld.player()
		pclass = player.getClass()
		skInfos = skUpgradeLoader.getSkInfos( pclass, type )
		maxSortIndex = 0
		if len( skInfos ):
			maxSortIndex = skInfos[-1].sortIndex
		pyItems = []
		for index in range( maxSortIndex + 1 ):
			pyItem = None
			for skInfo in skInfos:
				if skInfo.sortIndex == index:
					skID = skInfo.skillID
					if skID == 0:
						item = GUI.load( "guis/general/skilltree/linearrow.gui" )
						uiFixer.firstLoadFix( item )
						pyItem = SkillArrow( item )
					else:
						isSpec = skInfo.isSpecial
						item = GUI.load( "guis/general/skilltree/skitem.gui" )
						if isSpec:
							item = GUI.load( "guis/general/skilltree/speskitem.gui" )
						uiFixer.firstLoadFix( item )
						pyItem = SkTreeItem( item, self )
					pyItem.updateInfo( skInfo, type )
					pyItem.sortIndex = skInfo.sortIndex
			if pyItem == None:
				item = GUI.load( "guis/general/skilltree/empty.gui" )
				pyItem = ListItem( item )
				pyItem.size = 58.0, 84.0
				pyItem.teachInfo = None
				pyItem.sortIndex = index
			pyItems.append( pyItem )
		pyItems.sort( key = lambda pyItem: pyItem.sortIndex )
		self.pyListPanel_.addItems( pyItems )

# -------------------------------------------------------------------------------------

class ComSkPanel( BaseSkPanel ):
	"""
	通用技能分页
	"""
	def __init__( self, panel ):
		BaseSkPanel.__init__( self, panel )
		self.pyListPanel_.sbarState = 2
		self.__pyStTitle = StaticText( panel.title.lbTitle )
		self.__pyStTitle.text = labelGather.getText("SkillList:main", "comskill" )

	def onEnterWorld( self ):
		BaseSkPanel.onEnterWorld( self, 0 )
		self.listPanel.textureName = "guis/general/skilltree/commbg.dds"
		mapping = CLASS_2_POSTURE[ BigWorld.player().getClass() ][2]
		util.setGuiState( self.listPanel, ( 2, 2 ), mapping )
	
	def addSkill( self, skillInfo ):
		"""
		添加普通技能
		"""
		BaseSkPanel.addSkill( self, skillInfo )
	
	def updateSkill( self, oldSkillID, skillInfo ):
		"""
		更新普通技能
		"""
		BaseSkPanel.updateSkill( self, oldSkillID, skillInfo )
	
	def removeSkill( self, skillID, skillType ):
		"""
		删除技能
		"""
		BaseSkPanel.removeSkill( self, skillID, skillType )
	
	def onCheckSucc( self, skillInfo ):
		"""
		检测技能
		"""
		BaseSkPanel.onCheckSucc( self, skillInfo )
	
	def clearItems( self ):
		"""
		清空技能格
		"""
		BaseSkPanel.clearItems( self )
	
	def flashSkillsInfo( self ):
		"""
		刷新技能信息
		"""
		BaseSkPanel.flashSkillsInfo( self )
		
# -------------------------------------------------------------------------
class HeartSkPanel( BaseSkPanel, TabPanel ):
	"""
	心法技能面板
	"""
	def __init__( self, panel ):
		BaseSkPanel.__init__( self, panel )
		TabPanel.__init__( self, panel )
	
	def setBgTexture( self, texture, mapping ):
		self.listPanel.textureName = texture
		util.setGuiState( self.listPanel, ( 2, 2 ), mapping )
	
	def onEnterWorld( self, type ):
		BaseSkPanel.onEnterWorld( self, type )
		
# -------------------------------------------------------------------------------------------------
class PstSkPanel( PyGUI ):
	"""
	姿态技能面板
	"""
	def __init__( self, panel ):
		PyGUI.__init__( self, panel )
		self.__pyTabCtr = TabCtrl( panel.tabCtrl )
		panelCls = 2*[HeartSkPanel]
		self.__pyTabCtr.autoSearchPages( panelCls )
		for index, pyPage in enumerate( self.__pyTabCtr.pyPages ) :
			pyPanel = pyPage.pyPanel
			pyPanel.type = index + 1
			pyPanel.subclass( pyPage.pyPanel.gui, self )
			pyBtn = pyPage.pyBtn
			pyBtn.setStatesMapping( UIState.MODE_R4C1 )
			labelGather.setPyBgLabel( pyBtn, "SkillList:main", "tbBtn_%i" % index )
	
	def __setPostureLabels( self ) :
		"""
		根据角色的职业设置界面表现
		"""
		postures = CLASS_2_POSTURE[ BigWorld.player().getClass() ]
		for idx, pyBtn in enumerate( self.__pyTabCtr.pyBtns ) :
			posture = POSTURE_2_SKILLTYPE[ postures[idx] ][0]
			label = POSTURE_2_SKILLTYPE[ postures[idx] ][1]
			pText = labelGather.getText( "SkillList:main", "heart" )%labelGather.getText( "SkillList:main", label )
			pyBtn.text = pText
			pyPanel = self.__pyTabCtr.pyPages[idx].pyPanel
			texture = ""
			if posture == SKILL_TYPE_POSTURE1:
				texture = "guis/general/skilltree/violtbg.dds"
			else:
				texture = "guis/general/skilltree/defebg.dds"
			mapping = postures[2]
			pyPanel.setBgTexture( texture, mapping )
	
	def onEnterWorld( self ):
		"""
		设置初始信息
		"""
		self.__setPostureLabels()
		for pyPage in self.__pyTabCtr.pyPages:
			pyPanel = pyPage.pyPanel
			pyPanel.onEnterWorld( pyPanel.type )
	
	def addSkill( self, skillInfo ):
		"""
		添加心法技能
		"""
		posture = skillInfo.baseItem.getPosture()
		if posture in POSTURE_2_SKILLTYPE:
			index = POSTURE_2_SKILLTYPE[posture][0]
			pyPanel = self.__pyTabCtr.pyPages[index - 1].pyPanel
			pyPanel.addSkill( skillInfo )
	
	def updateSkill( self, oldSkillID, skillInfo ):
		"""
		更新心法技能
		"""
		posture = skillInfo.baseItem.getPosture()
		if posture in POSTURE_2_SKILLTYPE:
			index = POSTURE_2_SKILLTYPE[posture][0]
			pyPanel = self.__pyTabCtr.pyPages[index - 1].pyPanel
			pyPanel.updateSkill( oldSkillID, skillInfo )
	
	def removeSkill( self, skillID, skillType ):
		"""
		删除心法
		"""
		skill = Skill.getSkill( skillID )
		posture = skill.getPosture()
		if posture in POSTURE_2_SKILLTYPE:
			index = POSTURE_2_SKILLTYPE[posture][0]
			pyPanel = self.__pyTabCtr.pyPages[index - 1].pyPanel
			pyPanel.removeSkill( skillID, skillType )
	
	def onCheckSucc( self, skillInfo ):
		posture = skillInfo.baseItem.getPosture()
		if posture in POSTURE_2_SKILLTYPE:
			index = POSTURE_2_SKILLTYPE[posture][0]
			pyPanel = self.__pyTabCtr.pyPages[index - 1].pyPanel
			pyPanel.onCheckSucc( skillInfo )
	
	def clearItems( self ):
		for pyPage in self.__pyTabCtr.pyPages:
			pyPage.pyPanel.clearItems()
	
	def flashSkillsInfo( self ):
		for pyPage in self.__pyTabCtr.pyPages:
			pyPage.pyPanel.flashSkillsInfo()

# ----------------------------------------------------------------------------------
class SkTreePanel( TabPanel ):
	"""
	角色技能树
	"""
	def __init__( self, panel ):
		TabPanel.__init__( self, panel )
		self.__triggers = {}
		self.__registerTriggers()
		self.__initSkills( panel )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initSkills( self, panel ):
		self.__pyComSkPanel = ComSkPanel( panel.panel_0 )
		self.__pyPstSkPanel = PstSkPanel( panel.panel_1 )
		
		self.__pyStRolePot = StaticText( panel.stPotent )
		self.__pyStRolePot.text = ""
		
		self.__pyBtnReSet = HButtonEx( panel.btnReset )
		self.__pyBtnReSet.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnReSet.onLClick.bind( self.__onReSet )
		labelGather.setPyBgLabel( self.__pyBtnReSet, "SkillList:main","reset" )
		
		self.__pyBtnOk = HButtonEx( panel.btnOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onOk )
		labelGather.setPyBgLabel( self.__pyBtnOk, "SkillList:main","ok" )
		
		self.__pyBtnTest = HButtonEx( panel.btnTest )
		self.__pyBtnTest.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnTest.onLClick.bind( self.__onShowTest )
		labelGather.setPyBgLabel( self.__pyBtnTest, "SkillList:main","test" )

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_CHECK_SKILL_SUCC"] = self.__onCheckSucc
		self.__triggers["EVT_ON_ROLE_CANCEL_UPGRADE_SKILLS"] = self.__onCancelUpgrade
		self.__triggers["EVT_ON_ROLE_POTENTIAL_CHANGED"] = self.__onRolePotenChanged # 潜能
		self.__triggers["EVT_ON_ROLE_LEVEL_CHANGED"] = self.__onRoleLevelChanged # level

		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# --------------------------------------------------------
	def __onCheckSucc( self, skillID ):
		"""
		检测升级/降级成功回调
		"""
		skill = Skill.getSkill( skillID )
		skillInfo = SkillItem( skill )
		skillType = self.__getSkillType( skillInfo )
		if skillType == SKILL_TYPE_COMMON:
			self.__pyComSkPanel.onCheckSucc( skillInfo )
		else:
			self.__pyPstSkPanel.onCheckSucc( skillInfo )
		player = BigWorld.player()
		reqPotent = player.getTotalPotential()
		remPotent = player.potential - reqPotent
		if remPotent <= 0:
			remPotent = 0
		self.__pyStRolePot.text = labelGather.getText( "SkillList:main", "rolePotent" )%str( remPotent )
	
	def __onUpgradeSucc( self, skillID ):
		"""
		技能升级成功回调
		"""
		pass
	
	def __onCancelUpgrade( self ):
		"""
		技能取消升级回调
		"""
		pass
	
	def __onRolePotenChanged( self, oldValue, newValue ):
		"""
		角色潜能点改变
		"""
		self.__pyStRolePot.text = labelGather.getText( "SkillList:main", "rolePotent" )%str( newValue )
		self.__pyComSkPanel.flashSkillsInfo()
		self.__pyPstSkPanel.flashSkillsInfo()
		
	def __onRoleLevelChanged( self, oldLevel, newLevel ):
		"""
		角色等级改变
		"""
		self.__pyComSkPanel.flashSkillsInfo()
		self.__pyPstSkPanel.flashSkillsInfo()
		
	def __onReSet( self, pyBtn ):
		if pyBtn is None:return
		BigWorld.player().cancelUpgradeSkill()
	
	def __onOk( self, pyBtn ):
		if pyBtn is None:return
		BigWorld.player().upgradeSkills()
	
	def __onShowTest( self, pyBtn ):
		skillList = rds.ruisMgr.skillList
		skillList.visible = not skillList.visible

	def __onPostureChanged( self, newPosture, oldPosture ) :
		"""
		玩家姿态改变
		"""
		self.__pyPanels[SKILL_TYPE_POSTURE1].refreshSkills()
		self.__pyPanels[SKILL_TYPE_POSTURE2].refreshSkills()

	def __setPostureLabels( self ) :
		"""
		根据角色的职业设置界面表现
		"""
		postures = CLASS_2_POSTURE[ BigWorld.player().getClass() ]
		pyTBtns = [ self.__pyTCSkills.pyBtns[0], self.__pyTCSkills.pyBtns[1] ]
		for idx, pyBtn in enumerate( pyTBtns ) :
			pText = POSTURE_2_SKILLTYPE[ postures[idx] ][1]
			labelGather.setPyBgLabel( pyBtn, "SkillList:main", pText )
	
	def __getSkillType( self, skInfo ):
		"""
		获取技能类型
		"""
		skill = skInfo.baseItem
		if skInfo.id == 1:
			return SKILL_TYPE_COMMON
		else :
			posture = skill.getPosture()
			if posture in POSTURE_2_SKILLTYPE:
				return POSTURE_2_SKILLTYPE[posture][0]

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def clearItems( self ):
		"""
		清除技能
		"""
		self.__pyComSkPanel.clearItems()
		self.__pyPstSkPanel.clearItems()
		
	def addSkill( self, skillInfo ):
		"""
		添加技能
		"""
		skillType = self.__getSkillType( skillInfo )
		if skillType == SKILL_TYPE_COMMON:
			self.__pyComSkPanel.addSkill( skillInfo )
		else:
			self.__pyPstSkPanel.addSkill( skillInfo )
	
	def updateSkill( self, oldSkillID, skillInfo ):
		"""
		更新技能
		"""
		skillType = self.__getSkillType( skillInfo )
		if skillType == SKILL_TYPE_COMMON:
			self.__pyComSkPanel.updateSkill( oldSkillID, skillInfo )
		else:
			self.__pyPstSkPanel.updateSkill( oldSkillID, skillInfo )
	
	def removeSkill( self, skillID ):
		"""
		删除技能
		"""
		skill = Skill.getSkill( skillID )
		skillInfo = SkillItem( skill )
		skillType = self.__getSkillType( skillInfo )
		if skillType == SKILL_TYPE_COMMON:
			self.__pyComSkPanel.removeSkill( skillID, skillType )
		else:
			self.__pyPstSkPanel.removeSkill( skillID, skillType )
		
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onEnterWorld( self ) :
		self.__pyComSkPanel.onEnterWorld()
		self.__pyPstSkPanel.onEnterWorld()
	
	def show( self ):
		pass

