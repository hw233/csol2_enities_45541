# -*- coding: gb18030 -*-
#
# $Id: SkillsPanel.py,v 1.13 2008-08-28 01:20:09 songpeifang Exp $

from guis import *
from LabelGather import labelGather
from guis.controls.Control import Control
from guis.controls.TabCtrl import TabPanel
from guis.controls.StaticText import StaticText
from guis.controls.ODPagesPanel import ODPagesPanel
from guis.common.GUIBaseObject import GUIBaseObject
from guis.tooluis.CSRichText import CSRichText
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from guis.tooluis.richtext_plugins.PL_Space import PL_Space
from config.client.LivingSkillUpgradeClew import Datas as lvs_UpgradeDatas
from SkillItem import BaseSkillItem, ExtendSkillItem, LiveSkillItem, TongSkillItem, ChallengeSkItem
from ItemsFactory import SkillItem as SkillInfo
from LivingConfigMgr import LivingConfigMgr
lvcMgr = LivingConfigMgr.instance()
from TongSkillResearchData import TongSkillResearchData
tongSkillResearch = TongSkillResearchData.instance()
from SkillUpgradeConfigLoader import chSkillLoader
import skills
import csdefine
import TongDatas
tongSkillDatas = TongDatas.tongSkill_instance()

SKILL_TYPE_COMMON	= 0
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

