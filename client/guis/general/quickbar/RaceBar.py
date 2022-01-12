# -*- coding: gb18030 -*-
#
# $Id: OperationBar.py,v 1.15 2008-08-26 02:17:14 huangyongwei Exp $
from guis import *
from guis.common.PyGUI import PyGUI
from guis.common.FrameEx import HFrameEx
from guis.common.RootGUI import RootGUI
from guis.controls.StaticText import StaticText
from LabelGather import labelGather
import csdefine
import Timer

#赛马和特战凤栖镇共用技能栏
class RaceBar( HFrameEx ):
	
	_cc_race_num = 3
	_cc_fengqi_num = 2
	
	def __init__( self, bar, pyBinder = None ):
		HFrameEx.__init__( self, bar )
		self.moveFocus = False
		self.focus = True
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyItems = {}
		self.pyBinder = pyBinder
		self.__initialize( bar )

	def __initialize( self, bar ):
		pass

	# -------------------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_ROLE_RACEHORSE_START"] = self.__onHorseRaceStart #开始赛马
		self.__triggers["EVT_ON_ROLE_RACEHORSE_END"] = self.__onRaceEnd #结束赛马
		self.__triggers["EVT_ON_FENGQI_ON_ENTER"] = self.__onEnterFengQi #进入夜战凤栖
		self.__triggers["EVT_ON_FENGQI_ON_EXIT"] = self.__onExitFengQi #离开夜战凤栖
		self.__triggers["EVT_ON_RACEBAG_ADD_ITEM"] = self.__onAddItem #增加道具
		self.__triggers["EVT_ON_RACEBAG_REMOVE_ITEM"] = self.__onRemoveItem #删除道具
		self.__triggers["EVT_ON_RACEBAG_SWAP_ITEMS"] = self.__onRaceSwapItems #交换物品栏道具
		for key in self.__triggers.iterkeys() :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( key, self )

	# --------------------------------------------------
	def __onHorseRaceStart( self ):
		self.__layoutItems( self._cc_race_num )
		self.pyBinder.autoFightBar.visible = False
		self.visible = True

	def __onRaceEnd( self ):
		if self.pyBinder.autoBarShow:
			self.pyBinder.autoFightBar.visible = True
		for index in self.__pyItems.keys():
			pyItem = self.__pyItems.pop( index )
			self.delPyChild( pyItem )
		self.visible = False

	def __onAddItem( self, index, itemInfo ):
		if self.__pyItems.has_key( index ):
			pyItem = self.__pyItems[index]
			pyItem.update( itemInfo )
	
	def __onEnterFengQi( self, role ):
		self.__layoutItems( self._cc_fengqi_num )
		self.pyBinder.autoFightBar.visible = False
		self.visible = True
	
	def __onExitFengQi( self, role ):
		self.__onRaceEnd()

	def __onRemoveItem( self, index ):
		if self.__pyItems.has_key( index ):
			pyItem = self.__pyItems[index]
			pyItem.update( None )

	def __onRaceSwapItems( self, srcOrder, srcItemInfo, dstOrder, dstItemInfo ):
		srcItem = self.__pyItems[srcOrder]
		dstItem = self.__pyItems[dstOrder]
		srcItem.update( dstItemInfo )
		dstItem.update( srcItemInfo )
	
	def __layoutItems( self, num ):
		"""
		排序技能格
		"""
		offset = 48.0
		for index in range( num ):
			item = GUI.load( "guis/general/quickbar/racebag/item.gui" )
			uiFixer.firstLoadFix( item )
			pyRaceItem = RaceItem( item )
			self.addPyChild( pyRaceItem, "item_%d"%index )
			pos = offset + index*40.0, 14.0
			pyRaceItem.pos = pos
			gbIndex = index+1
			pyRaceItem.gbIndex = gbIndex
			self.__pyItems[gbIndex] = pyRaceItem
		self.width = offset + num*40.0 + 18.0

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		for pyItem in self.__pyItems.itervalues():
			pyItem.update( None )

	def onRoleEnterWorld( self ):
		pass

