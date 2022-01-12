# -*- coding: gb18030 -*-
#
# $Id: GemDrawPanel.py, fangpengjun Exp $
#
from guis import *
from LabelGather import labelGather
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabButton
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.controls.ListPanel import ListPanel
from guis.common.PyGUI import PyGUI
import csconst
import csdefine
import time
common_amount = 8
ROLE_TYPE = 1
PET_TYPE = 2
NONE_TYPE = -1
comonTypes = { ROLE_TYPE: "guis/general/playerprowindow/gempanel/rolecommon.gui", #玩家和宠物宝石
		PET_TYPE: "guis/general/playerprowindow/gempanel/petcommon.gui"
			}
class GemDrawPanel( TabPanel ): #宝石领取
	def __init__( self, tabPanel ):
		TabPanel.__init__( self, tabPanel )
		self.__triggers = {}
		self.__activeGems = []
		self.__commonGems = {}
		self.__registerTriggers()
		self.sortByNameFlag = False
		self.sortByTimeFlag = False
		self.__initPanel( tabPanel )

	def __initPanel( self, tabPanel ):
		self.__pyGemsPanel = ListPanel( tabPanel.gemsPanel.listPanel, tabPanel.gemsPanel.scrollBar ) #可领取的宝石列表
		self.__pyGemsPanel.onItemSelectChanged.bind( self.__onPetItemSelectedChanged )
		self.__pyGemsPanel.autoSelect = True

		self.__pyRefurbishBtn = Button( tabPanel.refurbishBtn ) # 刷新宝石列表
		self.__pyRefurbishBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyRefurbishBtn.onLClick.bind( self.__onRefurshGems )

		self.__pyDrawBtn = Button( tabPanel.drawBtn ) #领取宝石
		self.__pyDrawBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyDrawBtn.onLClick.bind( self.__onDawGem )

		self.__pyNameBtn = Button( tabPanel.nameBtn ) #按宝石玩家名字排序
		self.__pyNameBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyNameBtn.onLClick.bind( self.__onSortByName )

		self.__pyReTimeBtn = Button( tabPanel.reTimeBtn ) #按剩余时间排序
		self.__pyReTimeBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyReTimeBtn.onLClick.bind( self.__onSortByRemianTime )

		self.__initActiveGems( tabPanel.holdPanel )

	def __initActiveGems( self, activePanel ):
		self.__activeItems = {}
		for name, item in activePanel.children:
			if "activeItem_" not in name:continue
			index = int( name.split( "_" )[1] )
			pyItem = ActiveItem( item )
			pyItem.active = False
			self.__activeItems[index] = pyItem

	def __registerTriggers( self ):
		self.__triggers["EVT_ON_LOAD_ROLE_GEM"] = self.__onLoadRoleGem #领取玩家经验石
		self.__triggers["EVT_ON_OFFLOAD_ROLE_GEM"] = self.__onOffloadRoleGem #取消玩家经验石
		self.__triggers["EVT_ON_LOAD_PET_GEM"] = self.__onLoadPetGem #领取宠物经验石
		self.__triggers["EVT_ON_OFFLOAD_PET_GEM"] = self.__onOffloadPetGem #取消宠物经验石