class BaseSkillsPanel( TabPanel ):

	def __init__( self, skillsPanel = None, pyBinder = None ):
		TabPanel.__init__( self, skillsPanel, pyBinder )
		self.__spellingItems = []	# 正在施放的技能
		self.__invalidItems = []	# 选中的不可用技能
		self.__cdCoverCBID	= 0
		self.__triggers = {}
		self.__registerTriggers()
		self.__initSkills( skillsPanel )


	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initSkills( self, skillsPanel ):
		self.pageControlPanel_ = ODPagesPanel( skillsPanel.itemsPanel, skillsPanel.pgIdxBar )
		self.pageControlPanel_.onViewItemInitialized.bind( self.initListItem_ )
		self.pageControlPanel_.onDrawItem.bind( self.drawListItem_ )
		
		self.__pyLbTitle = StaticText( skillsPanel.title.lbTitle )
		self.__pyLbTitle.text = ""

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
		for pyViewItem in self.pageControlPanel_.pyViewItems :
			skillInfo = pyViewItem.pageItem
			if skillInfo is not None and skillInfo.baseItem.getID() == skillID :
				pySkillItem = pyViewItem.pySkillItem
				self.__spellingItems.append( pySkillItem )
				toolbox.itemCover.showSpellingItemCover( pySkillItem.pyItem )

	def __onHideSpellingCover( self ) :
		"""
		隐藏图标的高亮显示状态
		"""
		for pySkillItem in self.__spellingItems :
			toolbox.itemCover.hideItemCover( pySkillItem.pyItem )
		self.__spellingItems = []

	def __onShowInvalidCover( self, skillID ) :
		"""
		点击不可用技能时用红色边框显示
		"""
		BigWorld.cancelCallback( self.__cdCoverCBID )
		self.__hideInvalidItemCovers()
		for pyViewItem in self.pageControlPanel_.pyViewItems :
			skillInfo = pyViewItem.pageItem
			if skillInfo is not None and skillInfo.baseItem.getID() == skillID :
				pySkillItem = pyViewItem.pySkillItem
				self.__invalidItems.append( pySkillItem )
				toolbox.itemCover.showInvalidItemCover( pySkillItem.pyItem )
		self.__cdCoverCBID = BigWorld.callback( 1, self.__hideInvalidItemCovers )		# 标记在1秒后自动隐藏

	def __onAutoSkChange( self, defaultSkID ):
		"""
		自动战斗技能
		"""
		for pyViewItem in self.pageControlPanel_.pyViewItems :
			skillInfo = pyViewItem.pageItem
			pySkillItem = pyViewItem.pySkillItem
			if skillInfo is None:continue
			if pySkillItem is None:continue
			if skillInfo.baseItem.getID() == defaultSkID :
				pySkillItem.showAutoParticle()
			else:
				pySkillItem.hideAutoParticle()

	def __onAutoSkStop( self, defaultSkID ):
		for pyViewItem in self.pageControlPanel_.pyViewItems :
			skillInfo = pyViewItem.pageItem
			pySkillItem = pyViewItem.pySkillItem
			if skillInfo is None:continue
			if pySkillItem is None:continue
			if skillInfo.baseItem.getID() == defaultSkID :
				pySkillItem.hideAutoParticle()
				break

	def __hideInvalidItemCovers( self ) :
		"""
		隐藏不可用技能的红色边框
		"""
		for pySkillItem in self.__invalidItems :
			toolbox.itemCover.hideItemCover( pySkillItem.pyItem )
		self.__invalidItems = []

	def initListItem_( self, pyViewItem ) :
		"""
		初始化添加的技能列表项
		"""
		pySkillItem = self.getPyPageItem_( pyViewItem )
		pyViewItem.pySkillItem = pySkillItem
		pyViewItem.addPyChild( pySkillItem )
		pySkillItem.left = 0
		pySkillItem.top = 0

	def drawListItem_( self, pyViewItem ) :
		"""
		重画技能列表项
		"""
		skillInfo = pyViewItem.pageItem
		pySkillItem = pyViewItem.pySkillItem
		pySkillItem.update( skillInfo )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def initViewSize_( self, size ) :
		"""
		初始化技能列表行列数
		"""
		self.pageControlPanel_.viewSize = size

	def getPyPageItem_( self, pyViewItem ) :
		"""
		获取技能
		"""
		pass


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def refreshSkills( self ) :
		"""
		刷新技能信息
		"""
		for pyViewItem in self.pageControlPanel_.pyViewItems :
			if pyViewItem.pageItem is None : continue
			pyViewItem.pySkillItem.description = pyViewItem.pageItem.description

	def addSkill( self, skillInfo ):
		if skillInfo not in self.pageControlPanel_.items:
			self.pageControlPanel_.addItem( skillInfo )

	def removeSkill( self, skillID ):
		for skillInfo in self.pageControlPanel_.items:
			if skillInfo.id == skillID:
				self.pageControlPanel_.removeItem( skillInfo )
				break

	def updateSkill( self, oldSkillID, newSkillInfo ): # 更新当前页技能信息
		for idx, skillInfo in enumerate( self.pageControlPanel_.items ): # 更新技能信息列表中相应位置技能
			if skillInfo.id == oldSkillID:
				self.pageControlPanel_.updateItem( idx, newSkillInfo )
				break

	def getSkillInfos( self ):
		return self.pageControlPanel_.items
		
	def clearItems( self ):
		self.pageControlPanel_.clearItems()
		self.__onHideSpellingCover()
	
	def setTitle( self, title ):
		self.__pyLbTitle.text = title

	def show( self ):
		self.pageControlPanel_.pageIndex = 0

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItems( self ):
		return self.pageControlPanel_.items

	items = property( _getItems )

# --------------------------------------------------------------------
# 普通技能、被动技能、表情动作界面
# --------------------------------------------------------------------
class SkillsPanel( BaseSkillsPanel ) :

	def __init__( self, skillsPanel = None, pyBinder = None ):
		BaseSkillsPanel.__init__( self, skillsPanel, pyBinder )
		self.pageControlPanel_.nOrder = False
		self.initViewSize_( ( 5, 3 ) )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getPyPageItem_( self, pyViewItem ) :
		"""
		获取技能
		"""
		return ExtendSkillItem( pyViewItem )
