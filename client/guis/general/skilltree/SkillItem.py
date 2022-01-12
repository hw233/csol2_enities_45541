# -*- coding: gb18030 -*-
#
# $Id: SkillList.py,v 1.23 2008-08-26 02:19:28 huangyongwei Exp $

"""
implement skilllist window class
"""
from guis import *
from guis.controls.SkillItem import SkillItem as SkItem
from guis.controls.ListItem import ListItem
from guis.tooluis.CSRichText import CSRichText
from guis.common.PyGUI import PyGUI
from guis.controls.Control import Control
from guis.common.GUIBaseObject import GUIBaseObject
from guis.controls.CircleCDCover import CircleCDCover as Cover
from guis.otheruis.AnimatedGUI import AnimatedGUI
from LabelGather import labelGather
from LivingConfigMgr import LivingConfigMgr
lvcMgr = LivingConfigMgr.instance()
import event.EventCenter as ECenter
from config.client.LivingSkillUpgradeClew import Datas as lvs_UpgradeDatas
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
import skills as Skill
from ItemsFactory import SkillItem as SkillInfo
from SkillUpgradeConfigLoader import chSkillLoader

SKILL_BASE_TYPE = 0
SKILL_EXTEND_TYPE = 1
SKILL_LIVE_TYPE = 2
SKILL_TREE_TYPE = 3
POSTURE_SKILL_LIST = [322458, 322459, 322460, 322461, 322462, 322463, 322464, 322465]


class BaseSkillItem( GUIBaseObject ) :

	def __init__( self, item, pyBinder = None ) :
		GUIBaseObject.__init__( self, item )

		self.pySkItem_ = SkillItem( item.icon, self )
		self.pySkItem_.skillType = SKILL_BASE_TYPE
		self.pySkItem_.crossFocus = False
		self.pySkItem_.onDragStart.bind( self.onDragStart_ )
		self.pySkItem_.onDragStart.bind( self.onDragStop_ )
		self.__autoParticle = "autoParticle"

		self.__pyCover = Cover( item.cdCover.circleCover )
		self.__pyCover.crossFocus = False
		self.__pyOverCover = AnimatedGUI( item.cdCover.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )					# 动画播放一次，共8帧
		self.__pyOverCover.cycle = 0.4										# 循环播放一次的持续时间，单位：秒
		self.__pyCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )

		self.__triggers = {}
		self.__registerTriggers()

	# ----------------------------------------------------------------
	# about event
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_BEGIN_COOLDOWN"] = self.__beginCooldown
		self.__triggers["EVT_ON_KITBAG_ITEM_INFO_CHANGED"] = self.__itemInfoChanged
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

	def __itemInfoChanged( self, kitbagOrder, itemOrder, itemInfo ) :
		"""
		"""
		if not self.itemInfo : return
		icon = Skill.getSkill( self.itemInfo.id ).getIcon()
		if self.pySkItem_.icon[0] != icon:
			self.pySkItem_.icon = icon


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDragStart_( self, pyDragged ):
		pass
	
	def onDragStop_( self, pyDragged ):
		pass
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def update( self, itemInfo ) :
		self.pySkItem_.update( itemInfo )
		if itemInfo is not None :
			self.pySkItem_.crossFocus = True
			cdInfo = itemInfo.getCooldownInfo()
			self.__pyCover.unfreeze( *cdInfo )
		else :
			self.pySkItem_.crossFocus = False
			self.__pyCover.reset( 0 )

	def showAutoParticle( self ):
		"""
		显示自动技能光效
		"""
		particleUI = getattr( self.pySkItem_.gui, self.__autoParticle, None )
		if particleUI :
			particleUI.visible = True
		else :
			textureName = "maps/particle_2d/guangxiao_huang_kuang/guangxiao_huang_kuang.texanim"
			toolbox.itemParticle.addParticle( self.pySkItem_, textureName, self.__autoParticle, 0.99999 )

	def hideAutoParticle( self ):
		"""
		隐藏自动技能光效
		"""
		particleUI = getattr( self.pySkItem_.gui, self.__autoParticle, None )
		if particleUI :
			particleUI.visible = False


	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _getItemInfo( self ) :
		return self.pySkItem_.itemInfo

	def _setItemInfo( self, itemInfo ):
		self.pySkItem_.itemInfo = itemInfo

	def _getItem( self ):
		return self.pySkItem_

	def _getDescription( self ) :
		return self.pySkItem_.description

	def _setDescription( self, dsp ) :
		self.pySkItem_.description = dsp


	itemInfo = property( _getItemInfo, _setItemInfo )
	pyItem = property( _getItem )
	description = property( _getDescription, _setDescription )

