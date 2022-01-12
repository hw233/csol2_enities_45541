# -*- coding: gb18030 -*-
#
# $Id: AutoFightBar.py,v 1.15 2008-08-26 02:18:33 huangyongwei Exp $

import event.EventCenter as ECenter
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.Button import Button
from AutoFightItem import AutoFightItem
from guis.general.autoFightWindow.AutoFightWindow import AutoFightWindow
from LabelGather import labelGather
from ItemsFactory import SkillItem
import skills as Skills
import csconst
import csdefine

class AutoFightBar( PyGUI ) :
	def __init__( self, qb ) :
		PyGUI.__init__( self, qb )
		self.__triggers = {}
		self.__registerTriggers()

		self.__pyItems = {}
		self.__spellingItems = []		# 正在释放的技能
		self.__invalidItems = []		# 选中的不可用技能
		self.__cancelCoverCBID = 0
		self.autoSkIDs = 5*[-1]#自动战斗技能列表
		self.__isFirstEnterChallenge = False

		self.__initialize( qb )

	def __initialize( self, qb ) :
		self.__initQBItems( qb )
		self.__pySettingBtn = Button( qb.settingBtn, self )
		self.__pySettingBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pySettingBtn.onLClick.bind( self.__onShowSetting )

		self.__pyOpenBtn = Button( qb.openBtn, self )
		self.__pyOpenBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyOpenBtn.onLClick.bind( self.__onStart )
		self.__pyOpenBtn.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyOpenBtn.onMouseLeave.bind( self.__onBtnMouseLeave )

		self.__pyCloseBtn = Button( qb.closeBtn, self )
		self.__pyCloseBtn.setStatesMapping( UIState.MODE_R3C1 )
		self.__pyCloseBtn.onLClick.bind( self.__onClose )
		self.__pyCloseBtn.onMouseEnter.bind( self.__onBtnMouseEnter )
		self.__pyCloseBtn.onMouseLeave.bind( self.__onBtnMouseLeave )

		# -------------------------------------------------
		# 设置标签
		# -------------------------------------------------
		labelGather.setPyBgLabel( self.__pySettingBtn, "quickbar:afBar", "btnSetting" )
		labelGather.setPyBgLabel( self.__pyOpenBtn, "quickbar:afBar", "btnOpen" )
		labelGather.setPyBgLabel( self.__pyCloseBtn, "quickbar:afBar", "btnClose" )

	def dispose( self ) :
		RootGUI.dispose( self )
		self.__deregisterTriggers()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __initQBItems( self, qb ) :
		for name, item in qb.children :
			if "item_" not in name : continue
			index = int( name.split( "_" )[1] )
			pyItem = AutoFightItem( item.icon, self )
			gbIndex = csdefine.QB_AUTO_SPELL_INDEX + index
			pyItem.gbIndex = gbIndex
			pyItem.gbCopy = True
			description = ""
			if index in range(5):
				description = labelGather.getText( "quickbar:afBar", "tipsSkillItem" )
			elif index == 5:
				description = labelGather.getText( "quickbar:afBar", "tipsHPItem" )
			else:
				description = labelGather.getText( "quickbar:afBar", "tipsMPItem" )
			pyItem.description = description
			pyItem.onLMouseDown.bind( self.__onBarMouseDown )
			pyItem.onMouseEnter.bind( self.__onBarMouseEnter )
			pyItem.onMouseLeave.bind( self.__onBarMouseLeave )
			self.__pyItems[pyItem.gbIndex] = pyItem

	# -------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_QUICKBAR_UPDATE_ITEM"] = self.__onUpdateItem
		self.__triggers["EVT_ON_START_AUTOFIGHT"] = self.__startAutoFight
		self.__triggers["EVT_ON_STOP_AUTOFIGHT"] = self.__stopAutoFight
		self.__triggers["EVT_ON_SHOW_SPELLING_COVER"]	= self.__onShowSpellingCover		# 高亮显示正在施放的技能
		self.__triggers["EVT_ON_HIDE_SPELLING_COVER"]	= self.__onHideSpellingCover		# 隐藏技能的高亮显示
		self.__triggers["EVT_ON_SHOW_INVALID_COVER"]	= self.__onShowInvalidCover			# 点击不可用技能时显示红色边框
		self.__triggers["EVT_ON_ENTER_SPECIAL_COPYSPACE"] = self.__onEnterSpaceCopy
		self.__triggers["EVT_ON_LEAVE_CHALLENGE_COPY"] = self.__onLeaveSpaceCopy
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __onShowSpellingCover( self, skillID ) :
		"""
		用高亮图标标识正在施放的技能
		@param		skillID	:	技能ID
		@type		skillID	:	SKILLID( INT64 )
		"""
		self.__onHideSpellingCover()
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is None : continue
			if pyItem in self.__spellingItems : continue
			if not hasattr( pyItem.itemInfo.baseItem, "getID" ) : continue
			if pyItem.itemInfo.baseItem.getID() == skillID :
				self.__spellingItems.append( pyItem )
				toolbox.itemCover.showSpellingItemCover( pyItem )

	def __onHideSpellingCover( self ) :
		"""
		隐藏图标的高亮显示状态
		"""
		for pyItem in self.__spellingItems :
			toolbox.itemCover.hideItemCover( pyItem )
		self.__spellingItems = []

	def __onShowInvalidCover( self, skillID ) :
		"""
		点击不可用技能时用红色边框显示
		"""
		BigWorld.cancelCallback( self.__cancelCoverCBID )
		self.__hideInvalidItemCovers()
		for pyItem in self.__pyItems.itervalues() :
			if pyItem.itemInfo is None : continue
			if pyItem in self.__invalidItems : continue
			if not hasattr( pyItem.itemInfo.baseItem, "getID" ) : continue
			if pyItem.itemInfo.baseItem.getID() == skillID :
				self.__invalidItems.append( pyItem )
				toolbox.itemCover.showInvalidItemCover( pyItem )
		self.__cancelCoverCBID = BigWorld.callback( 1, self.__hideInvalidItemCovers )		# 标记在1秒后自动隐藏
	
	def __onEnterSpaceCopy( self, skills, spaceType ):
		if spaceType == csdefine.SPACE_TYPE_CHALLENGE and not self.__isFirstEnterChallenge:
			player = BigWorld.player()
			avatarType = player.avatarType
			if avatarType == "":return
			challengeAutoSkillsLoader = ChallengeAutoSkillsLoader.instance()
			autoSkInfos = challengeAutoSkillsLoader.getSkInfos( avatarType )
			self.__isFirstEnterChallenge = True
			for index, autoSkInfo in enumerate( autoSkInfos ):
				spaceSkill = self.__getSpaceSkill( autoSkInfo, skills )
				if spaceSkill == 0:continue
				gbIndex = csdefine.QB_AUTO_SPELL_INDEX + index
				pyItem = self.__pyItems.get( gbIndex, None )
				if pyItem is None:continue
				skill = Skills.getSkill( spaceSkill )
				skillInfo = SkillItem( skill )
				self.__onUpdateItem( gbIndex, skillInfo )
	
	def __getSpaceSkill( self, autoSkInfo, skills ):
		"""
		获取副本技能
		"""
		for spaceSkill in skills:
			if autoSkInfo[0] == spaceSkill/1000:
				return spaceSkill
		return 0
		
	def __onLeaveSpaceCopy( self ):
		"""
		离开副本
		"""
		player = BigWorld.player()
		spaceType = player.getCurrentSpaceType()
		itemInfos = player.qb_getItems()
		self.__isFirstEnterChallenge = False
		player.setAutoSkillIDList()
		for pyItem in self.__pyItems.values() :			# 切换姿态的时候需要保留空间技能
			gbIndex = pyItem.gbIndex
			itemInfo = itemInfos.get( gbIndex, None )
			self.__onUpdateItem( gbIndex, itemInfo )
			pyItem.updateIconState()
			
	def __hideInvalidItemCovers( self ) :
		"""
		隐藏不可用技能的红色边框
		"""
		for pyItem in self.__invalidItems :
			toolbox.itemCover.hideItemCover( pyItem )
		self.__invalidItems = []

	# -------------------------------------------------
	def __onUpdateItem( self, gbIndex, itemInfo ) :
		player = BigWorld.player()
		if self.__pyItems.has_key( gbIndex ):
			pyItem = self.__pyItems[gbIndex]
			pyItem.update( itemInfo )
			pyItem.updateIconState()
			if itemInfo is None:
				index = gbIndex - csdefine.QB_AUTO_SPELL_INDEX
				description = ""
				if index in range(5):
					description = labelGather.getText( "quickbar:afBar", "tipsSkillItem" )
				elif index == 5:
					description = labelGather.getText( "quickbar:afBar", "tipsHPItem" )
				else:
					description = labelGather.getText( "quickbar:afBar", "tipsMPItem" )
				pyItem.description = description
			autoSkIndexs = [csdefine.QB_AUTO_SPELL_INDEX + i for i in xrange( 5 )]
			if gbIndex in autoSkIndexs: #技能列表
				index = autoSkIndexs.index( gbIndex )
				autoSkIDs = []
				if itemInfo is None:
					self.autoSkIDs[index] = -1
				else:
					self.autoSkIDs[index] = itemInfo.baseItem.getID()
				for skID in self.autoSkIDs:
					if skID == -1:continue
					autoSkIDs.append( skID )
				player.setAutoSkillIDList( autoSkIDs )
			elif gbIndex == csdefine.QB_AUTO_SPELL_INDEX + 5: #角色自动回血栏
				player.qb_setRecordRedMedication( itemInfo )
			elif gbIndex == csdefine.QB_AUTO_SPELL_INDEX + 6:
				player.qb_setRecordBlueMedication( itemInfo ) #角色自动回蓝栏

	def __onShowSetting( self ):
		"""
		"""
		AutoFightWindow.instance().toggleAuotFightWindow()


	def __onStart( self ):
		"""
		"""
		self.__pyOpenBtn.visible = False
		self.__pyCloseBtn.visible = True
		BigWorld.player().toggleAutoFight()


	def __onClose( self ):
		"""
		"""
		self.__pyOpenBtn.visible = True
		self.__pyCloseBtn.visible = False
		BigWorld.player().toggleAutoFight()

	def __stopAutoFight( self ):
		"""
		"""
		self.__pyOpenBtn.visible = True
		self.__pyCloseBtn.visible = False

	def __startAutoFight( self ):
		"""
		"""
		self.__pyOpenBtn.visible = False
		self.__pyCloseBtn.visible = True

	def __onShowFightBar( self ):
		ECenter.fireEvent( "EVT_ON_AUTO_FIGHT_BAR_SHOW" )

	def __onHideFightBar( self ):
		ECenter.fireEvent( "EVT_ON_AUTO_FIGHT_BAR_HIDE" )

	def __onBarMouseDown( self ) :
		"""
		鼠标点击则浮动框消失
		"""
		toolbox.infoTip.hide()

	def __onBarMouseEnter( self, pyItem ) :
		"""
		鼠标进入则浮动框出现
		"""
		toolbox.infoTip.showItemTips( self, pyItem.description )

	def __onBarMouseLeave( self ) :
		"""
		鼠标离开则浮动框消失
		"""
		toolbox.infoTip.hide()
	
	def __onBtnMouseEnter( self, pyBtn ):
		"""
		鼠标进入出现提示框
		"""
		tips = labelGather.getText( "quickbar:afBar", "tipsOpenBtn" )
		toolbox.infoTip.showItemTips( self, tips )
	
	def __onBtnMouseLeave( self ):
		"""
		鼠标离开隐藏提示框
		"""
		toolbox.infoTip.hide()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		self.visible = False
		self.__onHideSpellingCover()
		self.__isFirstEnterChallenge = False
		for index, pyItem in self.__pyItems.iteritems() :
			pyItem.gbIndex = index
			self.__onUpdateItem( index, None )

	def onEnterWorld( self ) :
		self.__pyOpenBtn.visible = True
		self.__pyCloseBtn.visible = False
		
	def updateIconState( self ):
		"""
		更新格子图标颜色
		"""
		for pyItem in self.__pyItems.itervalues():
			if pyItem and pyItem.itemInfo:
				pyItem.updateIconState()
	# ----------------------------------------------------------------
	# property
	# ----------------------------------------------------------------
	def _setVisible( self, visible ) :
		PyGUI._setVisible( self, visible )
		if visible :
			self.__onShowFightBar()
		else :
			self.__onHideFightBar()

	# -------------------------------------------------
	visible = property( PyGUI._getVisible, _setVisible )					# 重写visible属性