# ---------------------------------------------------
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.controls.CircleCDCover import CircleCDCover as CDCover
from guis.otheruis.AnimatedGUI import AnimatedGUI
import csdefine


class RaceItem( PyGUI ):
	def __init__( self, item ):
		PyGUI.__init__( self, item )
		self.__pyItem = Item( item.item )
	
	def update( self, itemInfo ):
		self.__pyItem.update( itemInfo )

	def _getGBIndex( self ) :
		return self.__pyItem.gbIndex

	def _setGBIndex( self, index ) :
		self.__pyItem.gbIndex = index

	def _getItemInfo( self ):
		return self.__pyItem.itemInfo

	gbIndex = property( _getGBIndex, _setGBIndex )
	itemInfo = property( _getItemInfo )

class Item( BOItem ):
	def __init__( self, item ):
		BOItem.__init__( self, item )
		self.__gbIndex = 0
		self.focus = True
		self.crossFocus = True
		self.dragFocus = True
		self.dropFocus = True
		self.selectable = True
		self.dragMark = DragMark.RACE_BAG

		self.__pyCDCover = CDCover( item.circleCover, self )
		self.__pyCDCover.crossFocus = False

		self.__pyOverCover = AnimatedGUI( item.overCover )
		self.__pyOverCover.initAnimation( 1, 8, ( 2, 4 ) )					# 动画播放一次，共8帧
		self.__pyOverCover.cycle = 0.4										# 循环播放一次的持续时间，单位：秒
		self.__pyCDCover.onUnfreezed.bind( self.__pyOverCover.playAnimation )
		self.__dropEvents = {}
		self.__triggers = {}
		self.__registerTriggers()
		if item is None:return
		self.__dropEvents[DragMark.RACE_BAG] = DropHandlers.fromRaceBag 		# 只能本包裹交换

	def dispose( self ):
		self.__pyCDCover.dispose()
		self.__deregisterTriggers()
		BOItem.dispose( self )

	def onMouseEnter_( self ):
		self.onDescriptionShow_()
		toolbox.itemCover.highlightItem( self )
		return True

	def onMouseLeave_( self ):
		BOItem.onMouseLeave_( self )
		return True

	def onDescriptionShow_( self ):
		dsp = self.description
		if dsp is None : return
		if dsp == [] : return
		if dsp == "" : return
		toolbox.infoTip.showItemTips( self, dsp )

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_ROLE_BEGIN_COOLDOWN"] = self.__beginCooldown
		for trigger in self.__triggers.iterkeys():
			ECenter.registerEvent( trigger, self )

	def __deregisterTriggers( self ):
		for trigger in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( trigger, self )

	# -------------------------------------------------
	def __beginCooldown( self, cooldownType, lastTime ):
		"""
		handle cooldown message
		"""
		if self.itemInfo is None : return
		cdInfo = self.itemInfo.getCooldownInfo()
		self.__pyCDCover.unfreeze( *cdInfo )

	# -------------------------------------------------
	def onRClick_( self, mods ):
		BOItem.onRClick_( self, mods )
		if self.itemInfo is None : return
		player = BigWorld.player()
		player.useRacehorseItem( self.gbIndex ) #使用该道具

	def onDragStart_( self, pyDragged ):
		BOItem.onDragStart_( self, pyDragged )
		return True

	def onDragStop_( self, pyDragged ):
		BOItem.onDragStop_( self, pyDragged )
		return True

	def onDrop_( self, pyTarget, pyDropped ) :
		BOItem.onDrop_( self, pyTarget, pyDropped )
		dragMark = rds.ruisMgr.dragObj.dragMark
		if not self.__dropEvents.has_key( dragMark ) : return
		self.__dropEvents[dragMark]( pyTarget, pyDropped )
		return True
	
	def update( self, itemInfo ):
		BOItem.update( self, itemInfo )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getGBIndex( self ) :
		return self.__gbIndex

	def _setGBIndex( self, index ) :
		self.__gbIndex = index

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	gbIndex = property( _getGBIndex, _setGBIndex )

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