# --------------------------------------------------------------------
# 生活技能界面
# --------------------------------------------------------------------
from config.client.msgboxtexts import Datas as mbmsgs
class LiveSkillsPanel( BaseSkillsPanel ) :

	def __init__( self, skillsPanel = None, pyBinder = None ):
		BaseSkillsPanel.__init__( self, skillsPanel, pyBinder )
		self.initViewSize_( ( 1, 2 ) )
		
		self.pageControlPanel_.selectable = True
		self.pageControlPanel_.onItemSelectChanged.bind( self.__onItemSelectChanged )
		
		self.__pyBtnGiveUpSkill = HButtonEx( skillsPanel.descriptionPanel.btnGiveup )
		self.__pyBtnGiveUpSkill.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnGiveUpSkill.onLClick.bind( self.__onGiveUpSkill )
		self.__pyBtnGiveUpSkill.enable = False
		labelGather.setPyBgLabel( self.__pyBtnGiveUpSkill, "SkillList:main","btnGiveup" )
		
		self.__pyStSkillDesc = CSRichText( skillsPanel.descriptionPanel.rtDescription )
		self.__pyStSkillDesc.text = ""
		
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------		
	def __onItemSelectChanged( self, index ):	
		if index < 0:
			self.__pyStSkillDesc.text = ""
			self.__pyBtnGiveUpSkill.enable = False
		else:		
			self.__pyBtnGiveUpSkill.enable = True
					
		for pyViewItem in self.pageControlPanel_.pyViewItems:
			liveSkillItem = pyViewItem.pySkillItem
			itemIndex = pyViewItem.itemIndex
			liveSkillItem.selected = itemIndex ==  index
			if index == itemIndex:
				self.__setDescription( liveSkillItem.itemInfo )
	
	def __setDescription( self, itemInfo ):
		"""
		设置技能说明以及采集能获得什么原料
		"""
		player = BigWorld.player()
		if itemInfo is not None:
			skillID = itemInfo.id
			livingSk = player.livingskill.get( skillID, (0, 0) )
			livingStr = lvcMgr.getDes2ByLevel( skillID , livingSk[1] )
			self.__pyStSkillDesc.text = PL_NewLine.getSource()
			self.__pyStSkillDesc.text += PL_Space.getSource( 2 )
			self.__pyStSkillDesc.text += livingStr	
				
	def __onGiveUpSkill( self ):
		itemInfo =self.pageControlPanel_.selItem
		if itemInfo is not None:
			skillID = itemInfo.id
			def query( rs_id ) :
				if rs_id == RS_OK :
					BigWorld.player().cell.onTeachTalkObliveSkill( skillID )
			showMessage( mbmsgs[ 0x00e3 ] % itemInfo.name, "", MB_OK_CANCEL, query )
			
	def __refreshSkills( self ):
		skInfos = self.getSkillInfos()
		BaseSkillsPanel.clearItems( self )
		for skInfo in skInfos:
			BaseSkillsPanel.addSkill( self, skInfo )	
				
	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------	
	def initListItem_( self, pyViewItem ) :
		"""
		初始化添加的技能列表项
		"""
		pySkillItem = self.getPyPageItem_( pyViewItem )
		pyViewItem.pySkillItem = pySkillItem
		pyViewItem.addPyChild( pySkillItem )
		pyViewItem.focus = True
		pySkillItem.left = 0
		pySkillItem.top = 0
		
	def getPyPageItem_( self, pyViewItem ) :
		"""
		获取技能
		"""
		return LiveSkillItem( pyViewItem )
		
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------	
	def onEnterWorld( self ):
		pass

	def addSkill( self, skillInfo ):
		skInfos = self.getSkillInfos()
		for skiInfo in skInfos:
			skill = skiInfo.baseItem
			if skiInfo.id/1000 == skillInfo.id/1000:
				BaseSkillsPanel.updateSkill( self, skiInfo.id, skillInfo )
				return	
		BaseSkillsPanel.addSkill( self, skillInfo )
			
	def removeSkill( self, skillID ):
		"""
		"""
		BaseSkillsPanel.removeSkill( self, skillID )
		self.__refreshSkills()