#		self.__triggers["EVT_ON_COMMON_GEM_LIMILTED"] = self.__onGemLimitChange #更新宝石剩余时间
		self.__triggers["EVT_ON_ROLE_DEAD"] = self.__offloadActiveGems # 死亡后卸下所有领取的宝石
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def deregisterTriggers_( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# ----------------------------------------------------------------
	def __offloadActiveGems( self ) :
		for pyActItem in self.__activeItems.itervalues() :
			pyActItem.offload()

	def __onLoadRoleGem( self, index ):#领取玩家宝石
		roleGem = BigWorld.player().gem_getcomGemByIndex( index )
		if roleGem is None:return
		limitTime = 0
		if self.__commonGems.has_key( index ):
			pyCommonGem = self.__commonGems[index]
			limitTime = pyCommonGem.time*3600 + time.time()
		activeGem = ActiveGem( roleGem, ROLE_TYPE, limitTime )
		for pyActiveGem in self.__activeItems.itervalues():
			if not pyActiveGem.active:
				pyActiveGem.update( activeGem )
				self.__activeGems.append( activeGem )
				break
		self.__addActiveGem( index, ROLE_TYPE )

	def __onOffloadRoleGem( self, index ): #卸掉一个宝石
		for activeGem in self.__activeGems:
			if activeGem.index == index:
				self.__activeGems.remove( activeGem )
				self.__resetActiveGes( )

	def __onLoadPetGem( self, index ):
		petGems = BigWorld.player().ptn_getCommonGems()
		def getPetGem( index ):
			for petGem in petGems:
				if petGem.index == index:
					return petGem
		petGem = getPetGem( index )
		if petGem is None:return
		limitTime = 0
		if self.__commonGems.has_key( index ):
			pyCommonGem = self.__commonGems[index]
			limitTime = pyCommonGem.time*3600 + time.time()
		activeGem = ActiveGem( petGem, PET_TYPE, limitTime )
		for pyActiveGem in self.__activeItems.itervalues():
			if not pyActiveGem.active:
				pyActiveGem.update( activeGem )
				self.__activeGems.append( activeGem )
				break
		self.__addActiveGem( index, PET_TYPE )

	def __onOffloadPetGem( self, index ):
		for activeGem in self.__activeGems:
			if activeGem.index == index:
				self.__activeGems.remove( activeGem )
				self.__resetActiveGes( )

	def __addActiveGem( self, index, gemType ):
		if self.__commonGems.has_key( index ):
			pyCommonGem = self.__commonGems.pop( index )
			self.__pyGemsPanel.removeItem( pyCommonGem )
		activeIndexs = [activeGem.index for activeGem in self.__activeGems]
		commonIndexs = [commonGem.index for commonGem in self.__commonGems.itervalues()]
		commonIndexs.extend( activeIndexs )
		if gemType == ROLE_TYPE: #玩家宝石
			for newIndex in xrange( csdefine.GEM_ROLE_COMMON_INDEX, csdefine.GEM_PET_COMMON_INDEX ):
				if newIndex in commonIndexs: continue
				self.__resetCommonGems( gemType, newIndex )
				break
		else: #宠物宝石
			for newIndex in xrange( csdefine.GEM_PET_COMMON_INDEX, csdefine.GEM_PET_COMMON_INDEX + csconst.GEM_PET_COMMON_COUNT_UPPER ):
				if newIndex in commonIndexs: continue
				self.__resetCommonGems( gemType, newIndex )
				break
		if len( self.__pyGemsPanel.pyItems ) >= common_amount:
			return

	def __resetActiveGes( self ):
		for pyActiveGem in self.__activeItems.itervalues():
			pyActiveGem.update( None )
		for index, activeGem in enumerate ( self.__activeGems ):
			if self.__activeItems.has_key( index ):
				self.__activeItems[index].update( activeGem )

	def __onPetItemSelectedChanged( self, pyItem ):
		self.__pyDrawBtn.enable = pyItem is not None

	def __onRefurshGems( self ): #刷新列表,纯客户端
		self.__pyGemsPanel.clearItems()
		self.__commonGems = {}
		activeIndexs = [activeGem.index for activeGem in self.__activeGems]
		for index in xrange( common_amount ):
			commonIndexs = [commonGem.index for commonGem in self.__commonGems.itervalues()]
			commonIndexs.extend( activeIndexs )
			type = random.choice( comonTypes.keys() )
			if type == ROLE_TYPE: #玩家宝石
				for newIndex in xrange( csdefine.GEM_ROLE_COMMON_INDEX, csdefine.GEM_PET_COMMON_INDEX ):
					if newIndex in commonIndexs: continue
					self.__resetCommonGems( type, newIndex )
					break
			else: #宠物宝石
				for newIndex in xrange( csdefine.GEM_PET_COMMON_INDEX, csdefine.GEM_PET_COMMON_INDEX + csconst.GEM_PET_COMMON_COUNT_UPPER ):
					if newIndex in commonIndexs: continue
					self.__resetCommonGems( type, newIndex )
					break

	def __resetCommonGems( self, type, newIndex ):
		gemGui = GUI.load( comonTypes[type] )
		uiFixer.firstLoadFix( gemGui )
		pyGemItem = GemItem( gemGui )
		pyGemItem.type = type
		pyGemItem.focus = True
		pyGemItem.selectable = True
		pyGemItem.index = newIndex
		self.__commonGems[newIndex] = pyGemItem
		self.__pyGemsPanel.addItem( pyGemItem )

	def __onDawGem( self ):
		pyGemItem = self.__pyGemsPanel.pySelItem
		if pyGemItem is None:return
		if pyGemItem.index in [activeGem.index for activeGem in self.__activeGems]:
			return
		type = pyGemItem.type
		if type == ROLE_TYPE: #玩家经验石
			BigWorld.player().gem_hire( pyGemItem.index, pyGemItem.time*3600 )
		elif type == PET_TYPE:
			BigWorld.player().ptn_activeCommonGem( pyGemItem.index, pyGemItem.time*3600 )

	def __onSortByName( self ): #按人名排序
		flag = self.sortByNameFlag and True or False
		self.__pyGemsPanel.sort( key = lambda n: n.name, reverse = flag )
		self.sortByNameFlag = not self.sortByNameFlag

	def __onSortByRemianTime( self ): #按剩余时间排序
		flag = self.sortByNameFlag and True or False
		self.__pyGemsPanel.sort( key = lambda n: n.time, reverse = flag )
		self.sortByNameFlag = not self.sortByNameFlag

	# ------------------------------------------------------------
	# public
	# ------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def addPetGems( self ):#初始化待领取宝石列表,纯客户端
		self.__pyGemsPanel.clearItems()
		for index in xrange( common_amount ):
			type = random.choice( comonTypes.keys() )
			gemGui = GUI.load( comonTypes[type] )
			uiFixer.firstLoadFix( gemGui )
			pyGemItem = GemItem( gemGui )
			if type == ROLE_TYPE: #玩家宝石
				pyGemItem.index = random.randint( csdefine.GEM_ROLE_COMMON_INDEX, csdefine.GEM_PET_COMMON_INDEX )
			else:
				pyGemItem.index = random.randint( csdefine.GEM_PET_COMMON_INDEX, csdefine.GEM_PET_COMMON_INDEX + csconst.GEM_PET_COMMON_COUNT_UPPER )
			pyGemItem.type = type
#			pyGemItem.focus = True
#			pyGemItem.selectable = True
			self.__commonGems[pyGemItem.index] = pyGemItem
			self.__pyGemsPanel.addItem( pyGemItem )

	def clearGems( self ):
		self.__pyGemsPanel.clearItems()

	def reset( self ):
		self.clearGems()
		self.__activeGems = []
		self.__commonGems = {}
		for pyActiveGem in self.__activeItems.itervalues():
			pyActiveGem.update( None )
# -------------------------------------------------------
# 已领取宝石类
# -------------------------------------------------------
from guis.controls.Control import Control
from guis.controls.Icon import Icon
import Timer
from Time import Time
class ActiveItem( Control ):
	def __init__( self, item ):
		Control.__init__( self, item )
		self.__index = -1
		self.__gemIndex = -1
		self.__pyStRemain = StaticText( item.stTime )
		self.__pyStRemain.text = ""
		self.limitTimerID = 0
		self.__limitTime = 0

		self.__pyStopBtn =Button( item.stopBtn )
		self.__pyStopBtn.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyStopBtn.onLClick.bind( self.__onPauseActive )

		self.__pyGemIcon = Icon( item.gemIcon )
		self.__activeGem = None
		self.__active = False
		self.__type = -1

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def onStateChanged_( self, state ):
		pass

	def onMouseEnter_( self ):
		Control.onMouseEnter_( self )
		return True

	def onMouseLeave_( self ):
		Control.onMouseLeave_( self )
		return True

	def __onPauseActive( self ):
		if self.__activeGem is None:return
		if self.type == ROLE_TYPE:
			BigWorld.player().cell.gem_endHire( self.activeGem.index )
		elif self.type == PET_TYPE:
			BigWorld.player().ptn_inactiveCommonGem( self.activeGem.index )

	def __limitTimeUpdate( self ):
		if not self.active:
			self.__cancelLimitTimer()
			return
		remainTime = self.__limitTime - time.time()
		hours = remainTime/3600
		mins = ( remainTime%3600 )/60
		secs = ( remainTime%3600 )%60
		if hours > 0:
			self.__pyStRemain.text = labelGather.getText( "PlayerProperty:GemPanel", "remainTime" )%( hours, mins )
		else:
			self.__pyStRemain.text = labelGather.getText( "PlayerProperty:GemPanel", "remainMins" )%( mins, secs )
#		if remainTime <= 0:
#			self.__cancelLimitTimer()
#			self.update( None, 0, 0 )

	def __cancelLimitTimer( self ): #清除计时器
		Timer.cancel( self.limitTimerID )
		self.limitTimerID = 0

	def update( self, activeGem ):
		if activeGem is None :
			self.active = False
			self.index = -1
			self.__type = -1
			self.__cancelLimitTimer()
		else:
			self.activeGem = activeGem
			self.index = activeGem.index
			self.active = True
			self.__type = activeGem.type
			self.limitTimerID = Timer.addTimer( 0, 10, self.__limitTimeUpdate )
			self.__limitTime = activeGem.limitTime
			mapping = ((0.000000, 0.000000), (0.000000, 0.937500), (1.000000, 0.937500),(1.000000, 0.000000))
			if activeGem.type == ROLE_TYPE:
				self.__pyGemIcon.icon = ( "guis/general/playerprowindow/gempanel/roleicon.tga", mapping )
			elif activeGem.type == PET_TYPE:
				self.__pyGemIcon.icon = ( "guis/general/playerprowindow/gempanel/peticon.tga", mapping )

	def offload( self ) :
		self.__onPauseActive()


	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getIndex( self ):
		return self.__index

	def _setIndex( self, index ):
		self.__index = index

	def _getActiveGem( self ):
		return self.__activeGem

	def _setActiveGem( self, activeGem ):
		self.__activeGem = activeGem

	def _getActive( self ):
		return self.__active

	def _setActive( self ,active ):
		self.visible = active
		self.__active = active

	def _getType( self ):
		return self.__type

	def _setType( self, type ):
		self.__type = type

	def _getLimitTime( self ):
		return self.__limitTime

	def _setLimitTime( self, limitTime ):
		self.__limitTime = limitTime
	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
#	remain = property( _getRemian, _setRemain )
	index = property( _getIndex, _setIndex )
	activeGem = property( _getActiveGem, _setActiveGem )
	active = property( _getActive, _setActive )
	type = property( _getType, _setType )
	limitTime = property( _getLimitTime, _setLimitTime )

# --------------------------------------------------
# #待领取宝石类
# --------------------------------------------------
from guis.controls.ListItem import MultiColListItem
import random
class GemItem( MultiColListItem ):
	def __init__( self, item ):
		MultiColListItem.__init__( self, item )
		self.__index = -1
		self.__type = -1
		name = labelGather.getText( "PlayerProperty:GemPanel", "csPlayer" )
		time = random.randint( 3, 24 )
		timeText = labelGather.getText( "PlayerProperty:GemPanel", "timeHours" )%time
		self.__time = time
		self.setTextes( name, timeText )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def onMouseEnter_( self ):
		MultiColListItem.onMouseEnter_( self )
		self.highlightBackColor = 0,255,255,255
		return True

	def onMouseLeave_( self ):
		MultiColListItem.onMouseLeave_( self )
		self.commonBackColor = 255,255,255,255
		return True

	def onLMouseDown_( self, mods ):
		MultiColListItem.onLMouseDown_( self, mods )
		return True

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------

	def _getName( self ):
		return self._getCols()[0].text

	def _setName( self, name ):
		self._getCols()[0].text = name

	# ----------------------------------------------
	def _getTime( self ):
		return self.__time

	def _setTime( self, time ):
		self.__time = time

	def _getIndex( self ):
		return self.__index

	def _setIndex( self, index ):
		self.__index = index

	def _getType( self ):
		return self.__type

	def _setType( self, type ):
		self.__type = type

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	name = property( _getName, _setName )
	time = property( _getTime, _setTime )
	index = property( _getIndex, _setIndex )
	type = property( _getType, _setType )

# -----------------------------------------------------
# 封装经验石
# -----------------------------------------------------
class ActiveGem:
	def __init__( self, activeGem, type, limitTime ):
		self.activeGem = activeGem
		self.type = type
		self.index = activeGem.index
		self.limitTime = limitTime
