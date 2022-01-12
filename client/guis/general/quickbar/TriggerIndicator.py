# -*- coding: gb18030 -*-

import csstatus
from bwdebug import ERROR_MSG
from guis import *
import skills
import event.EventCenter as ECenter
from guis import uiFixer
from guis.controls.Item import Item
from guis.controls.StaticText import StaticText
from guis.common.RootGUI import RootGUI
from guis.tooluis.CSRichText import CSRichText
from guis.otheruis.AnimatedGUI import AnimatedGUI
from guis.general.quickbar.SKItemDetector import SKIDetector
from QBItem import QBItem
import GUIFacade
import skills as Skill
from ItemsFactory import SkillItem
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from config.skill.Skill.SkillDataMgr import Datas as SKILL_DATA


class TriggerIndicator( RootGUI ) :

	def __init__( self, gui ) :
		RootGUI.__init__( self, gui )
		self.focus = False
		self.movable_ = False										# 不可移动
		self.escHide_ = False										# 不可按esc键关闭
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "BOTTOM"
		self.__holdCBID = 0
		self.addToMgr()
		self.__initialize( gui )

		self.__pyItem = TriggerItem( gui.item, self )
		self.__ptSkID = 0		#母技能id
		self.__skID = 0			#自身技能id
		self.__triggers = {}
		self.__registerTriggers()

	def __initialize( self, gui ):
		self.__fader = GUI.AlphaShader()
		self.__fader.speed = 0.3
		self.__fader.value = 1.0
		self.__fader.reset()
		gui.addShader( self.__fader )
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_BEGIN_COOLDOWN"] = self.__beginCooldown

		for trigger in self.__triggers.iterkeys() :
			ECenter.registerEvent( trigger, self )

	def __deregisterTriggers( self ) :
		for trigger in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( self, trigger )

	# --------------------------------------------------------------
	def __beginCooldown( self, cooldownType, lastTime ) :
		self.__pyItem.beginCooldown( cooldownType, lastTime )

	def __getLastTime( self ):
		skillInfo = self.__pyItem.itemInfo
		if skillInfo is None:return
		timeStr = SKILL_DATA.__getitem__(self.__skID)["param4"]
		if timeStr == "":return
		return int( timeStr )

	def __getCoolDownTime( self ):
		maxCDTime = 0
		itemInfo = self.__pyItem.itemInfo
		if itemInfo is None:return maxCDTime
		skill = itemInfo.baseItem
		if hasattr( skill , "getLimitCooldown" ):										# 冷却时间
			for cd in skill.getLimitCooldown():
				for cdData in skill.getSpringOnUsedCD():
					if cdData[ "CDID" ] == cd:
						if cdData[ "CDTime" ] > maxCDTime:
							maxCDTime  = cdData[ "CDTime" ]
				for cdData in skill.getSpringOnIntonateOverCD():
					if cdData[ "CDID" ] == cd:
						if cdData[ "CDTime" ] > maxCDTime:
								maxCDTime  = cdData[ "CDTime" ]
		return maxCDTime

	def __endHolding( self ) :
		self.__fader.value = 0
		BigWorld.callback( self.__fader.speed, self.dispose )

	def __del__( self ) :
		if Debug.output_del_RollBox :
			INFO_MSG( str( self ) )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def dispose( self ) :
		"""
		销毁
		"""
		BigWorld.cancelCallback( self.__holdCBID )
		self.__holdCBID = 0
		self.__pyItem.dispose()
		RootGUI.dispose( self )
		ECenter.fireEvent( "EVT_ON_TRIGGERS_REMOVE_SUBSKILL", self.__ptSkID, self.__skID )
		self.__ptSkID = 0

	def update( self, itemInfo ):
		"""
		更新技能信息
		"""
		self.__pyItem.update( itemInfo )

	def isMouseHit( self ) :
		return self.__pyItem.isMouseHit()

	def onLeaveWorld( self ):
		"""
		"""
		self.dispose()

	def show( self ):
		lastTime = self.__getLastTime() - self.__fader.speed
		self.__holdCBID = BigWorld.callback( lastTime, self.__endHolding )
		RootGUI.show( self )

	def delayHide( self ):
		self.__endHolding()

	def triggerShow( self ):

		BigWorld.callback( self.__fader.speed, self.show )
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	def _getPtSkID( self ) :
		return self.__ptSkID

	def _setPtSkID( self, skID ) :
		self.__ptSkID = skID

	def _getSkID( self ):
		return self.__skID

	def _setSkID( self, skID ):
		self.__skID = skID

	ptSkID = property( _getPtSkID, _setPtSkID )
	skID = property( _getSkID, _setSkID )

# --------------------------------------------------------------------------

