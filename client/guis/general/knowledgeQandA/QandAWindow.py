# -*- coding: gb18030 -*-
#
# $Id: QuestHelp.py,v 1.5 2008-08-26 02:18:23 huangyongwei Exp $

"""
implement Knowledge Q&A
"""

from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.StaticText import StaticText
from guis.tooluis.CSTextPanel import CSTextPanel
import GUIFacade

class QandAWindow( Window ):
	def __init__( self ):
		wnd = GUI.load( "guis/general/knowledgeQandA/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_  = True
		self.remianQuest = -1 #剩余问题数
		self.__triggers = {}
		self.answerState = -1 #答题状态，默认为未回答
		self.__registerTriggers()
		self.__initialize( wnd )

	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "QandAWindow:main", "lbTitle" )
		self.__pyContPanel = ContentPanel( wnd.contsPanel )

		self.__pyTipsPanel = CSTextPanel( wnd.tipsPanel.clipPanel, wnd.tipsPanel.sbar )
		self.__pyTipsPanel.text = ""

		self.__pySigns = PyGUI( wnd.signs )
		self.__pySigns.visible = False

		self.__pyStRemain = StaticText( wnd.stRemain )
		self.__pyStRemain.text = ""

		self.__pyBtnNext = Button( wnd.btnNext )
		self.__pyBtnNext.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnNext.enable = False
		self.__pyBtnNext.onLClick.bind( self.__onNextQuest )
		labelGather.setPyBgLabel( self.__pyBtnNext, "QandAWindow:main", "btnNext" )

		self.__pyBtnQuit = Button( wnd.btnQuit )
		self.__pyBtnQuit.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnQuit.visible = False
		self.__pyBtnQuit.onLClick.bind( self.__onQuit )
		labelGather.setPyBgLabel( self.__pyBtnQuit, "QandAWindow:main", "btnQuit" )

		self.__pyBtnFulfill = Button( wnd.btnFulfill )
		self.__pyBtnFulfill.setStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnFulfill.visible = False
		self.__pyBtnFulfill.onLClick.bind( self.__onFullfill )
		labelGather.setPyBgLabel( self.__pyBtnFulfill, "QandAWindow:main", "btnFulfill" )

		labelGather.setLabel( wnd.tipsPanel.infoTitle.stTitle, "QandAWindow:main", "infoTitle" )
		labelGather.setLabel( wnd.remainText, "QandAWindow:main", "remainText" )
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_RECIEVE_NPC_QUESTIONS"]	= self.__onRecieveQuestions #问题内容
		self.__triggers["EVT_ON_IS_ANSWER_SUCCEED"] 	= self.__onIsSucceed #回答是否正确
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			ECenter.unregisterEvent( key, self )

	# ------------------------------------------------------------
	def __onRecieveQuestions( self, content, answers, questAccount, qusetInfo ):
		self.__pyContPanel.clearCheckers()
		self.answerState = -1 #重置答题状态
		self.__pyContPanel.setContent( content )
		self.__pyContPanel.addQuestions( answers )
		self.__pyStRemain.text = str( questAccount )
		self.__pySigns.visible = False
		self.__pyBtnQuit.visible = questAccount > 0
		self.__pyBtnFulfill.visible = questAccount <= 0
		self.__pyBtnNext.enable = False
		self.remianQuest = questAccount
		self.__pyTipsPanel.text = qusetInfo
		if self.visible:return
		self.show()
#		toolbox.infoTip.showOperationTips( 0x0084, self.__pyTipsPanel )
#		toolbox.infoTip.showOperationTips( 0x0085, self.__pyBtnNext )

	def __onIsSucceed( self, isSucceed ):
		self.__pySigns.visible = True
		self.__pyBtnNext.enable = isSucceed
		if isSucceed:
			self.remianQuest -= 1
			self.__pyBtnNext.enable = self.remianQuest > 0
			self.__pyStRemain.text = str( self.remianQuest )
			self.__pyBtnQuit.visible = self.remianQuest > 0
			self.__pyBtnFulfill.visible = self.remianQuest <= 0
			util.setGuiState( self.__pySigns.getGui(), ( 1, 2 ), ( 1, 1 ) )
			self.answerState = 1
			self.__pyContPanel.setCheckers()
		else:
			self.answerState = 0
			util.setGuiState( self.__pySigns.getGui(), ( 1, 2 ), ( 1, 2 ) )
			self.hide()

	def __onNextQuest( self ): #下一题
		player = BigWorld.player()
		target = GUIFacade.getGossipTarget()
		if target is None:return
		player.gossipWith( target, "START ANSWER" ) #重新对话
		self.__pyBtnNext.enable = False

	def __onQuit( self ): #退出
		msg = ""
		if self.answerState == -1:#未答题就退出
			# "您还未答题，是否确定退出？"
			msg = 0x0421
		elif self.answerState == 0: #回答错误
			# "答错了，不要气馁哦，您可以再次回答。"
			msg = 0x0422
		else: #回答正确
			# "退出回答，您需要重新对话开始。"
			msg = 0x0423
		def query( rs_id ):
			if rs_id == RS_OK:
				if self.visible:
					self.hide()
		showMessage( msg, "", MB_OK_CANCEL, query , pyOwner = self )
		return True

	def __onFullfill( self ):
		self.hide()
	
	def onMove_( self, dx, dy ):
		Window.onMove_( self, dx, dy )
