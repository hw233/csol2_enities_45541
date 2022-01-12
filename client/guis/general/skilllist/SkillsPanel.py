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
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
from config.client.LivingSkillUpgradeClew import Datas as lvs_UpgradeDatas
from LivingConfigMgr import LivingConfigMgr
lvcMgr = LivingConfigMgr.instance()
import skills


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
		self.__pageControlPanel = ODPagesPanel( skillsPanel.itemsPanel, skillsPanel.pgIdxBar )
		self.__pageControlPanel.onViewItemInitialized.bind( self.__initListItem )
		self.__pageControlPanel.onDrawItem.bind( self.__drawListItem )
		self.__pageControlPanel.nOrder = True

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
		for pyViewItem in self.__pageControlPanel.pyViewItems :
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
		for pyViewItem in self.__pageControlPanel.pyViewItems :
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
		for pyViewItem in self.__pageControlPanel.pyViewItems :
			skillInfo = pyViewItem.pageItem
			pySkillItem = pyViewItem.pySkillItem
			if skillInfo is None:continue
			if pySkillItem is None:continue
			if skillInfo.baseItem.getID() == defaultSkID :
				pySkillItem.showAutoParticle()
			else:
				pySkillItem.hideAutoParticle()

	def __onAutoSkStop( self, defaultSkID ):
		for pyViewItem in self.__pageControlPanel.pyViewItems :
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

	def __initListItem( self, pyViewItem ) :
		"""
		初始化添加的技能列表项
		"""
		pySkillItem = self.getPyPageItem_( pyViewItem )
		pyViewItem.pySkillItem = pySkillItem
		pyViewItem.addPyChild( pySkillItem )
		pySkillItem.left = 0
		pySkillItem.top = 0

	def __drawListItem( self, pyViewItem ) :
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
		self.__pageControlPanel.viewSize = size

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
		for pyViewItem in self.__pageControlPanel.pyViewItems :
			if pyViewItem.pageItem is None : continue
			pyViewItem.pySkillItem.description = pyViewItem.pageItem.description

	def addSkill( self, skillInfo ):
		if skillInfo not in self.__pageControlPanel.items:
			self.__pageControlPanel.addItem( skillInfo )

	def removeSkill( self, skillID ):
		for skillInfo in self.__pageControlPanel.items:
			if skillInfo.id == skillID:
				self.__pageControlPanel.removeItem( skillInfo )
				break

	def updateSkill( self, oldSkillID, newSkillInfo ): # 更新当前页技能信息
		for idx, skillInfo in enumerate( self.__pageControlPanel.items ): # 更新技能信息列表中相应位置技能
			if skillInfo.id == oldSkillID:
				self.__pageControlPanel.updateItem( idx, newSkillInfo )
				break

	def clearItems( self ):
		self.__pageControlPanel.clearItems()
		self.__onHideSpellingCover()

	def show( self ):
		self.__pageControlPanel.pageIndex = 0

	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getItems( self ):
		return self.__pageControlPanel.items

	items = property( _getItems )


# --------------------------------------------------------------------
# 普通技能、被动技能、表情动作界面
# --------------------------------------------------------------------
class SkillsPanel( BaseSkillsPanel ) :

	def __init__( self, skillsPanel = None, pyBinder = None ):
		BaseSkillsPanel.__init__( self, skillsPanel, pyBinder )
		self.initViewSize_( ( 8, 2 ) )


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
class LiveSkillsPanel( BaseSkillsPanel ) :

	def __init__( self, skillsPanel = None, pyBinder = None ):
		BaseSkillsPanel.__init__( self, skillsPanel, pyBinder )
		self.initViewSize_( ( 4, 1 ) )


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def getPyPageItem_( self, pyViewItem ) :
		"""
		获取技能
		"""
		return LiveSkillItem( pyViewItem )


# --------------------------------------------------------------------
# 实现技能选项类
# --------------------------------------------------------------------
from guis.controls.SkillItem import SkillItem
from guis.controls.CircleCDCover import CircleCDCover as Cover
from guis.otheruis.AnimatedGUI import AnimatedGUI

class BaseSkillItem( GUIBaseObject ) :

	def __init__( self, item, pyBinder = None ) :
		GUIBaseObject.__init__( self, item )

		self.pySkItem_ = SkillItem( item.icon )
		self.pySkItem_.crossFocus = False
		self.pySkItem_.onRClick.bind( self.onItemRClick_ )
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
		icon = skills.getSkill( self.itemInfo.id ).getIcon()
		if self.pySkItem_.icon[0] != icon:
			self.pySkItem_.icon = icon


	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onItemRClick_( self, mods ):
		pass

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
		self.__pySkName = StaticText( item.stName )
		self.__pySkLevel = StaticText( item.stLevel )

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onItemRClick_( self, mods ):
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
			self.__pySkName.text = itemInfo.name
			self.__pySkLevel.text = labelGather.getText( "SkillList:main", "skillLevel", itemInfo.level )
		else :
			self.__pySkName.text = ""
			self.__pySkLevel.text = ""


# --------------------------------------------------------------------
# 生活技能格子
# --------------------------------------------------------------------
class LiveSkillItem( BaseSkillItem ) :

	def __init__( self, pyBinder = None ) :
		item = GUI.load( "guis/general/skilllist/liveskillitem.gui" )
		uiFixer.firstLoadFix( item )
		BaseSkillItem.__init__( self, item, pyBinder )

		self.pySkItem_.dragFocus = False
		self.__pySkName = CSRichText( item.rtSkillName )
		self.__pySkName.foreColor = ( 252, 235, 179, 255 )
		self.__pySkLevel = CSRichText( item.rtSkillLevel )
		self.__pySkLevel.foreColor = ( 252, 235, 179, 255 )
		self.__pyUpgradeClew = CSRichText( item.rtUpgradeClew )
		self.__pyProgBar = LSProgressBar( item.progBar )


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def update( self, itemInfo ) :
		BaseSkillItem.update( self, itemInfo )
		if itemInfo is not None :
			skillName = PL_Font.getSource( itemInfo.name, fc = ( 255, 255, 255, 255 ) )
			self.__pySkName.text = labelGather.getText( "SkillList:main", "liveSkillName", skillName )
			skID = itemInfo.id
			skillInfo = BigWorld.player().livingskill.get( skID, (0, 0) )
			skLV = skillInfo[1]
			dspText = lvcMgr.getDesByLevel( skID, skLV )
			if dspText is not None :
				levelStr = dspText.split( "|" )[-1]
				levelStr = PL_Font.getSource( levelStr, fc = ( 255, 255, 255, 255 ) )
				self.__pySkLevel.text = labelGather.getText( "SkillList:main", "liveSkillLevel", levelStr )
			else :
				ERROR_MSG( "Error living skill config! Skill %s in level %s not found!" % ( skID, skLV ) )
				self.__pySkLevel.text = "None"
			self.__pyUpgradeClew.text = lvs_UpgradeDatas[ skLV ]
			sleightMax = lvcMgr.getMaxSleightByLevel( skID, skLV )
			self.__pyProgBar.currValue = skillInfo[0]
			self.__pyProgBar.upperLimit = sleightMax
			self.__pyProgBar.visible = True
			#self.gui.itemBg.visible = True
		else :
			self.__pySkName.text = ""
			self.__pySkLevel.text = ""
			self.__pyUpgradeClew.text = ""
			self.__pyProgBar.visible = False
			#self.gui.itemBg.visible = False


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