# --------------------------------------------------------------------
# 普通技能、被动技能、表情动作的格子
# --------------------------------------------------------------------
class ExtendSkillItem( BaseSkillItem ):

	def __init__( self, pyBinder = None ) :
		item = GUI.load( "guis/controls/skillitem/bg_item.gui" )
		uiFixer.firstLoadFix( item )
		BaseSkillItem.__init__( self, item, pyBinder )

		self.pySkItem_.dragMark = DragMark.SKILL_WND
		self.pySkItem_.skillType = SKILL_EXTEND_TYPE
		self.pySkName_ = StaticText( item.stName )
		self.pySkName_.top = 16.0
		self.pySkLevel_ = StaticText( item.stLevel )
		self.pySkLevel_.text = ""

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ):
		if not ( self.itemInfo is None or self.itemInfo.isPassive ) :
			self.itemInfo.spell()
		return True
	
	def onDragStart_( self, pyDragged ):
		if self.itemInfo is None:return
		rds.ruisMgr.hideBar.enterShow()
	
	def onDragStop_( self, pyDragged ):
		if self.itemInfo is None:return
		rds.ruisMgr.hideBar.leaveShow()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BaseSkillItem.update( self, itemInfo )
		if itemInfo is not None :
			self.pySkName_.text = itemInfo.name
		else :
			self.pySkName_.text = ""

# --------------------------------------------------------------------
# 生活技能格子
# --------------------------------------------------------------------
class LiveSkillItem( BaseSkillItem, Control ) :
	
	COMMON						= ( 1,1 )					# 普通状态
	HIGHLIGHT 					= ( 2,1 )					# 高亮状态
	
	def __init__( self, pyBinder = None ) :
		item = GUI.load( "guis/general/skilllist/liveskillitem.gui" )
		uiFixer.firstLoadFix( item )
		BaseSkillItem.__init__( self, item, pyBinder )
		Control.__init__( self, item, pyBinder )	
		self.focus = False	
		self.__selected = False
		self.__itemBg = PyGUI( item.itemBg )

		self.pySkItem_.dragFocus = False
		self.pySkItem_.focus = False
		self.pySkItem_.skillType = SKILL_LIVE_TYPE
		self.__pySkName = CSRichText( item.rtSkillName )
		self.__pySkName.foreColor = ( 252, 235, 179, 255 )
		self.__pySkLevel = CSRichText( item.rtSkillLevel )
		self.__pySkLevel.align = "R"
		self.__pySkLevel.foreColor = ( 252, 235, 179, 255 )
		self.__pyUpgradeClew = CSRichText( item.rtUpgradeClew )
		self.__pyProgBar = LSProgressBar( item.progBar )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------	
	def update( self, itemInfo ) :
		BaseSkillItem.update( self, itemInfo )
		if itemInfo :
			skillName = PL_Font.getSource( itemInfo.name, fc = ( 252, 235, 179, 255 ) )
			self.__pySkName.text = skillName
			skID = itemInfo.id
			isInRoleSks = skID in BigWorld.player().skillList_
			if isInRoleSks:
				skillInfo = BigWorld.player().livingskill.get( skID, (0, 0) )
				skLV = skillInfo[1]
				dspText = lvcMgr.getDesByLevel( skID, skLV )
				if dspText:
					levelStr = dspText.split( "|" )[-1]
					levelStr = PL_Font.getSource( levelStr, fc = ( 252, 235, 179, 255 ) )
					self.__pySkLevel.text = levelStr
				else :
					ERROR_MSG( "Error living skill config! Skill %s in level %s not found!" % ( skID, skLV ) )
					self.__pySkLevel.text = "None"
				self.__pyUpgradeClew.text = lvs_UpgradeDatas[ skLV ]
				sleightMax = lvcMgr.getMaxSleightByLevel( skID, skLV )
				self.__pyProgBar.currValue = skillInfo[0]
				self.__pyProgBar.upperLimit = sleightMax
				skillDesc = "skill_%s" % skLV
				self.__pySkLevel.text = labelGather.getText( "SkillList:main", skillDesc )
			else:
				self.__pySkName.text = ""
				self.__pySkLevel.text = self.__pySkLevel.text = labelGather.getText( "SkillList:main", "noLearned" )
				self.__pyUpgradeClew.text = ""
				self.__pyProgBar.visible = False
			self.__pyProgBar.visible = isInRoleSks
			
		else :
			self.__pySkName.text = ""
			self.__pySkLevel.text = self.__pySkLevel.text = labelGather.getText( "SkillList:main", "noLearned" )
			self.__pyUpgradeClew.text = ""
			self.__pyProgBar.visible = False
	
	
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------			
	def __setBgState( self, state ):
		util.setGuiState( self.__itemBg.gui,(4,2), state )
	
	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getSelected( self ):
		return self.__selected
		
	def _setSelected( self, selected ):
		if selected and self.pySkItem_.itemInfo:
			self.__setBgState( ( 2,1 ))
		else:
			self.__setBgState( ( 1, 1 ) )
		self.__selected = selected
	
	def _getItemInfo( self ):
		return self.pySkItem_.itemInfo
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	selected = property( _getSelected, _setSelected )
	itemInfo = property( _getItemInfo )
		
	
