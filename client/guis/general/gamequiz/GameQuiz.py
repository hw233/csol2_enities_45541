# -*- coding: gb18030 -*-
#
# $Id: TongStorage.py, fangpengjun Exp $

"""
implement GameQuiz window class

"""
from guis import *
from LabelGather import labelGather
from guis.common.PyGUI import PyGUI
from guis.common.Window import Window
from guis.controls.Button import Button
from guis.controls.ButtonEx import HButtonEx
from guis.controls.StaticText import StaticText
from guis.tooluis.CSRichText import CSRichText
from guis.controls.CheckBox import CheckBoxEx
from guis.controls.SelectableButton import SelectableButton
from Time import Time
import csconst
import Timer
import csdefine
import Font

TIMER_INTERVAL = 21.0 #时间间隔

PRE_QUEST_TIME = 30.0 #答题前倒计时

class GameQuizWnd( Window ):

	def __init__( self ):
		wnd = GUI.load( "guis/general/gamequiz/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = False
		self.__initialize( wnd )
		self.boxTimerID = 0 #确认框计时
		self.questID = 0 #当前问题ID
		self.preTimerID = 0 #准备时间
		self.preTime = 0.0 #确认框已过时间
		self.remainTimerID = 0 #题目之间的time
		self.endTime = 0
		self.nextTimeID = 0
		self.nextTime = 0.0
		self.reMainTime = TIMER_INTERVAL
		self.alreadyNume = 0 #已出题目数量
		self.isUseLuckStar = False #是否使用幸运星
		self.isUseHead = False #是否使用"心有灵犀"
		self.isAnswered = False
		self.totalNumber = 0
		self.__triggers = {}
		self.__registerTriggers()
		self.currentTime = 0.0
		self.isSelectAnswer = False #是否已经选定答案

	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "GameQuiz:main", "lbTitle" )
		self.pyCloseBtn_.onLClick.bind( self.__onClosed )

		self.__pyBtnHeart = HButtonEx( wnd.btnHeart ) #使用心有灵犀
		self.__pyBtnHeart.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnHeart.enable = False
		self.__pyBtnHeart.onLClick.bind( self.__onUseYourHead )
		self.__pyBtnHeart.onMouseEnter.bind( self.__showHeartTips )
		self.__pyBtnHeart.onMouseLeave.bind( self.__hideHeartTip )
		self.__pyBtnHeart.onLMouseDown.bind( self.__hideHeartTip )
		labelGather.setPyBgLabel( self.__pyBtnHeart, "GameQuiz:main", "btnHeart" )

		self.__pyStReTime = StaticText( wnd.stRetime ) #剩余时间
		self.__pyStReTime.text = ""

		self.__pyStReQuest = StaticText( wnd.stRequest ) #剩余题目
		self.__pyStReQuest.text = ""

		self.__pyStTaxis = StaticText( wnd.stTaxis ) #排名
		self.__pyStTaxis.text = ""

		self.__pyStScore = StaticText( wnd.stScore ) #积分
		self.__pyStScore.text = 0

		self.__pyContPanel = ContentPanel( wnd.contPanel, self )

		self.__pyStCountdown = StaticText( wnd.stCountdown ) #读秒倒计时十位数
		self.__pyStCountdown.text = ""
		self.__pyStCountdown.fontSize = 30
		self.__pyStCountdown.limning = Font.LIMN_OUT
		self.__pyStCountdown.color = 255, 240, 222

		self.stRemind = wnd.stRemind

		self.__pyAnswerSign = PyGUI( wnd.answerSign ) #是对还是错
		self.__pyAnswerSign.visible = False

		self.__pySortItems = {}
		self.__pyLuckStars = {}
		for name, item in wnd.children: #排名控件
			if name.startswith( "sortItem_" ):
				index = int( name.split( "_" )[1] )
				pySortItem = SortItem( item )
				pySortItem.setTextes( "", "", "" )
				self.__pySortItems[index] = pySortItem

			if name.startswith( "star_" ): #幸运星
				index = int( name.split( "_" )[1] )
				pyLuckStar = LuckStarBtn( item )
				pyLuckStar.isUsed = False #是否已经使用
				pyLuckStar.index = index
				pyLuckStar.setStatesMapping( UIState.MODE_R2C2 )
				pyLuckStar.onMouseEnter.bind( self.__onLuckStarEnter )
				pyLuckStar.onMouseLeave.bind( self.__onLuckStarLeave )
				pyLuckStar.onLMouseDown.bind( self.__onLuckStarLeave )
				pyLuckStar.onLClick.bind( self.__onUseLuckStar )
				self.__pyLuckStars[index] = pyLuckStar

		labelGather.setLabel( wnd.curInterText, "GameQuiz:main", "curInterText" )
		labelGather.setLabel( wnd.curRankText, "GameQuiz:main", "curRankText" )
		labelGather.setLabel( wnd.remQsText, "GameQuiz:main", "remQsText" )
		labelGather.setLabel( wnd.remTiemText, "GameQuiz:main", "remTiemText" )
		labelGather.setLabel( wnd.luckStarText, "GameQuiz:main", "luckStarText" )
		labelGather.setLabel( wnd.rankTitle.col_0.lbText, "GameQuiz:main", "rankText" )
		labelGather.setLabel( wnd.rankTitle.col_1.lbText, "GameQuiz:main", "nameText" )
		labelGather.setLabel( wnd.rankTitle.col_2.lbText, "GameQuiz:main", "integralText" )
		labelGather.setLabel( wnd.listFrm.bgTitle.stTitle, "GameQuiz:main", "integralRank" )
	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		"""
		register event triggers
		"""
		self.__triggers["EVT_ON_QUIZ_INVITE_JOIN"] = self.__onInviteJoin #邀请答题
		self.__triggers["EVT_ON_QUIZ_ENTER_STATE"] =  self.__onEnterQuiz #进入答题
		self.__triggers["EVT_ON_QUIZ_RECEIVE_QUESTIONS"] = self.__onRecQuests #接收问题
		self.__triggers["EVT_ON_QUIZ_RECEIVE_ANSWER"] = self.__onRecAnswer #接收正确答案
		self.__triggers["EVT_ON_QUIZ_RECEIVE_TOPS"] = self.__onRecTops #积分排名
		self.__triggers["EVT_ON_QUIZ_SCORE_CHANGE"] = self.__onScoreChange #积分改变
		self.__triggers["EVT_ON_QUIZ_ANSWER_STATE"]	= self.__onAnswerState #对错
		self.__triggers["EVT_ON_ROLE_GOLD_CHANGED"] = self.__onGoldChanged 	#金元宝数量发生变化
		self.__triggers["EVT_ON_QUIZ_TOTAL_NUMBER"] = self.__onRecTotalNum #题目总数
		self.__triggers["EVT_ON_QUIZ_USE_LUCKSTAR"] = self.__onLuckStarUsed #使用幸运星
		self.__triggers["EVT_ON_QUIZ_ON_ENTER_INVITE_JOIN"] = self.__onEnterInviteJoin # 登录知识问答进行邀请答题
		self.__triggers["EVT_ON_QUIZ_SELECT_ANSWER"] = self.__onSelectAnswer #选定答案

		for macroName in self.__triggers.iterkeys():
			ECenter.registerEvent( macroName, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for macroName in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( macroName, self )

	# ------------------------------------------------------------
	def __onInviteJoin( self ):
		"""
		邀请参加
		"""
		player = BigWorld.player()
		if not rds.statusMgr.isInWorld():return
		self.boxTimerID = Timer.addTimer( 0, 1, self.__boxCountdown ) #弹出确认框倒计时
		if player.getCurrentSpaceType() == csdefine.SPACE_TYPE_NORMAL:
			# "想获得大量经验和潜能吗？知识答题简单又有趣，快点击确定参与吧。"
			askString = 0x03a2
		else:
			# "是否需要传送回复活点进行答题？"
			askString = 0x03a3
		def query( rs_id ):
			if rs_id == RS_OK:
				player.quiz_request()
				self.__cancelBoxTimer()
		self.pyBox = getattr( self, "pyBox", None )
		if self.pyBox:self.pyBox.hide()
		self.pyBox = showAutoHideMessage( 30, askString, "", MB_OK_CANCEL, query )
		return True

	def __onEnterInviteJoin( self ):
		"""
		刚登陆，邀请参加
		"""
		player = BigWorld.player()
		if not rds.statusMgr.isInWorld():return
		if player.getCurrentSpaceType() == csdefine.SPACE_TYPE_NORMAL:
			# "知识答题活动正在进行，您是否参加活动？"
			askString = 0x03a4
		else:
			# "知识答题活动正在进行，是否需要传送回复活点进行答题？"
			askString = 0x03a5
		def query( rs_id ):
			if rs_id == RS_OK:
				player.quiz_request()
		self.pyBox = getattr( self, "pyBox", None )
		if self.pyBox:self.pyBox.hide()
		self.pyBox = showAutoHideMessage( 30, askString, "", MB_OK_CANCEL, query )
		return True

	def __boxCountdown( self ):
		self.preTime += 1
		if self.preTime >= PRE_QUEST_TIME:
			self.__cancelBoxTimer()

	def __cancelBoxTimer( self ):
		Timer.cancel( self.boxTimerID )
		self.boxTimerID = 0

	def __onEnterQuiz( self ):
		"""
		进入答题
		"""
		if self.visible:return
		else:self.show()
		startTime = BigWorld.player().quizGameStartTime
		if startTime > 0.0: #中途上线答题
			alreadyTime = Time.time() - startTime #已经开始持续时间
			if alreadyTime < 30.0: #还在答题前倒计时
				self.preEndTime = Time.time() +( PRE_QUEST_TIME - alreadyTime )
				self.preTimerID = Timer.addTimer( 0, 1, self.__preCountdown )
			else: #已经开始答题，等待下一题开始
				self.__pyStCountdown.visible = False
				self.stRemind.visible = True
				labelGather.setLabel( self.stRemind, "GameQuiz:main", "nextQuestion" )
				for pyPoint in self.__pyLuckStars.itervalues():
					pyPoint.focus = False
		else: #
			self.preEndTime = Time.time() +( PRE_QUEST_TIME - self.preTime )
			self.preTimerID = Timer.addTimer( 0, 1, self.__preCountdown )

	def __preCountdown( self ):
		"""
		题目发过来之前的倒计时
		"""
		preRemain = self.preEndTime - Time.time()
		self.__pyStCountdown.visible = preRemain > 0
		self.stRemind.visible =  preRemain > 0
		labelGather.setLabel( self.stRemind, "GameQuiz:main", "distQandA" )
		self.__pyStCountdown.text = str( int( preRemain ) )
		if preRemain <= 0:
			Timer.cancel( self.preTimerID )
			self.preTimerID = 0
			self.preTime = 0.0
		for pyPoint in self.__pyLuckStars.itervalues():
			pyPoint.focus = preRemain <= 0

	def __onRecQuests( self, questID, comment, optionalStrs ):
		"""
		接收问题
		"""
		self.alreadyNume += 1
		if self.isUseHead:
			self.isUseHead = False #重新设置元宝答题状态
		self.__pyContPanel.clearCheckers()
		self.__pyAnswerSign.visible = False
		self.isUseLuckStar = False
		self.isAnswered = False
		self.isSelectAnswer = False
		self.__cancelRemainTimer()
		self.__pyStReQuest.text = str( self.totalNumber - self.alreadyNume )
		self.questID = questID
		self.reMainTime = TIMER_INTERVAL
		self.__pyContPanel.setContent( questID, comment, optionalStrs )
		self.currentTime = Time.time()
		self.remainTimerID = Timer.addTimer( 0.0, 1.0, self.__countDown )

	def __onRecAnswer( self, questID, questAnswer ): #使用元宝后接收正确的答案
		if questID != self.questID:return
		self.__pyContPanel.onRecAnswer( questAnswer )
		self.isAnswered = True
		self.__pyAnswerSign.visible = True
		util.setGuiState( self.__pyAnswerSign.getGui(), ( 1, 2 ), ( 1, 1 ) )

	def __onRecTops( self, roleList, scoreList, playerOrder ): #积分排名
		for index, pySort in self.__pySortItems.iteritems(): #清空积分排名
			pySort.setSortInfo( index, ( 0, 0 ) )

		for index, tuple in enumerate( zip( roleList, scoreList ) ):
			pySortItem = self.__pySortItems.get( index )
			if pySortItem is None:return
			pySortItem.setSortInfo( index, tuple )

		self.__pyStTaxis.text = str( playerOrder + 1 )
		
	def __onGoldChanged( self, oldValue, newValue ):
		pass

	def __showHeartTips( self ):
		if not self.__pyBtnHeart.enable: return
		dsp = labelGather.getText( "GameQuiz:main", "heartTips" )
		toolbox.infoTip.showToolTips( self, dsp )

	def __hideHeartTip( self ):
		"""
		隐藏按钮功能提示
		"""
		toolbox.infoTip.hide()

	def __onRecTotalNum( self, totalNum ):
		self.totalNumber = totalNum

	def __onScoreChange( self, score ):
		"""
		玩家积分改变,说明回答正确
		"""
		self.__pyStScore.text = str( score )

	def __onAnswerState( self, questID, answerState ):
		if questID != self.questID :return
		if answerState: #答对
			util.setGuiState( self.__pyAnswerSign.getGui(), ( 1, 2 ), ( 1, 1 ) )
		else: #答错
			util.setGuiState( self.__pyAnswerSign.getGui(), ( 1, 2 ), ( 1, 2 ) )
		self.__pyContPanel.setCheckers() #不管对错，选项不能再选
		self.__pyAnswerSign.visible = True
		self.stRemind.text = ""

	def __onLuckStarUsed( self, index ):
		self.isUseLuckStar = True
		for starIndex, pyLuckStar in self.__pyLuckStars.items():
			if pyLuckStar.isUsed:
				continue
			pyLuckStar.isUsed = starIndex == index

	def __onLuckStarEnter( self, pyStarLuck ):
		isUsed = pyStarLuck.isUsed
		if not isUsed:
			msg = labelGather.getText( "GameQuiz:main", "luckStarDsp" )
		toolbox.infoTip.showItemTips( self, msg )

	def __onLuckStarLeave( self ):
		toolbox.infoTip.hide()

	def __onUseYourHead( self ):
		"""
		使用心有灵犀
		"""
		scoreRate = 1
		if self.isUseLuckStar:
			scoreRate = 2
		BigWorld.player().quiz_useGold( self.questID, scoreRate )
		self.isUseHead = True
		self.__pyBtnHeart.enable = False

	def __onUseLuckStar( self, pyLuckStar ):
		"""
		使用幸运星
		"""
		if self.isUseLuckStar: return
		if self.isSelectAnswer: return
		pyLuckStar.isUsed = True
		index = pyLuckStar.index
		ECenter.fireEvent( "EVT_ON_QUIZ_USE_LUCKSTAR", index )

	def __onSelectAnswer( self ):
		"""
		选定答案
		"""
		self.isSelectAnswer = True

	def __countDown( self ):
		"""
		读秒倒计时,在倒数10-20秒内不让答题，0-10才让答题，界面需要相应处理
		"""
		self.reMainTime -= 1.0
		if self.preTimerID > 0:
			Timer.cancel( self.preTimerID )
			self.preTimerID = 0
			self.stRemind.text = ""
			self.__pyStCountdown.text = ""
		self.__pyContPanel.setContState( self.reMainTime )
		self.__pyStCountdown.visible = self.reMainTime > 0 and not self.__pyAnswerSign.visible
		self.__pyStReTime.visible = self.reMainTime > 0
		if self.reMainTime > 0.0 and self.reMainTime <= 10.0:
			self.__pyStReTime.text = labelGather.getText( "GameQuiz:main", "stRetime" )%int( self.reMainTime )
			labelGather.setLabel( self.stRemind, "GameQuiz:main", "pleaseAnswer" )
			self.__pyBtnHeart.enable = BigWorld.player().gold >= 30 and not self.isUseHead and not self.__pyAnswerSign.visible
			self.__pyStCountdown.text = str( int( self.reMainTime ) )
		elif self.reMainTime <= 20.0 and self.reMainTime >10.0:
			labelGather.setLabel( self.stRemind, "GameQuiz:main", "pleaseRead" )
			self.__pyBtnHeart.enable = False
			self.__pyStReTime.text = ""
			self.__pyStCountdown.text = str( int( self.reMainTime - 10.0 ) )
		self.stRemind.visible = self.reMainTime > 0.0 and not self.__pyAnswerSign.visible
		for pyLuckStar in self.__pyLuckStars.itervalues():
			pyLuckStar.focus = self.reMainTime <=20.0 and self.reMainTime > 0.0
		if self.reMainTime <= 0.0:
			self.__pyBtnHeart.enable = False
			self.__pyStReTime.text = ""
			self.__cancelRemainTimer()
			if self.alreadyNume >= self.totalNumber: #题目发送完毕且读秒已完，则自动退出答题关闭窗口
				BigWorld.player().quiz_quit()
				self.hide()
		else:
			timeData = Time.time() - self.currentTime - 1.0
			if timeData < 0.0:
				timeData = 0.0
			timeInterval = 1.0 - timeData
			if timeInterval < 0.0:
				timeInterval = 0.0
			self.__cancelRemainTimer()
			self.remainTimerID = Timer.addTimer( timeInterval, 0.0, self.__countDown )
			self.currentTime += 1.0

	def __cancelRemainTimer( self ):
		Timer.cancel( self.remainTimerID )
		self.remainTimerID = 0

	def __onClosed( self ):
		def query( rs_id ):
			if rs_id == RS_OK:
				BigWorld.player().quiz_quit()
				self.hide()
		# "是否确定退出知识问答？"
		showMessage( 0x03a1, "", MB_OK_CANCEL, query )
		return True
	#----------------------------------------------------------
	# public
	# ---------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		"""
		respond base triggering
		"""
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
#		self.endTime = 0
		self.hide()

	def show( self ):
		Window.show( self )

	def hide( self ):
		self.__pyStReTime.text = ""
		self.__pyStReQuest.text = ""
		self.__pyStTaxis.text = ""
		self.__pyStScore.text = 0
		self.__pyStCountdown.text = ""
		self.questID = 0
		Timer.cancel( self.preTimerID )
		self.preTimerID = 0
		Timer.cancel( self.remainTimerID )
		self.reMainTime = TIMER_INTERVAL
		self.remainTimerID = 0
		self.alreadyNume = 0
		self.preTime = 0.0
		self.nextTime = 0.0
		self.currentTime = 0.0
		Timer.cancel( self.nextTimeID )
		self.isAnswered = False
		self.isUseLuckStar = False
		self.isUseHead = False
		self.isSelectAnswer = False
		self.stRemind.visible = False
		self.__pyAnswerSign.visible = False
		for index, pySort in self.__pySortItems.iteritems(): #清空积分排名
			pySort.setSortInfo( index, ( 0, 0 ) )
		for pyLuckStar in self.__pyLuckStars.itervalues():
			pyLuckStar.isUsed = False
			pyLuckStar.enable = True
		self.__pyContPanel.reSetContent()
		Window.hide( self )

# -------------------------------------------------------------------------
from guis.controls.CheckerGroup import CheckerGroup
from guis.controls.CheckBox import CheckBoxEx
from guis.tooluis.CSRichText import CSRichText

class ContentPanel( PyGUI ):
	answer_tags = ["a","b","c","d","e"]
	def __init__( self, panel, pyBinder = None ):
		PyGUI.__init__( self, panel )
		self.__pyTextPanel = CSRichText( panel.rtText )
		self.__pyTextPanel.opGBLink = True
		self.__pyTextPanel.align = "L"
		self.__pyTextPanel.text = ""
		self.__pyTextPanel.foreColor = ( 228, 220, 188, 255 )
		self.pyBinder = pyBinder
		self.questID = -1

		self.__pyCheckGroup = CheckerGroup()
		self.__pyCheckGroup.onCheckChanged.bind( self.__onAnswerSelected )

	def setContent( self, questID, content, answers ):
		self.reSetContent()
		self.questID = questID
		self.__pyTextPanel.text = content
		top = self.__pyTextPanel.bottom + 5.0
		left = self.__pyTextPanel.left + 5.0
		for index, answer in enumerate( answers ):
			ckBox = GUI.load( "guis/general/gamequiz/qachecker.gui" )
			uiFixer.firstLoadFix( ckBox )
			pyQuestCheck = CheckBoxEx( ckBox )
			pyQuestCheck.text = answer
			pyQuestCheck.tag = self.answer_tags[index]
			pyQuestCheck.checked = False
			pyQuestCheck.clickCheck = True
			self.addPyChild( pyQuestCheck )
			top += pyQuestCheck.height + 2.0
			pyQuestCheck.top = top
			pyQuestCheck.left = left
			self.__pyCheckGroup.addChecker( pyQuestCheck )

	def clearCheckers( self ):
		if self.__pyCheckGroup.count > 0:
			for pyChecker in self.__pyCheckGroup.pyCheckers:
				self.delPyChild( pyChecker )
				pyChecker.dispose()
			self.__pyCheckGroup.clearCheckers()

	def setCheckers( self ):
		if self.__pyCheckGroup.count > 0:
			for pyChecker in self.__pyCheckGroup.pyCheckers:
				pyChecker.enable = False

	def __onAnswerSelected( self, checker ):
		"""
		选择答案
		"""
		player = BigWorld.player()
		if checker is None:return
		answer = checker.tag
		scoreRate = 1
		if self.pyBinder.isUseLuckStar:
			scoreRate = 2
		player.quiz_answer( self.questID, answer, scoreRate )
		ECenter.fireEvent( "EVT_ON_QUIZ_SELECT_ANSWER" )

	def onRecAnswer( self, answer ):
		for pyChecker in self.__pyCheckGroup.pyCheckers:
			if pyChecker.tag == answer:
				pyChecker.checked = True
				break

	def setContState( self, reMainTime ):
		"""
		根据剩余时间设置内容
		"""
		if reMainTime <= 0:return
		for pyChecker in self.__pyCheckGroup.pyCheckers:
			pyChecker.enable = reMainTime <= 10.0 and reMainTime > 0.0 and self.__pyCheckGroup.pyCurrChecker is None \
			and not self.pyBinder.isAnswered

	def reSetContent( self ):
		self.__pyTextPanel.text = ""
		self.questID = -1
		self.__pyCheckGroup.clearCheckers()
# ------------------------------------------------------------
from guis.controls.ListItem import MultiColListItem

class SortItem( MultiColListItem ): #排名控件
	def __init__( self, sortItem ):
		MultiColListItem.__init__( self, sortItem )

	def setSortInfo( self, index, tuple ):
		if tuple == ( 0, 0 ): #清空信息
			self.setTextes( "", "", "" )
		else:
			self.setTextes( str( index+1 ), tuple[0], str( tuple[1] ) )
		commonForeColor = ( 255, 255, 255, 255 )
		self.commonForeColor = commonForeColor
		self.highlightForeColor = commonForeColor
		self.selectedForeColor = commonForeColor

class LuckStarBtn( Button ):
	def __init__( self, luckStar ):
		Button.__init__( self, luckStar )
		self.__isUsed = False

	def _getSelected( self ) :
		return self.__isUsed

	def _setSelected( self, isUsed ) :
		if self.__isUsed == isUsed:return
		self.enable = not isUsed
		if not isUsed:
			self.setState( UIState.COMMON )
		else:
			self.setState( UIState.DISABLE )
	isUsed = property( _getSelected, _setSelected )								# 设置选中状态