import Language
class ChallengeAutoSkillsLoader:
	
	__sk_config_path = "config/client/ChallengeSpaceAutoSkills.xml"
	_instance = None
	
	def __init__( self ):
		# 不允许有2个或2个以上实例
		assert ChallengeAutoSkillsLoader._instance is None
		self._datas = {}
		ChallengeAutoSkillsLoader._instance = self
		self.load( self.__sk_config_path )
		
	def load( self, configPath ):
		self._datas = {}
		section = Language.openConfigSection( configPath )
		if section is None:return
		for node in section.values():
			avatarType = node.readString( "avatarType" )
			index = node.readInt( "index" )
			skillID = node.readInt64( "skillID" )
			skillInfo = ( skillID, index )
			if self._datas.has_key( avatarType ):
				self._datas[avatarType].append( skillInfo )
			else:
				self._datas[avatarType] = [skillInfo]
		# 清除缓冲
		Language.purgeConfig( self.__sk_config_path )

	def getSkInfos( self, avatarType ):
		"""
		根据npc编号取得对应的技能ID表
		"""
		try:
			skInfos = self._datas[avatarType]
			skInfos.sort( key = lambda skInfo: skInfo[1] )
			return skInfos
		except KeyError:
			return []
	
	@staticmethod
	def instance():
		"""
		"""
		if ChallengeAutoSkillsLoader._instance is None:
			ChallengeAutoSkillsLoader._instance = ChallengeAutoSkillsLoader()
		return ChallengeAutoSkillsLoader._instance
