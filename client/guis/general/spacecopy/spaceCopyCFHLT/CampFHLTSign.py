# -*- coding: gb18030 -*-
#

from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.StaticText import StaticText
from  guis.controls.ButtonEx import HButtonEx
import Timer

class CampFHLTSign( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/spacecopyabout/cFhltSign.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.__remainTime = 0
		self.__timeControlID = 0
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( wnd )
	
	def __initialize( self, wnd ):
		self.__pyStRemainTime = StaticText( wnd.panel.stRemainTime )
		self.__pyStRemainTime.fontSize = 18
		self.__pyStRemainTime.text = "00:00"
		
		self.__pyStMaxNum = StaticText( wnd.panel.stMaxNum )
		self.__pyStMaxNum.text =  labelGather.getText( "CampFHLTRankWnd:campFHLTSign", "stMaxNum" )% 0
		
		self.__pyStBattleNum = StaticText( wnd.panel.stBattleNum)
		self.__pyStBattleNum.text = labelGather.getText( "CampFHLTRankWnd:campFHLTSign", "stBattleNum" )% 0
		
		self.__pyBtnCancel = HButtonEx( wnd.panel.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R3C1 )
		self.__pyBtnCancel.onLClick.bind( self.__cancelSign ) 
		labelGather.setPyBgLabel( self.__pyBtnCancel, "CampFHLTRankWnd:campFHLTSign", "btnCancel" )
		
		labelGather.setLabel( wnd.lbTitle, "CampFHLTRankWnd:campFHLTSign", "lbTitle" )
		labelGather.setLabel( wnd.panel.remainTimeText, "CampFHLTRankWnd:campFHLTSign", "remainTimeText" )
	
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_HIDE_CAMP_FHLTR_SIGN_WND"] = self.__onHideWnd
		self.__triggers["EVT_ON_UPDATE_CAMP_FHLT_BATTLE_NUM"] = self.__onUpdateBattleNum
		for macroName in self.__triggers.iterkeys():
			ECenter.registerEvent( macroName, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for macroName in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( macroName, self )
	# -------------------------------------------------------
	
	def __updateRemainTime( self ):
		"""
		更新剩余时间
		"""
		if self.__remainTime <= 0:
			Timer.cancel( self.__timeControlID )
			self.__timeControlID = 0
			self.hide()
		else:
			self.__remainTime -= 1
			mins = self.__remainTime / 60
			secs = self.__remainTime % 60
			self.__pyStRemainTime.text = "%02d:%02d" % ( mins, secs )
	
	def __onShowWnd( self ):
		"""
		窗口显示
		"""
		Window.show( self )
		self.__remainTime = 600
		self.__timeControlID = Timer.addTimer( 0, 1, self.__updateRemainTime )
	
	def __onHideWnd( self ):
		"""
		隐藏窗口
		"""
		self.hide()
		
	def __onUpdateBattleNum( self, remainTime, battleNum, maxNum  ):
		"""
		更新玩家报名战场数字和当前最大战场数字
		"""
		battleNumText = labelGather.getText( "CampFHLTRankWnd:campFHLTSign", "stBattleNum" )% battleNum
		self.__pyStBattleNum.text = battleNumText
		
		maxNum = labelGather.getText( "CampFHLTRankWnd:campFHLTSign", "stMaxNum" )% maxNum
		self.__pyStMaxNum.text = maxNum	
		self.__remainTime = remainTime
		self.__timeControlID = Timer.addTimer( 0, 1, self.__updateRemainTime )
		Window.show( self )	
		
	def __cancelSign( self ):
		"""
		取消报名
		"""
		BigWorld.player().onRequestQuitCampFengHuoSignUp()	
	
	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, evtMacro, *args ) :
		self.__triggers[evtMacro]( *args )

	def onLeaveWorld( self ):
		self.hide()

	def hide( self ):
		self.__remainTime = 0
		if self.__timeControlID:
			Timer.cancel( self.__timeControlID )
		self.__timeControlID = 0
		Window.hide( self )