#		toolbox.infoTip.moveOperationTips( 0x0083 )
#		toolbox.infoTip.moveOperationTips( 0x0084 )
#		toolbox.infoTip.moveOperationTips( 0x0085 )
	# ----------------------------------------------------------------
	# public
	# ----------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )

	def onLeaveWorld( self ):
		self.hide()

	def show( self ):
		Window.show( self )

	def hide( self ):
		self.__pyStRemain.text = ""
		self.remianQuest = -1
		self.__pyTipsPanel.text = ""
		self.__pySigns.visible = False
		self.answerState = -1
		self.__pyContPanel.clearText()
		self.__pyContPanel.clearCheckers()
		Window.hide( self )
		toolbox.infoTip.hideOperationTips( 0x0083 )
		toolbox.infoTip.hideOperationTips( 0x0084 )
		toolbox.infoTip.hideOperationTips( 0x0085 )
		GUIFacade.cancelTurnCB( GUIFacade.getGossipTarget() )

# ---------------------------------------------------------
from guis.controls.CheckerGroup import CheckerGroup
from guis.controls.CheckBox import CheckBoxEx
from guis.tooluis.CSRichText import CSRichText

class ContentPanel( PyGUI ):

	answer_tags = ["a", "b", "c", "d", "e"]

	def __init__( self, panel ):
		PyGUI.__init__( self, panel )
		self.__pyTextPanel = CSRichText( panel.textPanel )
		self.__pyTextPanel.opGBLink = True
		self.__pyTextPanel.align = "L"
		self.__pyTextPanel.text = ""

		self.__pyCheckGroup = CheckerGroup()
		self.__pyCheckGroup.onCheckChanged.bind( self.__onAnswerSelected )

		self.__pyChecksPanel = PyGUI( panel.checksPanel )

	def setContent( self, content ):
		self.__pyTextPanel.text = content

	def addQuestions( self, answers ):
		top = self.__pyTextPanel.bottom + 5.0
		left = self.__pyTextPanel.left + 5.0
		for index, answer in enumerate( answers ):
			ckBox = GUI.load( "guis/general/knowledgeQandA/qachecker.gui" )
			uiFixer.firstLoadFix( ckBox )
			pyQuestCheck = QusetCheckBox( ckBox )
			pyQuestCheck.text = answer
			pyQuestCheck.tag = self.answer_tags[index]
			pyQuestCheck.checked = False
			pyQuestCheck.clickCheck = True
			self.addPyChild( pyQuestCheck )
			top += pyQuestCheck.height + 2.0
			pyQuestCheck.top = top
			pyQuestCheck.left = left
			self.__pyCheckGroup.addChecker( pyQuestCheck )
#		toolbox.infoTip.showOperationTips( 0x0083, self.__pyCheckGroup.pyCheckers[0] )

	def clearCheckers( self ):
		if self.__pyCheckGroup.count > 0:
			for pyChecker in self.__pyCheckGroup.pyCheckers:
				self.delPyChild( pyChecker )
				pyChecker.dispose()
			self.__pyCheckGroup.clearCheckers()
			toolbox.infoTip.hideOperationTips( 0x0085 )

	def setCheckers( self ):
		if self.__pyCheckGroup.count > 0:
			for pyChecker in self.__pyCheckGroup.pyCheckers:
				pyChecker.enable = False

	def clearText( self ):
		self.__pyTextPanel.text = ""

	def __onAnswerSelected( self, checker ): #选择答案
		if checker is None:return
		tag= checker.tag
		target = GUIFacade.getGossipTarget()
		if target is None:return
		BigWorld.player().gossipWith( target, tag )

# ------------------------------------------------------------
# 任务答案单选框
class QusetCheckBox( CheckBoxEx ):
	def __init__( self, checkerBox ):
		CheckBoxEx.__init__( self, checkerBox )

	# ----------------------------------------------------------------
	# property methods
	# ----------------------------------------------------------------
	def _getText( self ) :
		return self.pyText_.text

	def _setText( self, text ) :
		self.pyText_.text = text
		self.width = self.pyText_.right + 2.0

	# ----------------------------------------------------------------
	# properties
	# ----------------------------------------------------------------
	text = property( _getText, _setText )						# 获取/设置文本