class TriggerItem( QBItem ) :

	def __init__( self, item, pyBinder ) :
		QBItem.__init__( self, item, pyBinder )
		self.focus = True
		self.crossFocus = True
		self.dragFocus = False
		self.dropFocus = False

		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False

	# ----------------------------------------------------------------
	# protected
	# ----------------------------------------------------------------
	def onRClick_( self, mods ) :
		QBItem.onRClick_( self, mods )
		return True

	def onLClick_( self, mods ) :
		QBItem.onLClick_( self, mods )
		return True

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def beginCooldown( self, cooldownType, lastTime ) :
		"""
		进入冷却状态
		"""
		if self.itemInfo is None : return
		if self.itemInfo.isCooldownType( cooldownType ) :
			cdInfo = self.itemInfo.getCooldownInfo()
			self.__pyCDCover.unfreeze( *cdInfo )

	def update( self, itemInfo ) :
		"""
		更新
		"""
		SKIDetector.unbindPyItem( self )						# 将探测器中的旧数据清空
		QBItem.update( self, itemInfo )
		if itemInfo is None :return
		spell = itemInfo.getSpell()
		if spell is None : return
		player = BigWorld.player()
		rangeMax = spell.getRangeMax( player )
		rangeMin = spell.getRangeMin( player )
		if rangeMax > 0.0 :
			SKIDetector.bindPyItem( self, ( "COM", rangeMax ) )	# 添加到探测器
		if rangeMin > 0.0 :
			SKIDetector.bindPyItem( self, ( "COM", rangeMin ) )	# 添加到探测器

# ---------------------------------------------------------------------------------

class TrigIntorMgr:

	__cc_max_rows 	= 3 				#最多显示3个
	__cc_spacing	= 1.0				#之间间隔
	__cc_v_site		= 0.73				#垂直方向的显示位置（目前设为屏幕 7/10 位置处

	def __init__( self ):
		self.__pyTriIntors = {}		#子技能列表 {母技能id：[子技能1，子技能2...]}
		self.__triggers = {}
		self.__registerTriggers()

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SKILL_TRIGGER_SPELL"] 		= self.__onTrigger
		self.__triggers["EVT_ON_TRIGGERS_REMOVE_SUBSKILL"]	= self.__onRemoveSubSkill

		for key in self.__triggers :
			GUIFacade.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )

	# -------------------------------------------------------------
	def __onTrigger( self, ptSkID, skID ):
		"""
		触发显示
		"""
		if skID != 0: #触发了子技能
			gui = GUI.load( "guis/general/quickbar/tricator.gui" )
			uiFixer.firstLoadFix( gui )
			pyTrigIntor = TriggerIndicator( gui )
			skill = Skill.getSkill( skID )
			skillInfo = SkillItem( skill )
			pyTrigIntor.update( skillInfo )
			pyTrigIntor.ptSkID = ptSkID
			pyTrigIntor.skID = skID
			trigIntors = []
			if self.__pyTriIntors.has_key( ptSkID ):
				trigIntors = self.__pyTriIntors[ptSkID]
				if self.__isInTrigsList( pyTrigIntor, trigIntors ):return
				trigIntors.append( pyTrigIntor )
			else:
				trigIntors.append( pyTrigIntor )
				self.__pyTriIntors[ptSkID] = trigIntors
			self.__layoutIntors( ptSkID, pyTrigIntor )
		else: #触发结束
			pass


	def __isInTrigsList( self, pyTrigIntor, trigIntors ):
		if pyTrigIntor is None:return
		skID = pyTrigIntor.skID
		trigsList = [pyIntor.skID for pyIntor in trigIntors]
		return skID in trigsList

	def __onRemoveSubSkill( self, ptSkID, skID ):
		trigIntors = self.__pyTriIntors.get( ptSkID )
		if trigIntors is None:return
		for trigIntor in trigIntors:
			if trigIntor.skID == skID:
				trigIntors.remove( trigIntor )
		if len( trigIntors ) <= 0:
			self.__pyTriIntors.pop( ptSkID )

	def __layoutIntors( self, ptSkID, pyTrigIntor ):
		"""
		设置技能格位置
		"""
		trigIntors = self.__pyTriIntors.get( ptSkID )
		lowIndex = len( self.__pyTriIntors ) - 1 #列索引
		rowIndex = len( trigIntors ) - 1		 #行索引
		st_left = BigWorld.screenWidth() * 0.5 + 80
		st_top = BigWorld.screenHeight() * 0.5 + 50
		pyTrigIntor.left = st_left + lowIndex*45
		pyTrigIntor.top = st_top + rowIndex*45
		pyTrigIntor.triggerShow()

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ) :
		for pyRollBox in self.__pyRollBoxs:
			pyRollBox.onLeaveWorld()