# ------------------------------------------------------------------------
class TongSkillsPanel( BaseSkillsPanel ):
	def __init__( self, skillsPanel = None, pyBinder = None ):
		BaseSkillsPanel.__init__( self, skillsPanel, pyBinder )
		self.pageControlPanel_.nOrder = False
		self.initViewSize_( ( 5, 3 ) )

	def onEnterWorld( self ):
		reSkDatas = tongSkillDatas.getDatas() #只获取角色帮会技能
		skillIds = reSkDatas.keys()
		skillIds.sort()
		for skId in skillIds:
			mapSkill = self.getPlayerMapSkill( skId )
			if mapSkill > 0:
				skId = mapSkill
			else:
				skId += 1
			skill = skills.getSkill( skId )
			skillInfo = SkillInfo( skill )
			BaseSkillsPanel.addSkill( self, skillInfo )
	
	def addSkill( self, skillInfo ):
		skInfos = self.getSkillInfos()
		for skiInfo in skInfos:	
			if skiInfo.id/1000 == skillInfo.id/1000:
				BaseSkillsPanel.updateSkill( self, skiInfo.id, skillInfo )
				
	def removeSkill( self, skillID ):
		"""
		删除技能其实是更新为1级未学习的技能
		"""
		skInfos = self.getSkillInfos()
		for skiInfo in skInfos:
			if skiInfo.id/1000 == skillID/1000:
				newSkillID = ( skiInfo.id/1000 )*1000 + 1
				skill = skills.getSkill( newSkillID )
				skillInfo = SkillInfo( skill )
				BaseSkillsPanel.updateSkill( self, skiInfo.id, skillInfo )							
	
	def getPlayerMapSkill( self, skillId ):
		skillIds = BigWorld.player().skillList_	
		for skId in skillIds:
			if skId/1000 == skillId/1000:
				return skId
		return 0

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getPyPageItem_( self, pyViewItem ) :
		"""
		获取技能
		"""
		return TongSkillItem( pyViewItem )
		
# ---------------------------------------------------------------------------------
from guis.controls.ODListPanel import ODListPanel
from guis.tooluis.CSTextPanel import CSTextPanel

