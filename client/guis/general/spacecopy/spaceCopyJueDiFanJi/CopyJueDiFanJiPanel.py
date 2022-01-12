# -*- coding: gb18030 -*-

import BigWorld
import Timer
import csdefine
import csstatus
import csconst
from guis import *
from LabelGather import labelGather
from guis.common.Window import Window
from guis.controls.ButtonEx import HButtonEx
from guis.tooluis.CSRichText import CSRichText
from Time import Time
from CopyJueDiFanJiCount import CopyJueDiFanJiCount

class CopyJueDiFanJiPanel( Window ):
	def __init__( self, pyBinder = None ):
		panel = GUI.load( "guis/general/spacecopyabout/spaceCopyJueDiFanJi/copyJueDiFanJiPanel.gui" )
		uiFixer.firstLoadFix( panel )
		Window.__init__( self, panel )

		self.__pyBtnSignUp = HButtonEx( panel.btnSignUp, self )	# 报名
		self.__pyBtnSignUp.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnSignUp.onLClick.bind( self.__jueDiSignUp )
		labelGather.setPyBgLabel( self.__pyBtnSignUp, "SpaceCopyJueDiFanJi:JueDiPanel", "btnSignUp" )

		self.__pyBtnCancelMatch = HButtonEx( panel.btnCancelMatch, self )	# 取消匹配
		self.__pyBtnCancelMatch.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancelMatch.onLClick.bind( self.__jueDiCancelMatch )
		labelGather.setPyBgLabel( self.__pyBtnCancelMatch, "SpaceCopyJueDiFanJi:JueDiPanel", "btnCancelMatch" )

		self.__pyBtnConfirm = HButtonEx( panel.btnConfirm, self )	# 确认
		self.__pyBtnConfirm.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnConfirm.onLClick.bind( self.__jueDiConfirm )
		labelGather.setPyBgLabel( self.__pyBtnConfirm, "SpaceCopyJueDiFanJi:JueDiPanel", "btnConfirm" )

		self.__pyBtnEnter = HButtonEx( panel.btnEnter, self )		# 进入
		self.__pyBtnEnter.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnEnter.onLClick.bind( self.__jueDiEnter )
		labelGather.setPyBgLabel( self.__pyBtnEnter, "SpaceCopyJueDiFanJi:JueDiPanel", "btnEnter" )

		self.__pyBtnRank = HButtonEx( panel.btnRank, self )		# 榜单
		self.__pyBtnRank.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnRank.onLClick.bind( self.__showJueDiRank )
		labelGather.setPyBgLabel( self.__pyBtnRank, "SpaceCopyJueDiFanJi:JueDiPanel", "btnRank" )

		self.__pyBtnCancel = HButtonEx( panel.btnCancel, self )		# 取消
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnCancel.onLClick.bind( self.__onCancelEnter )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "SpaceCopyJueDiFanJi:JueDiPanel", "btnCancel" )

		self.__pyLbText = CSRichText( panel.lbText )
		self.__pyLbText.align = "C"
		self.__pyLbText.text = ""

		self.__jueDiCounter = CopyJueDiFanJiCount()
		labelGather.setLabel( panel.lbTitle, "SpaceCopyJueDiFanJi:JueDiPanel", "lbTitle" )
		self.h_dockStyle = "CENTER"
		self.v_dockStyle = "MIDDLE"
		self.pressedOK_ = False
		self.callback_ = lambda *args : False
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ = True
		self.addToMgr()

		self.__remainTime = 0
		self.__confirmTimerID = 0
		self.__repeatedVictoryCount = 0
		self.__countTime = 0
		self.__countTimerID = 0
		self.__triggers = {}
		self.__registerTriggers()

	# ----------------------------------------------------------
	# pravite
	# ----------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_SHOW_JUEDI_PANEL"] = self.__onShow	#显示面板
		self.__triggers["EVT_ON_HIDE_JUEDI_PANEL"] = self.__onHide	#隐藏面板
		self.__triggers["EVT_ON_JUEDI_SIGN_UP"] = self.__onJueDiSignUp	#报名成功
		self.__triggers["EVT_ON_JUEDI_MATCH_SUCCESS"] = self.__onJueDiMatchSuccess #匹配成功
		self.__triggers["EVT_ON_JUEDI_CONFIRM"] = self.__onJueDiConfirm	#确认进入
		self.__triggers["EVT_ON_VICTORY_COUNT_CHANGE"] = self.__onVictoryCountChange	#连胜次数改变
		self.__triggers["EVT_ON_JUEDI_COUNT_DOWN"] = self.__onJueDiCountDown #比赛开始倒计时
		for key in self.__triggers.iterkeys():
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ):
		for key in self.__triggers.iterkeys():
			ECenter.unregisterEvent( key, self )

	# -------------------------------------------------
	def __jueDiSignUp( self ):
		"""
		"""
		BigWorld.player().jueDiFanJiSignUp()
		self.hide()

	def __onJueDiSignUp( self ):
		#报名成功
		self.__isFinish = False
		self.__initJueDiFanJiState()
		BigWorld.player().statusMessage( csstatus.JUE_DI_FAN_JI_ON_SIGN_UP )

	def __jueDiCancelMatch( self ):
		pass

	def __jueDiConfirm( self ):
		BigWorld.player().jueDiFanJiEnterConfirm()
		self.hide()

	def __onJueDiMatchSuccess( self ):
		#匹配成功
		self.__remainTime = csconst.JUE_DI_FAN_JI_WAIT_TIME
		self.__initJueDiFanJiState()
		Timer.cancel( self.__confirmTimerID )
		self.__confirmTimerID = Timer.addTimer( 1.0, 1.0, self.__countDown )

	def __countDown( self ):
		self.__remainTime -= 1
		if self.__remainTime <= 0:
			Timer.cancel( self.__confirmTimerID )
			self.__confirmTimerID = 0
			self.hide()
			return
		if self.__pyBtnConfirm.visible:
			self.__pyLbText.text = labelGather.getText( "SpaceCopyJueDiFanJi:JueDiPanel", "confirmText", self.__remainTime )

	def __onJueDiConfirm( self ):
		#确认进入
		self.__initJueDiFanJiState()

	def __jueDiEnter( self ):
		pass

	def __onVictoryCountChange( self, repeatedVictoryCount ):
		self.__repeatedVictoryCount = repeatedVictoryCount

	def __showJueDiRank( self ):
		BigWorld.player().showJueDiFanJiRankList()
		self.hide()

	def __onCancelEnter( self ):
		if self.__confirmTimerID:
			Timer.cancel( self.__confirmTimerID )
			self.__confirmTimerID = 0
			self.__remainTime = 0
		BigWorld.player().jueDiFanJiCancelEnter()
		self.hide()

	def __onJueDiCountDown( self, time ):
		if self.__countTimerID > 0:
			Timer.cancel( self.__countTimerID )
		self.__countTime = time
		self.__countTimerID = Timer.addTimer( 1, 1, self.__onCountDown )
		self.__jueDiCounter.showTimeCount( time )

	def __onCountDown( self ):
		self.__countTime -= 1
		if self.__countTime > 0:
			self.__jueDiCounter.showTimeCount( self.__countTime )
		else:
			Timer.cancel( self.__countTimerID )
			self.__countTimerID = 0
			self.__jueDiCounter.visible = False

	def __onShow( self, state ):
		self.show( state )

	def __onHide( self ):
		self.hide()

	def __updatePanel( self, state ):
		"""
		根据状态信息更新面板
		"""
		if state == csdefine.JUE_DI_FAN_JI_NOT_SIGN_UP: #未报名阶段
			self.__pyBtnSignUp.visible = True
			self.__pyBtnSignUp.enable = True
			self.__pyBtnCancelMatch.visible = False
			self.__pyBtnConfirm.visible = False
			self.__pyBtnEnter.visible = False
			self.__pyBtnRank.visible = False
			self.__pyBtnCancel.visible = False
			self.__pyLbText.text = labelGather.getText( "SpaceCopyJueDiFanJi:JueDiPanel", "signUpText" )
		elif state == csdefine.JUE_DI_FAN_JI_HAS_SIGN_UP: #匹配阶段
			self.__pyBtnSignUp.visible = False
			self.__pyBtnCancelMatch.visible = False
			self.__pyBtnConfirm.visible = False
			self.__pyBtnEnter.visible = False
			self.__pyBtnRank.visible = False
			self.__pyBtnCancel.visible = False
			self.__pyLbText.text = labelGather.getText( "SpaceCopyJueDiFanJi:JueDiPanel", "matchText" )
			if self.__repeatedVictoryCount != 0:
				self.__pyLbText.text = labelGather.getText( "SpaceCopyJueDiFanJi:JueDiPanel", "againMatchText", self.__repeatedVictoryCount )
		elif state == csdefine.JUE_DI_FAN_JI_HAS_MATCHED:	#匹配成功阶段
			self.__pyBtnSignUp.visible = False
			self.__pyBtnCancelMatch.visible = False
			self.__pyBtnConfirm.visible = True
			self.__pyBtnConfirm.enable = True
			self.__pyBtnEnter.visible = False
			self.__pyBtnRank.visible = False
			self.__pyBtnCancel.visible = True
			self.__pyBtnCancel.enable = True
			self.__pyLbText.text = labelGather.getText( "SpaceCopyJueDiFanJi:JueDiPanel", "confirmText", self.__remainTime )
		elif state == csdefine.JUE_DI_FAN_JI_HAS_CONFIRM_ENTER:	#确定进入阶段
			self.__pyBtnSignUp.visible = False
			self.__pyBtnCancelMatch.visible = False
			self.__pyBtnConfirm.visible = False
			self.__pyBtnEnter.visible = True
			self.__pyBtnEnter.enable = False
			self.__pyLbText.text = labelGather.getText( "SpaceCopyJueDiFanJi:JueDiPanel", "enterText" )
			self.__pyBtnRank.visible = False
			self.__pyBtnCancel.visible = True
			self.__pyBtnCancel.enable = True
		elif state == csdefine.JUE_DI_FAN_JI_HAS_ENTERED:	#已经进入副本阶段
			self.hide()
		elif state == csdefine.JUE_DI_FAN_JI_SHOW_RANK_LIST:	#结束查看榜单阶段
			self.__pyBtnSignUp.visible = False
			self.__pyBtnCancelMatch.visible = False
			self.__pyBtnConfirm.visible = False
			self.__pyBtnEnter.visible = False
			self.__pyBtnCancel.visible = False
			self.__pyBtnRank.visible = True
			self.__pyBtnRank.enable = True
			self.__pyLbText.text = labelGather.getText( "SpaceCopyJueDiFanJi:JueDiPanel", "rankText" )

	def __initJueDiFanJiState( self ):
		BigWorld.player().initJueDiFanJiButtonState()

	# ---------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ):
		self.__triggers[eventMacro]( *args )

	def show( self, state, pyOwner = None ):
		self.__updatePanel( state )
		Window.show( self, pyOwner )

	def clickShow( self ):
		"""
		点击图标显示面板
		"""
		if self.visible:
			self.hide()
			return
		self.__initJueDiFanJiState()

	def onLeaveWorld( self ):
		Timer.cancel( self.__confirmTimerID )
		Timer.cancel( self.__countTimerID )
		self.__remainTime = 0
		self.__confirmTimerID = 0
		self.__repeatedVictoryCount = 0
		self.__countTime = 0
		self.__countTimerID = 0
		self.hide()