# ---------------------------------------------------------------------
# 技能树格子
# ---------------------------------------------------------------------
class SkTreeItem( BaseSkillItem, ListItem ):
	
	def __init__( self, item, pyBinder = None ) :
		BaseSkillItem.__init__( self, item, pyBinder )
		ListItem.__init__( self, item, pyBinder )
		
		self.pySkItem_.dragMark = DragMark.SKILL_WND
		self.pySkItem_.skillType = SKILL_TREE_TYPE
		self.__pySkFrm = PyGUI( item.skFrm )
		self.__pyLvBg = PyGUI(item.lvBg )
		
		self.__pyStCurLv = StaticText( item.stCurLv )
		self.__pyStCurLv.font = "songti.font"
		self.__pyStCurLv.color = ( 255.0, 255.0, 255.0, 255.0 )
		self.__pyStCurLv.text = ""
		
		
		self.__pyStMaxLv = StaticText( item.stMaxLv )
		self.__pyStMaxLv.font = "songti.font"
		self.__pyStMaxLv.color = ( 255.0, 255.0, 255.0, 255.0 )
		self.__pyStMaxLv.text = ""
		
		self.__pyBtArrow = PyGUI( item.btArrow )
		self.__pyBtArrow.visible = False
		
		self.__pyBtLine = PyGUI( item.btLine )
		self.__pyBtLine.visible = False
		self.teachInfo = None
		
		self.size = 58.0,84.0
	
	def __getLeanedSkill( self, skillID ):
		"""
		判断有没有学习该技能
		"""
		teachSk = Skill.getSkill( self.teachInfo.skillID )
		hasSkills = BigWorld.player().skillList_
		if hasattr( teachSk, "_SkillsMap" ):
			if skillID in teachSk._SkillsMap:
				return skillID, True
			for hasSkID in hasSkills:
				if hasSkID in teachSk._SkillsMap:
					return hasSkID, True
			return 0, True
		else:
			return skillID, False
	
	def getCurSkillID( self ):
		skillID = self.teachInfo.skillID
		teachSkill = Skill.getSkill( skillID )
		ledSkID = self.__getRoleMapSkill( teachSkill )
		return ledSkID
	
	def __getRoleMapSkill( self, teachSk ):
		hasSkills = BigWorld.player().skillList_
		if hasattr( teachSk, "_SkillsMap" ):
			for hasSkID in hasSkills:
				if hasSkID in teachSk._SkillsMap:
					return hasSkID
			return teachSk.getID()
		return 0
	
	def __setCurLvColor( self, color ):
		"""
		设置当前等级颜色
		"""
		self.__pyStCurLv.color = color
	
	def __setMaxLvColor( self, color ):
		"""
		设置最大等级颜色
		"""
		self.__pyStMaxLv.color = color
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BaseSkillItem.update( self, itemInfo )
		skillID = itemInfo.id
		skill = itemInfo.baseItem
		learned = True
		leantID, isTeachSk = self.__getLeanedSkill( skillID )
		curLevel = skill.getLevel()
		self.pySkItem_.dragFocus = leantID > 0
		if skillID/1000 in POSTURE_SKILL_LIST:
			self.pySkItem_.dragFocus = False	# 心法技能不能拖动
		maxLevel = 0
		if isTeachSk:	#学习技能
			teachSkID = self.teachInfo.skillID
			teachSk = Skill.getSkill( teachSkID )
			maxLevel = teachSk.getTeachMaxLevel()
			if leantID <= 0:	#未学习
				learned = False
				self.pySkItem_.getGui().materialFX = "COLOUR_EFF"
				util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(2, 2) )
				util.setGuiState( self.__pyLvBg.getGui(),(2, 1),(2, 1) )
				self.__setCurLvColor( (255.0, 255.0, 255.0, 255.0 ) )
				self.__setMaxLvColor ( (255.0, 255.0, 255.0, 255.0 ) )
				curLevel = 0
			else:
				self.pySkItem_.getGui().materialFX = "BLEND"
		else:
			maxLevel = skill.getMaxLevel()
			
		if self.teachInfo.checkUpgrade( skillID ):
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(1, 2) )
			self.__setCurLvColor( (0.0, 255.0, 0.0, 255.0 ) )
			self.__setMaxLvColor( (0.0, 255.0, 0.0, 255.0 ) )
		else:
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(1, 1) )
			self.__setCurLvColor( (255.0, 255.0, 255.0, 255.0 ) )
			self.__setMaxLvColor( (255.0, 255.0, 255.0, 255.0 ) )
		if curLevel >= maxLevel:
			curLevel = maxLevel
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(2, 1) )
			self.__setCurLvColor( ( 231.0, 186.0, 0.0, 255.0 ) )
			self.__setMaxLvColor( ( 231.0, 186.0, 0.0, 255.0 ) )
		
		self.__pyStCurLv.text = "%d"%curLevel
		self.__pyStMaxLv.text = "%d"%maxLevel
		self.pySkItem_.description = self.teachInfo.getDescription( skillID, learned )
				
	def updateInfo( self, teachInfo, type ):
		"""
		初始化更新
		"""
		self.teachInfo = teachInfo
		skillID = teachInfo.skillID
		teachSkill = Skill.getSkill( skillID )
		ledSkID = self.__getLeanedSkill( skillID )[0]
		if ledSkID <= 0: #没有学习
			ledSkID = skillID
		skill = Skill.getSkill( ledSkID )
		if skill is None:
			ERROR_MSG( "can't load skill:%d" %ledSkID )
			return
		skillInfo = SkillInfo( skill )
		self.update( skillInfo )
		preState = teachInfo.getPreState( type )
		if preState < 0:	#无后置技能
			self.__pyBtArrow.visible = False
			self.__pyBtLine.visible = False
		elif preState == 0:
			self.__pyBtArrow.visible = False
			self.__pyBtLine.visible = True
		else:
			self.__pyBtArrow.visible = True
			self.__pyBtLine.visible = False

	def onCheckSucc( self ):
		player = BigWorld.player()
		skillID = self.skillInfo.id
		newSkillID = player.getUpgradeSkillID( skillID )
		skill = Skill.getSkill( newSkillID )
		if skill is None:return
		
		leantID, isTeachSk = self.__getLeanedSkill( skillID )
		maxLevel = 0
		if isTeachSk:	#学习技能
			teachSkID = self.teachInfo.skillID
			teachSk = Skill.getSkill( teachSkID )
			maxLevel = teachSk.getTeachMaxLevel()
		else:
			maxLevel = skill.getMaxLevel()
		
		newLevel = skill.getLevel()
