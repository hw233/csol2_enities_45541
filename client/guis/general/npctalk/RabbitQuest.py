# -*- coding: gb18030 -*-
#
# $Id: AutoFightWindow.py,v 1.5 2008-07-24 09:40:16 wangshufeng Exp $

"""
implement autofight window
"""
from guis import *
import Language
from AbstractTemplates import Singleton
from LabelGather import labelGather
from guis.common.Window import Window
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from guis.controls.RadioButton import RadioButtonEx
from guis.controls.StaticText import StaticText
from guis.controls.CheckerGroup import CheckerGroup
import Timer
import Time

class RabbitQuest( Singleton, Window ):
	
	__instance=None
	__triggers = {}
	
	_remain_time = 10.0
	
	def __init__( self ):
		assert RabbitQuest.__instance is None ,"RabbitQuest instance has been created"
		RabbitQuest.__instance = self
		wnd = GUI.load( "guis/general/npctalk/rabbitquest.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ 	= False
		self.focus = False
		self.reTimerID = 0
		self.remainTime = 0.0
		self.buffID = 0
		self.__initialize( wnd )
		self.addToMgr( "rabbitQuest" )

	def __del__( self ) :
		Window.__del__( self )
		if Debug.output_del_RabbitQuest:
			INFO_MSG( str( self ) )

	def dispose( self ) :
		Window.dispose( self )
		self.__class__.releaseInst()

	@staticmethod
	def instance():
		"""
		get the exclusive instance of RabbitQuest
		"""
		if RabbitQuest.__instance is None:
			RabbitQuest.__instance = RabbitQuest()
		return RabbitQuest.__instance

	@staticmethod
	def getInstance():
		"""
		return None or the instance of RabbitQuest
		"""
		return RabbitQuest.__instance
	
	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "RabbitQuest:main", "lbTitle" )
		self.__pyContentPanel = CSRichText( wnd.contentPanel )
		self.__pyContentPanel.text = ""
		self.__pyOptionsPanel = PyGUI( wnd.optionsPanel )
		self.__pyStRemain = StaticText( wnd.stRemain )
		self.__pyStRemain.text = ""

		self.__pyCheckGroup = CheckerGroup()
		self.__pyCheckGroup.onCheckChanged.bind( self.__onOptionSelected )
		
		labelGather.setLabel( wnd.contentFrm.bgTitle.stTitle, "RabbitQuest:main", "frmTitle" )
		labelGather.setLabel( wnd.remainText, "RabbitQuest:main", "remainText" )
	
	def __onOptionSelected( self, checker ):
		"""
		选择答案
		"""
		if checker is None:return
		key = checker.key
		BigWorld.player().cell.answerBuffQuestion( self.buffID, key )
		
	def onRecQuestion( self, question ):
		"""
		接收并显示问题
		"""
		if question is None:return
		self.clearCheckers()
		topOffset = 5.0
		leftOffset = 5.0
		questDes = question.questDes
		answers = question.answers
		self.buffID = question.buffID
		self.__pyContentPanel.text = questDes
		if answers is None:return
		index = 0
		for key, answer in answers.items():
			if answer == "":continue
			option = GUI.load( "guis/general/npctalk/rabbititem.gui" )
			uiFixer.firstLoadFix( option )
			pyAnswerCheck = RadioButtonEx( option )
			pyAnswerCheck.text = answer
			pyAnswerCheck.key = key
			pyAnswerCheck.checked = False
			pyAnswerCheck.clickCheck = True
			self.__pyOptionsPanel.addPyChild( pyAnswerCheck )
			pyAnswerCheck.top = pyAnswerCheck.height*index + topOffset
			pyAnswerCheck.left = leftOffset
			index += 1
			self.__pyCheckGroup.addChecker( pyAnswerCheck )
		if not self.visible:
			self.remainTime = 10.0
			self.reTimerID = Timer.addTimer( 0, 1, self.__countDown )
			self.show()
	
	def __countDown( self ):
		self.remainTime -= 1.0
		self.__pyStRemain.text = labelGather.getText( "RabbitQuest:main", "remainTime" )%int( self.remainTime )
		if self.remainTime <= 0.0: #倒计时结束
			Timer.cancel( self.reTimerID )
			self.reTimerID = 0

	def clearCheckers( self ):
		if self.__pyCheckGroup.count > 0:
			for pyChecker in self.__pyCheckGroup.pyCheckers:
				self.__pyOptionsPanel.delPyChild( pyChecker )
				pyChecker.dispose()
			self.__pyCheckGroup.clearCheckers()
	
	def onQuestionEnd( self ):
		"""
		答题回调
		"""
		Timer.cancel( self.reTimerID )
		self.reTimerID = 0
		self.hide()
	
	def show( self ):
		self.middle = BigWorld.screenHeight()/2.0
		self.center = BigWorld.screenWidth()/2.0
		Window.show( self )
	
	def hide( self ):
		self.__pyContentPanel.text = ""
		self.clearCheckers()
		Window.hide( self )
	
	def onLeaveWorld( self ):
		self.hide()
	
	@classmethod
	def __onRecQuestion( SELF, question ):
		"""
		接收题目内容和选项，在开始或答错后
		"""
		SELF.inst.onRecQuestion( question )
		
	@classmethod
	def __onQuestionEnd( SELF ):
		"""
		回答问题结果对错回调
		"""
		SELF.inst.onQuestionEnd()
	
	@classmethod
	def __onResolutionChanged( SELF, preReso ):
		"""
		分辨率改变时调用
		"""
		SELF.inst.middle = BigWorld.screenHeight()/2.0
		SELF.inst.center = BigWorld.screenWidth()/2.0

	@classmethod
	def onEvent( SELF, evtMacro, *args) :
		SELF.__triggers[ evtMacro ]( *args )

	@classmethod
	def registerEvents( SELF ) :
		SELF.__triggers["EVT_ON_RABBIT_QUESTION_RECEIVE"] = SELF.__onRecQuestion
		SELF.__triggers["EVT_ON_RABBIT_QUESTION_END"] = SELF.__onQuestionEnd
		SELF.__triggers["EVT_ON_RESOLUTION_CHANGED"] = SELF.__onResolutionChanged
		for key in SELF.__triggers :
			ECenter.registerEvent( key, SELF )

RabbitQuest.registerEvents()