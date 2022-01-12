# -*- coding: gb18030 -*-

import BigWorld
import Timer
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.RootGUI import RootGUI
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from guis.controls.BaseObjectItem import BaseObjectItem as BOItem
from guis.general.spacecopy.spaceCopyJueDiFanJi.CopyJueDiFanJiCount import CopyJueDiFanJiCount

class CopyAoZhanBox( RootGUI ):

	_cc_fly_times = [30, 20, 10, 5, 4, 3, 2, 1]

	def __init__( self ):
		box = GUI.load( "guis/general/spacecopyabout/spaceCopyAoZhan/copyAoZhanBox.gui" )
		uiFixer.firstLoadFix( box )
		RootGUI.__init__( self, box )
		self.h_dockStyle = "LEFT"
		self.v_dockStyle = "BOTTOM"
		self.moveFocus = False
		self.posZSegment = ZSegs.L5
		self.activable_ = False
		self.escHide_ = False
		self.addToMgr()
		self.__flashSign = True

		self.__isStart = False
		self.__countTime = 0
		self.__countTimerID = 0
		self.__initBox( box )
		self.__triggers = {}
		self.__registerTriggers()

	def __initBox( self, box ):
		self.__pyAoZhanPanel = CopyAoZhanPanel()
		self.__pyAoZhanCounter = CopyJueDiFanJiCount()
		self.__pyAoZhanItem = AoZhanItem( box.item.item, self )
		self.__pyAoZhanItem.onLClick.bind( self.__showAoZhan )

		self.__ringFader = box.fader
		self.__ringFader.speed = 0.4
		self.__ringFader.value = 1.0
		self.__flashID = 0

	# ----------------------------------------------------------
	# pravite
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_AOZHAN_BOX"] = self.__onShow
		self.__triggers["EVT_ON_HIDE_AOZHAN_BOX"] = self.__onHide
		self.__triggers["EVT_ON_AOZHAN_IS_JOIN"] = self.__isJoinAoZhan
		self.__triggers["EVT_ON_AOZHAN_COUNT_DOWN"] = self.__onAoZhanCountDown
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ):
		for key in self.__triggers.iterkeys():
			ECenter.unregisterEvent( key, self )

	# ----------------------------------------------------------
	def __flash( self ):
		"""
		窗口闪烁 淡入淡出
		"""
		BigWorld.cancelCallback( self.__flashID )
		self.__flashID = 0
		if self.__flashSign:
			self.__ringFader.value = 1.0
		else:
			self.__ringFader.value = 0.2
		self.__flashSign = not self.__flashSign
		self.__flashID = BigWorld.callback( self.__ringFader.speed + 0.1, self.__flash )

	def __stopFlash( self ):
		"""
		停止闪烁
		"""
		if self.__flashID:
			BigWorld.cancelCallback( self.__flashID )
			self.__flashID = 0
			self.__ringFader.value = 1.0

	def __showAoZhan( self, isSelected ):
		if isSelected:
			if self.__isStart:
				BigWorld.player().aoZhan_flushBattlefield()
			else:
				self.__pyAoZhanPanel.show()

	def __onShow( self ):
		if self.visible: return
		self.show()

	def __onHide( self ):
		self.hide()

	def __isJoinAoZhan( self, isJoin ):
		if isJoin:
			self.__isStart = True
			self.__onShow()
		else:
			self.__isStart = False
			self.__onHide()

	def __onAoZhanCountDown( self, time ):
		if self.__countTimerID > 0:
			Timer.cancel( self.__countTimerID )
		self.__countTime = time
		self.__countTimerID = Timer.addTimer( 1, 1, self.__onCountDown )
		if time in self._cc_fly_times:
			self.__pyAoZhanCounter.showTimeCount( time )

	def __onCountDown( self ):
		self.__countTime -= 1
		if self.__countTime > 0:
			if self.__countTime in self._cc_fly_times:
				self.__pyAoZhanCounter.showTimeCount( self.__countTime )
		else:
			Timer.cancel( self.__countTimerID )
			self.__countTimerID = 0
			self.__pyAoZhanCounter.visible = False

	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def show( self ):
		RootGUI.show( self )
		self.__flash()

	def hide( self ):
		self.__stopFlash()
		ECenter.fireEvent( "EVT_ON_HIDE_AOZHAN_RANK" )
		self.__pyAoZhanPanel.hide()
		RootGUI.hide( self )

	def onLeaveWorld( self ):
		Timer.cancel( self.__countTimerID )
		self.__isStart = False
		self.__countTime = 0
		self.__countTimerID = 0
		self.hide()

# -------------------------------------------------------------------------
class AoZhanItem( BOItem ):
	def __init__( self, item, pyBinder = None ):
		BOItem.__init__( self, item, pyBinder )
		self.icon = "guis/general/spacecopyabout/spaceCopyAoZhan/tb_azqx.dds"

	def onDescriptionShow_( self ):
		msg = labelGather.getText( "SpaceCopyAoZhan:AoZhanBox", "boxText" )
		toolbox.infoTip.showItemTips( self, msg )

# -------------------------------------------------------------------------
class CopyAoZhanPanel( Window ):
	def __init__( self ):
		panel = GUI.load( "guis/general/spacecopyabout/spaceCopyAoZhan/copyAoZhanPanel.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )

		self.__pyBtnTrans = HButtonEx( panel.btnTrans, self )		# 传送
		self.__pyBtnTrans.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnTrans.onLClick.bind( self.__aoZhanTrans )
		labelGather.setPyBgLabel( self.__pyBtnTrans, "SpaceCopyAoZhan:AoZhanPanel", "btnTrans" )

		self.__pyLbText = CSRichText( panel.lbText )
		self.__pyLbText.align = "C"
		self.__pyLbText.text = labelGather.getText( "SpaceCopyAoZhan:AoZhanPanel", "lbText" )

		labelGather.setLabel( panel.lbTitle, "SpaceCopyAoZhan:AoZhanPanel", "lbTitle" )
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"
		self.pressedOK_ = False
		self.callback_ = lambda *args : False
		self.activable_ = True
		self.escHide_ = True
		self.addToMgr()

	# -------------------------------------------------
	def __aoZhanTrans( self ):
		BigWorld.player().aoZhan_gotoEnterNPC()
		self.hide()