#		maxLevel = skill.getMaxLevel()
		learned = True
		if self.teachInfo.checkUpgrade( newSkillID ):
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(1, 2) )
			self.__setCurLvColor( (0.0, 255.0, 0.0, 255.0 ) )
			self.__setMaxLvColor( (0.0, 255.0, 0.0, 255.0 ) )
		else:
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(1, 1) )
			self.__setCurLvColor( (255.0, 255.0, 255.0, 255.0 ) )
			self.__setMaxLvColor( (255.0, 255.0, 255.0, 255.0 ) )
		if newLevel >= maxLevel:
			newLevel = maxLevel
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(2, 1) )
			self.__setCurLvColor( ( 231.0, 186.0, 0.0, 255.0 ) )
			self.__setMaxLvColor( ( 231.0, 186.0, 0.0, 255.0 ) )
		if newLevel == 0 and maxLevel == 0:	#未学习
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(2, 2) )
			self.__setCurLvColor( (255.0, 255.0, 255.0, 255.0 ) )
			self.__setMaxLvColor ( (255.0, 255.0, 255.0, 255.0 ) )
			learned = False

		self.__pyStCurLv.text = "%d"%newLevel
		self.pySkItem_.description = self.teachInfo.getDescription( newSkillID, learned )
		
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onDragStart_( self, pyDragged ):
		pass
	
	def onDragStop_( self, pyDragged ):
		pass
	
	def _getSkillInfo( self ):
		return self.pySkItem_.itemInfo

	skillInfo = property( _getSkillInfo, )