# --------------------------------------------------------------------
class DropHandlers :
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	@staticmethod
	def fromRaceBag( pyTarget, pyDropped ):
		"""
		the item draged from horserace bag
		"""
		dstOrder = pyTarget.gbIndex
		srcOreder = pyDropped.gbIndex
		BigWorld.player().swapRaceItems( srcOreder, dstOrder )


RACE_HORSE_TIME = 1200	# 赛马时间

class RaceHorseDataPanel( RootGUI ):
	def __init__( self ):
		panel = GUI.load( "guis/general/quickbar/racebag/raceTimePanel.gui" )
		uiFixer.firstLoadFix( panel )
		RootGUI.__init__( self, panel )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "TOP"
		self.moveFocus = False
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ = False
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyCurrentTime = StaticText( panel.lbTimeMsg )
		self.__pyCurrentTime.left = 0.0
		self.__pyCurrentTime.text = ""
		self.__pyRemainCircles  = StaticText( panel.lbCircleMsg )
		self.__pyRemainCircles.left = 0.0
		self.__pyRemainCircles.text = ""
		self.__currentCiecle = 1
		self._RaceHorseTimerID = 0
		self.visible = False
		self.leftTime = RACE_HORSE_TIME

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_SHOW_RACE_HORSE_TIME"]		= self.__onShowTimePanel		# 赛马比赛开始
		self.__triggers["EVT_ON_HIDE_RACE_HORSE_TIME"]		= self.__onHideTimePanel		# 赛马比赛结束
		self.__triggers["EVT_ON_UPDATE_RACE_CIRCLES"]		= self.__onUpdateRaceCircle		# 更新赛马圈数
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )

	def __onShowTimePanel( self ):
		"""
		赛马比赛开始
		"""
		if not self.visible:
			self.visible = True
		self.__currentCiecle = 1
		self.__pyCurrentTime.visible = True
		self.__pyCurrentTime.text = ""
		self.__pyRemainCircles.visible = True
		self.__pyRemainCircles.text = labelGather.getText( "quickbar:rhPanel", "stCircle" ) % self.__currentCiecle
		self.width = 300.0
		self._RaceHorseTimerID = Timer.addTimer( 0, 1, self.__gameTimeUpdate )

	def __onHideTimePanel( self ):
		"""
		赛马比赛结束
		"""
		self.__pyCurrentTime.text = ""
		if self.visible:
			self.visible = False
		self.__currentCiecle = 1
		self.leftTime = RACE_HORSE_TIME
		self.__cancelRaceHorseTimer()

	def __onUpdateRaceCircle( self ):
		"""
		更新赛马圈数
		"""
		if self.__currentCiecle < 3:
			self.__currentCiecle += 1
		self.__pyRemainCircles.text = labelGather.getText( "quickbar:rhPanel", "stCircle" ) % self.__currentCiecle

	def __gameTimeUpdate( self ):
		"""
		更新赛场剩余时间显示
		"""
		if not self.visible:
			self.__cancelRaceHorseTimer()
			return

		self.leftTime = self.leftTime - 1
		remainTime = self.leftTime
		if remainTime > 0:
			msg = ""
			minutes = remainTime / 60
			seconds = remainTime % 60
			if minutes <= 0:
				msg = labelGather.getText( "quickbar:rhPanel", "stSec" ) % seconds
			else:
				msg = labelGather.getText( "quickbar:rhPanel", "stMin" ) % minutes +\
					  labelGather.getText( "quickbar:rhPanel", "stSec" ) % seconds
			self.__pyCurrentTime.text = labelGather.getText( "quickbar:rhPanel", "stLeaveTime" ) % msg
			self.__pyCurrentTime.color = ( 128.0, 255.0, 0.0 )
		else:
			self.__pyCurrentTime.text = labelGather.getText( "quickbar:rhPanel", "stRaceOver" )
			self.__pyCurrentTime.color = ( 255.0, 255.0, 0.0 )

	def __cancelRaceHorseTimer( self ): #清除计时器
		Timer.cancel( self._RaceHorseTimerID )
		self._RaceHorseTimerID = 0
		self.leftTime = RACE_HORSE_TIME


	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		if self.visible:
			self.visible = False