class ChallengePanel( TabPanel ):
	"""
	挑战副本技能面板
	"""
	def __init__( self, skillsPanel = None, pyBinder = None ):
		TabPanel.__init__( self, skillsPanel, pyBinder )
		self.__spellingItems = []	# 正在施放的技能
		self.__invalidItems = []	# 选中的不可用技能
		self.__cdCoverCBID = 0
		self.__triggers = {}
		self.__registerTriggers()
		self.__initSkills( skillsPanel )
	
	def __initSkills( self, panel ):
		self.__pySkillsPanel = ODListPanel( panel.skillsPanel.listPanel, panel.skillsPanel.listBar )
		self.__pySkillsPanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pySkillsPanel.onDrawItem.bind( self.__drawListItem )
		self.__pySkillsPanel.ownerDraw = True
		self.__pySkillsPanel.itemHeight = 80.0
		self.__pySkillsPanel.autoSelect = True
		
		self.__pyInfoPanel = CSTextPanel( panel.dspPanel.listPanel, panel.dspPanel.listBar )
		self.__pyInfoPanel.opGBLink = True
		self.__pyInfoPanel.foreColor = ( 230, 227, 185, 255 )

		self.__pyLbTitle = StaticText( panel.title.lbTitle )
		self.__pyLbTitle.text = ""
		
		self.__pyBtnReset = HButtonEx( panel.btnReset )
		self.__pyBtnReset.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnReset.onLClick.bind( self.__onReSet )
		labelGather.setPyBgLabel( self.__pyBtnReset, "SkillList:main","reset" )

		self.__pyBtnOk = HButtonEx( panel.btnOk )
		self.__pyBtnOk.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnOk.onLClick.bind( self.__onOk )
		labelGather.setPyBgLabel( self.__pyBtnOk, "SkillList:main","ok" )
		
		self.__pyStRolePot = StaticText( panel.stPotent )
		self.__pyStRolePot.text = ""

	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_SPELLING_COVER"]	= self.__onShowSpellingCover		# 高亮显示正在施放的技能
		self.__triggers["EVT_ON_HIDE_SPELLING_COVER"]	= self.__onHideSpellingCover		# 隐藏技能的高亮显示
		self.__triggers["EVT_ON_SHOW_INVALID_COVER"]	= self.__onShowInvalidCover			# 点击不可用技能时显示红色边框
		self.__triggers["EVT_ON_AUTO_NOR_SKILL_CHANGE"] = self.__onAutoSkChange				# 自动战斗技能
		self.__triggers["EVT_ON_STOP_AUTO_SKILL"]		= self.__onAutoSkStop
		self.__triggers["EVT_ON_ROLE_CHECK_CHASKILL_SUCC"]		= self.__onCheckChaSkSucc
		self.__triggers["EVT_ON_ROLE_POTENTIAL_CHANGED"] = self.__onRolePotenChanged # 潜能
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# --------------------------------------------------------
	def __initListItem( self, pyViewItem ):
		item = GUI.load( "guis/general/skilltree/skitem.gui" )
		uiFixer.firstLoadFix( item )
		itemIndex = pyViewItem.itemIndex
		pyChaSkItem = ChallengeSkItem( item, itemIndex, self )
		pyViewItem.addPyChild( pyChaSkItem )
		pyChaSkItem.pos = -1.0, 1.0
		pyViewItem.pyItem = pyChaSkItem

	def __drawListItem( self, pyViewItem ) :
		pyChaSkItem = pyViewItem.pyItem
		skillInfos = pyViewItem.listItem
		itemIndex = pyViewItem.itemIndex
		pyChaSkItem.itemIndex = itemIndex
		pyChaSkItem.teachInfo = skillInfos[0]
		pyChaSkItem.update( skillInfos[1] )
		
	def __onShowSpellingCover( self, skillID ) :
		"""
		用高亮图标标识正在施放的技能
		@param		skillID	:	技能ID
		@type		skillID	:	SKILLID( INT64 )
		"""
		self.__onHideSpellingCover()
		for pyViewItem in self.__pySkillsPanel.pyViewItems:
			pySkItem = pyViewItem.pyItem
			skillInfo = pyViewItem.listItem[1]
			if skillInfo and skillInfo.baseItem.getID() == skillID :
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
		for pyViewItem in self.__pySkillsPanel.pyViewItems:
			pySkItem = pyViewItem.pyItem
			skillInfo = pyViewItem.listItem[1]
			if skillInfo and skillInfo.baseItem.getID() == skillID :
				self.__invalidItems.append( pySkItem )
				toolbox.itemCover.showInvalidItemCover( pySkItem.pyItem )
		self.__cdCoverCBID = BigWorld.callback( 1, self.__hideInvalidItemCovers )		# 标记在1秒后自动隐藏

	def __onAutoSkChange( self, defaultSkID ):
		"""
		自动战斗技能
		"""
		for pyViewItem in self.__pySkillsPanel.pyViewItems:
			pySkItem = pyViewItem.pyItem
			skillInfo = pyViewItem.listItem[1]
			if skillInfo.baseItem.getID() == defaultSkID :
				pySkItem.showAutoParticle()
			else:
				pySkItem.hideAutoParticle()

	def __onAutoSkStop( self, defaultSkID ):
		for pyViewItem in self.__pySkillsPanel.pyViewItems:
			pySkItem = pyViewItem.pyItem
			skillInfo = pyViewItem.listItem[1]
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
	
	def __onCheckChaSkSucc( self, skillID ):
		skill = skills.getSkill( skillID )
		skillInfo = SkillInfo( skill )
		self.__onCheckSucc( skillInfo )
		player = BigWorld.player()
		reqPotent = player.getTotalPotential( True )
		remPotent = player.potential - reqPotent
		if remPotent <= 0:
			remPotent = 0
		self.__pyStRolePot.text = labelGather.getText( "SkillList:main", "rolePotent" )%str( remPotent )
		
	def __onRolePotenChanged( self, oldValue, newValue ):
		"""
		角色潜能点改变
		"""
		self.__pyStRolePot.text = labelGather.getText( "SkillList:main", "rolePotent" )%str( newValue )
	
	def __onCheckSucc( self, skInfo ):
		for pyViewItem in self.__pySkillsPanel.pyViewItems:
			pySkItem = pyViewItem.pyItem
			skillInfo = pyViewItem.listItem[1]
			if skInfo.id == skillInfo.id:
				pySkItem.onCheckSucc()
	
	def __getChSkillDesp( self, chSkillId ):
		player = BigWorld.player()
		pclass = player.getClass()
		cskInfos = chSkillLoader.getChSkInfos( pclass )
		desp = ""
		if not chSkillId in [cskInfo.skillID for cskInfo in cskInfos]:
			chSkillId = int( "9" +"%d"%((chSkillId/1000)*1000) )
		desp = chSkillLoader.getChSkDesp( pclass, chSkillId )
		return desp
	
	def __onReSet( self, pyBtn ):
		if pyBtn is None:return
		BigWorld.player().cancelUpgradeSkill( True )

	def __onOk( self, pyBtn ):
		if pyBtn is None:return
		BigWorld.player().upgradeSkills( True )
	
	def onItemSlected( self, index ):
		selchSkId = 0
		for idx, pyViewItem in enumerate( self.__pySkillsPanel.pyViewItems ):
			pyChaSkItem = pyViewItem.pyItem
			pyChaSkItem.selected = idx == index
			if idx == index:
				selchSkId = pyViewItem.listItem[1].id
		desp= self.__getChSkillDesp( selchSkId )
		self.__pyInfoPanel.text = desp

	def addSkill( self, skillInfo ):
		for idx, chSkillInfo in enumerate( self.__pySkillsPanel.items ):
			teachId = chSkillInfo[0].skillID
			teachSkill = skills.getSkill( teachId )
			if hasattr( teachSkill, "_spellTeach" ):
				spellTeach = teachSkill._spellTeach
				if spellTeach/1000 == skillInfo.id/1000:
					self.__pySkillsPanel.updateItem( idx, [chSkillInfo[0], skillInfo] )

	def updateSkill( self, oldSkillID, newSkillInfo ): 
		for idx, chSkillInfo in enumerate( self.__pySkillsPanel.items ):
			if chSkillInfo[1].id == oldSkillID:
				self.__pySkillsPanel.updateItem( idx, [chSkillInfo[0], newSkillInfo] )
				break

	def removeSkill( self, skillID ):
		for chSkillInfo in self.__pySkillsPanel.items:
			if chSkillInfo[1].id == skillID:
				self.__pySkillsPanel.removeItem( chSkillInfo )

	def clearItems( self ):
		self.__pySkillsPanel.clearItems()
		self.__onHideSpellingCover()

	def setTitle( self, title ):
		self.__pyLbTitle.text = title

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )
	
	def onEnterWorld( self ):
		"""
		进入游戏，初始化技能树面板
		"""
		player = BigWorld.player()
		pclass = player.getClass()
		cskInfos = chSkillLoader.getChSkInfos( pclass )
		for cskInfo in cskInfos:
			skillID = cskInfo.skillID
			mapSkId = self.getMapSkillId( skillID )
			if mapSkId > 0:
				skillID = mapSkId
			skill = skills.getSkill( skillID )
			skillInfo = SkillInfo( skill )
			self.__pySkillsPanel.addItem( [cskInfo, skillInfo] )

	def getMapSkillId( self, skillID ):
		player = BigWorld.player()
		skill = skills.getSkill( skillID )
		spellTeach = skill._spellTeach
		for rSkillId in player.skillList_:
			if rSkillId/1000 == spellTeach/1000:
				return rSkillId
		return 0
	
	def show( self ):
		pass