class SkillArrow( ListItem ):
	def __init__( self, item ):
		ListItem.__init__( self, item )
		self.teachInfo = None
		self.type = 0
		self.size = 58.0, 84.0
		
		self.__pyLineArrow = PyGUI( item.lineArrow )
	
	def updateInfo( self, skInfo, type ):
		self.teachInfo = skInfo
		self.type = 0
		nextSortIndex = skInfo.sortIndex + 4
		nextSkill = skInfo.getNextSkill( type, nextSortIndex )
		if nextSkill is None :return
		if nextSkill.skillID == 0 :
			self.__pyLineArrow.texture = "guis/general/skilltree/linearrows2.dds"
		else:
			self.__pyLineArrow.texture = "guis/general/skilltree/linearrows.dds"
			
	
	def setEnable( self, isEnable ):
		if isEnable:
			util.setGuiState( self.__pyLineArrow.getGui(), ( 1, 2 ), ( 1, 1 ) )
		else:
			util.setGuiState( self.__pyLineArrow.getGui(), ( 1, 2 ), ( 1, 2 ) )

# ---------------------------------------------------------------------------------
import TongDatas
tongSkillDatas = TongDatas.tongSkill_instance()

class TongSkillItem( ExtendSkillItem ):
	
	def __init__( self, pyBinder = None ) :
		ExtendSkillItem.__init__( self, pyBinder )
		self.pySkName_.top = 5.0
		
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ):
		if not self.itemInfo:
			return
		if not ( self.itemInfo is None or self.itemInfo.isPassive ) :
			self.itemInfo.spell()
		return True
	
	def update( self, itemInfo ):
		ExtendSkillItem.update( self, itemInfo )
		if itemInfo is None:return
		skId = itemInfo.id
		isLearned = self.__isLearned( skId )
		self.pySkItem_.focus = isLearned
		self.pySkItem_.dragFocus = isLearned
		materialFX = "BLEND"
		if not self.__isLearned( skId ):
			materialFX = "COLOUR_EFF"
			self.pySkLevel_.text = labelGather.getText( "SkillList:main", "noLearned" )
		else:
			self.pySkLevel_.text = labelGather.getText( "SkillList:main", "skillLevel", itemInfo.level )
		
		
		self.pySkItem_.description = self.__getTeachSkDes( skId )
		self.pySkItem_.getGui().materialFX = materialFX

		
	def __isLearned( self, skID ):
		return skID in BigWorld.player().skillList_	
	
	def __getTeachSkDes( self, teachSkId ):
		teachSk = Skill.getSkill( teachSkId )
		des = SkillInfo( teachSk ).description
		return des

# -----------------------------------------------------------------------
# 
# -----------------------------------------------------------------------
class ChallengeSkItem( BaseSkillItem ):
	
	def __init__( self, item, itemIndex = 0, pyBinder = None ) :
		BaseSkillItem.__init__( self, item, pyBinder )
		self.pyBinder = pyBinder
		self.itemIndex = itemIndex
		self.pySkItem_.dragMark = DragMark.SKILL_WND
		self.pySkItem_.skillType = SKILL_TREE_TYPE
		self.__pySkFrm = PyGUI( item.skFrm )
		self.__pyLvBg = PyGUI(item.lvBg )
		
		self.__pyStCurLv = StaticText( item.stCurLv )
		self.__pyStCurLv.font = "songti.font"
		self.__pyStCurLv.text = ""
		
		self.__pyStMaxLv = StaticText( item.stMaxLv )
		self.__pyStMaxLv.font = "songti.font"
		self.__pyStMaxLv.color = ( 231.0, 186.0, 0.0, 255.0 )
		self.__pyStMaxLv.text = ""
		
		self.__pyBtArrow = PyGUI( item.btArrow )
		self.__pyBtArrow.visible = False
		
		self.__pyBtLine = PyGUI( item.btLine )
		self.__pyBtLine.visible = False
		
		self.teachInfo = None
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def __getLeanedSkill( self, skillID ):
		"""
		判断有没有学习该技能
		"""
		teachId = self.teachInfo.skillID
		teachSk = Skill.getSkill( teachId )
		hasSkills = BigWorld.player().skillList_
		if hasattr( teachSk, "_SkillsMap" ):
			if skillID in teachSk._SkillsMap:
				return skillID, True
			for hasSkID in hasSkills:
				if hasSkID in teachSk._SkillsMap:
					return hasSkID, True
			return 0, True
		else:
			return skillID, False
	
	def getCurSkillID( self ):
		skillID = self.teachInfo.skillID
		teachSkill = Skill.getSkill( skillID )
		ledSkID = self.__getRoleMapSkill( teachSkill )
		return ledSkID
	
	def __getRoleMapSkill( self, teachSk ):
		hasSkills = BigWorld.player().skillList_
		if hasattr( teachSk, "_SkillsMap" ):
			for hasSkID in hasSkills:
				if hasSkID in teachSk._SkillsMap:
					return hasSkID
			return teachSk.getID()
		return 0
	
	def __setCurLvColor( self, color ):
		"""
		设置当前等级颜色
		"""
		self.__pyStCurLv.color = color
	
	def __setMaxLvColor( self, color ):
		"""
		设置最大等级颜色
		"""
		self.__pyStMaxLv.color = color
	
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BaseSkillItem.update( self, itemInfo )
		player = BigWorld.player()
		skillID = itemInfo.id
		skill = itemInfo.baseItem
		leantID, isTeachSk = self.__getLeanedSkill( skillID )
		curLevel = skill.getLevel()
		self.pySkItem_.focus = leantID > 0
		self.pySkItem_.dragFocus = leantID > 0
		maxLevel = 0
		learned = True
		if isTeachSk:	#学习技能
			teachSkID = self.teachInfo.skillID
			teachSk = Skill.getSkill( teachSkID )
			maxLevel = teachSk.getTeachMaxLevel()
			if leantID <= 0:	#未学习
				learned = False
				self.pySkItem_.getGui().materialFX = "COLOUR_EFF"
				util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(2, 2) )
				util.setGuiState( self.__pyLvBg.getGui(),(2, 1),(2, 1) )
				self.__setCurLvColor( (255.0, 255.0, 255.0, 255.0 ) )
				self.__setMaxLvColor( (255.0, 255.0, 255.0, 255.0 ) )
				curLevel = 0
			else:
				self.pySkItem_.getGui().materialFX = "BLEND"
				if skillID in player.chalSkills:
					upgradeSkID = player.getUpgradeSkillID( skillID )
					upgradeSk = Skill.getSkill( upgradeSkID )
					curLevel = upgradeSk.getLevel()
					skillID = upgradeSkID
		else:
			maxLevel = skill.getMaxLevel()
		if self.teachInfo.checkUpgrade( skillID ): #可以升级
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(1, 1) )
			self.__setCurLvColor( (0.0, 255.0, 0.0, 255.0 ) )
			self.__setMaxLvColor( (0.0, 255.0, 0.0, 255.0 ) )
		else:
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(1, 1) )
			self.__setCurLvColor( (255.0, 255.0, 255.0, 255.0 ) )
			self.__setMaxLvColor( (255.0, 255.0, 255.0, 255.0 ) )
		if curLevel >= maxLevel:
			curLevel = maxLevel
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(2, 1) )
			self.__setCurLvColor( ( 231.0, 186.0, 0.0, 255.0 ) )
			self.__setMaxLvColor( ( 231.0, 186.0, 0.0, 255.0 ) )
		self.__pyStCurLv.text = "%d"%curLevel
		self.__pyStMaxLv.text = "%d"%maxLevel
		self.pySkItem_.description = self.teachInfo.getDescription( skillID, learned )

	def onCheckSucc( self ):
		player = BigWorld.player()
		skillID = self.skillInfo.id
		newSkillID = player.getUpgradeSkillID( skillID )
		skill = Skill.getSkill( newSkillID )
		if skill is None:return
		newLevel = skill.getLevel()
		maxLevel = skill.getMaxLevel()
		learned = True
		if self.teachInfo.checkUpgrade( newSkillID ):
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(1, 2) )
			self.__setCurLvColor( (0.0, 255.0, 0.0, 255.0 ) )
			self.__setMaxLvColor( (0.0, 255.0, 0.0, 255.0 ) )
		else:
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(1, 1) )
			self.__setCurLvColor( (255.0, 255.0, 255.0, 255.0 ) )
			self.__setMaxLvColor( (255.0, 255.0, 255.0, 255.0 ) )
		if newLevel >= maxLevel:
			newLevel = maxLevel
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(2, 1) )
			self.__setCurLvColor( ( 231.0, 186.0, 0.0, 255.0 ) )
			self.__setMaxLvColor( ( 231.0, 186.0, 0.0, 255.0 ) )
		if newLevel == 0 and maxLevel == 0:	#未学习
			util.setGuiState( self.__pySkFrm.getGui(),(2, 2),(2, 2) )
			self.__setCurLvColor( (255.0, 255.0, 255.0, 255.0 ) )
			self.__setMaxLvColor ( (255.0, 255.0, 255.0, 255.0 ) )
			learned = False
			
		self.__pyStCurLv.text = "%d"%newLevel
		self.pySkItem_.description = self.teachInfo.getDescription( newSkillID, learned )

	def _getSkillInfo( self ):
		return self.pySkItem_.itemInfo

	skillInfo = property( _getSkillInfo, )

# --------------------------------------------------------------------
# 生活技能熟练度进度条
# --------------------------------------------------------------------
from guis.controls.StaticText import StaticText
from guis.controls.ProgressBar import HFProgressBar

class LSProgressBar( GUIBaseObject ) :

	def __init__( self, pbar ) :
		GUIBaseObject.__init__( self, pbar )

		self.__pySTRate = StaticText( pbar.lbValue )
		self.__pySTRate.text = "100/500"
		self.__pyPGBar = HFProgressBar( pbar.bar )
		self.__pyPGBar.value = 100/500.0


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getCurrValue( self ) :
		text = self.__pySTRate.text
		if text == "" :
			return 0
		return int( text.split( "/" )[0] )

	def _setCurrValue( self, value ) :
		upperLimit = self.upperLimit
		self.__pySTRate.text = "%d/%d" % ( value, upperLimit )
		if upperLimit <= 0 :
			self.__pyPGBar.value = 0
		else :
			self.__pyPGBar.value = float( value  ) / upperLimit

	def _getUpperLimit( self ) :
		text = self.__pySTRate.text
		if text == "" :
			return 0
		return int( text.split( "/" )[1] )

	def _setUpperLimit( self, value ) :
		if value <= 0 :
			self.__pySTRate.text = ""
			self.__pyPGBar.value = 0
		else :
			currValue = self.currValue
			self.__pySTRate.text = "%d/%d" % ( currValue, value )
			self.__pyPGBar.value = float( currValue  ) / value

	currValue = property( _getCurrValue, _setCurrValue )
	upperLimit = property( _getUpperLimit, _setUpperLimit )

class SkillItem( SkItem ):
	
	def __init__( self, item, pyBinder = None ):
		SkItem.__init__( self, item, pyBinder )
		self.skillType = SKILL_BASE_TYPE

	def onLClick_( self, mods ):
		SkItem.onLClick_( self, mods )
		player = BigWorld.player()
		pyBinder = self.pyBinder
		if self.skillType == SKILL_TREE_TYPE:
			if pyBinder.itemInfo is None:return True
			skillID = pyBinder.getCurSkillID()
			if skillID == 0:return True
			if mods == 0:
				player.checkUpgradeSkill( skillID )
			elif mods == MODIFIER_CTRL: #升级到当前可升级的最大等级
				player.gm_upGradeSkLitToMax( skillID )
				
			elif mods == MODIFIER_SHIFT: #升级到技能的最大等级
				player.gm_upGradeSkToMax( skillID )
			return True
		
	def onRClick_( self, mods ):
		SkItem.onRClick_( self, mods )
		player = BigWorld.player()
		pyBinder = self.pyBinder
		if self.skillType == SKILL_TREE_TYPE:
			if pyBinder.itemInfo is None:return True
			skillID = pyBinder.getCurSkillID()
			if skillID == 0:return True
			if mods == 0:
				player.downgradeSkill( skillID )
			elif mods == MODIFIER_CTRL: #删除该技能
				player.gm_removeSkill( skillID )
			return True
		elif self.skillType == SKILL_EXTEND_TYPE:
			if not ( pyBinder.itemInfo is None or pyBinder.itemInfo.isPassive ) :
				pyBinder.itemInfo.spell()
			return True
	
