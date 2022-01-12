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

TIMER_INTERVAL = 21.0 #ʱ����

PRE_QUEST_TIME = 30.0 #����ǰ����ʱ

class GameQuizWnd( Window ):

	def __init__( self ):
		wnd = GUI.load( "guis/general/gamequiz/window.gui" )
		uiFixer.firstLoadFix( wnd )
		Window.__init__( self, wnd )
		self.posZSegment = ZSegs.L4
		self.activable_ = True
		self.escHide_ 		 = False
		self.__initialize( wnd )
		self.boxTimerID = 0 #ȷ�Ͽ��ʱ
		self.questID = 0 #��ǰ����ID
		self.preTimerID = 0 #׼��ʱ��
		self.preTime = 0.0 #ȷ�Ͽ��ѹ�ʱ��
		self.remainTimerID = 0 #��Ŀ֮���time
		self.endTime = 0
		self.nextTimeID = 0
		self.nextTime = 0.0
		self.reMainTime = TIMER_INTERVAL
		self.alreadyNume = 0 #�ѳ���Ŀ����
		self.isUseLuckStar = False #�Ƿ�ʹ��������
		self.isUseHead = False #�Ƿ�ʹ��"������Ϭ"
		self.isAnswered = False
		self.totalNumber = 0
		self.__triggers = {}
		self.__registerTriggers()
		self.currentTime = 0.0
		self.isSelectAnswer = False #�Ƿ��Ѿ�ѡ����

	def __initialize( self, wnd ):
		labelGather.setPyLabel( self.pyLbTitle_, "GameQuiz:main", "lbTitle" )
		self.pyCloseBtn_.onLClick.bind( self.__onClosed )

		self.__pyBtnHeart = HButtonEx( wnd.btnHeart ) #ʹ��������Ϭ
		self.__pyBtnHeart.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnHeart.enable = False
		self.__pyBtnHeart.onLClick.bind( self.__onUseYourHead )
		self.__pyBtnHeart.onMouseEnter.bind( self.__showHeartTips )
		self.__pyBtnHeart.onMouseLeave.bind( self.__hideHeartTip )
		self.__pyBtnHeart.onLMouseDown.bind( self.__hideHeartTip )
		labelGather.setPyBgLabel( self.__pyBtnHeart, "GameQuiz:main", "btnHeart" )

		self.__pyStReTime = StaticText( wnd.stRetime ) #ʣ��ʱ��
		self.__pyStReTime.text = ""

		self.__pyStReQuest = StaticText( wnd.stRequest ) #ʣ����Ŀ
		self.__pyStReQuest.text = ""

		self.__pyStTaxis = StaticText( wnd.stTaxis ) #����
		self.__pyStTaxis.text = ""

		self.__pyStScore = StaticText( wnd.stScore ) #����
		self.__pyStScore.text = 0

		self.__pyContPanel = ContentPanel( wnd.contPanel, self )

		self.__pyStCountdown = StaticText( wnd.stCountdown ) #���뵹��ʱʮλ��
		self.__pyStCountdown.text = ""
		self.__pyStCountdown.fontSize = 30
		self.__pyStCountdown.limning = Font.LIMN_OUT
		self.__pyStCountdown.color = 255, 240, 222

		self.stRemind = wnd.stRemind

		self.__pyAnswerSign = PyGUI( wnd.answerSign ) #�ǶԻ��Ǵ�
		self.__pyAnswerSign.visible = False

		self.__pySortItems = {}
		self.__pyLuckStars = {}
		for name, item in wnd.children: #�����ؼ�
			if name.startswith( "sortItem_" ):
				index = int( name.split( "_" )[1] )
				pySortItem = SortItem( item )
				pySortItem.setTextes( "", "", "" )
				self.__pySortItems[index] = pySortItem

			if name.startswith( "star_" ): #������
				index = int( name.split( "_" )[1] )
				pyLuckStar = LuckStarBtn( item )
				pyLuckStar.isUsed = False #�Ƿ��Ѿ�ʹ��
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
		self.__triggers["EVT_ON_QUIZ_INVITE_JOIN"] = self.__onInviteJoin #�������
		self.__triggers["EVT_ON_QUIZ_ENTER_STATE"] =  self.__onEnterQuiz #�������
		self.__triggers["EVT_ON_QUIZ_RECEIVE_QUESTIONS"] = self.__onRecQuests #��������
		self.__triggers["EVT_ON_QUIZ_RECEIVE_ANSWER"] = self.__onRecAnswer #������ȷ��
		self.__triggers["EVT_ON_QUIZ_RECEIVE_TOPS"] = self.__onRecTops #��������
		self.__triggers["EVT_ON_QUIZ_SCORE_CHANGE"] = self.__onScoreChange #���ָı�
		self.__triggers["EVT_ON_QUIZ_ANSWER_STATE"]	= self.__onAnswerState #�Դ�
		self.__triggers["EVT_ON_ROLE_GOLD_CHANGED"] = self.__onGoldChanged 	#��Ԫ�����������仯
		self.__triggers["EVT_ON_QUIZ_TOTAL_NUMBER"] = self.__onRecTotalNum #��Ŀ����
		self.__triggers["EVT_ON_QUIZ_USE_LUCKSTAR"] = self.__onLuckStarUsed #ʹ��������
		self.__triggers["EVT_ON_QUIZ_ON_ENTER_INVITE_JOIN"] = self.__onEnterInviteJoin # ��¼֪ʶ�ʴ�����������
		self.__triggers["EVT_ON_QUIZ_SELECT_ANSWER"] = self.__onSelectAnswer #ѡ����

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
		����μ�
		"""
		player = BigWorld.player()
		if not rds.statusMgr.isInWorld():return
		self.boxTimerID = Timer.addTimer( 0, 1, self.__boxCountdown ) #����ȷ�Ͽ򵹼�ʱ
		if player.getCurrentSpaceType() == csdefine.SPACE_TYPE_NORMAL:
			# "���ô��������Ǳ����֪ʶ���������Ȥ������ȷ������ɡ�"
			askString = 0x03a2
		else:
			# "�Ƿ���Ҫ���ͻظ������д��⣿"
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
		�յ�½������μ�
		"""
		player = BigWorld.player()
		if not rds.statusMgr.isInWorld():return
		if player.getCurrentSpaceType() == csdefine.SPACE_TYPE_NORMAL:
			# "֪ʶ�������ڽ��У����Ƿ�μӻ��"
			askString = 0x03a4
		else:
			# "֪ʶ�������ڽ��У��Ƿ���Ҫ���ͻظ������д��⣿"
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
		�������
		"""
		if self.visible:return
		else:self.show()
		startTime = BigWorld.player().quizGameStartTime
		if startTime > 0.0: #��;���ߴ���
			alreadyTime = Time.time() - startTime #�Ѿ���ʼ����ʱ��
			if alreadyTime < 30.0: #���ڴ���ǰ����ʱ
				self.preEndTime = Time.time() +( PRE_QUEST_TIME - alreadyTime )
				self.preTimerID = Timer.addTimer( 0, 1, self.__preCountdown )
			else: #�Ѿ���ʼ���⣬�ȴ���һ�⿪ʼ
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
		��Ŀ������֮ǰ�ĵ���ʱ
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
		��������
		"""
		self.alreadyNume += 1
		if self.isUseHead:
			self.isUseHead = False #��������Ԫ������״̬
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

	def __onRecAnswer( self, questID, questAnswer ): #ʹ��Ԫ���������ȷ�Ĵ�
		if questID != self.questID:return
		self.__pyContPanel.onRecAnswer( questAnswer )
		self.isAnswered = True
		self.__pyAnswerSign.visible = True
		util.setGuiState( self.__pyAnswerSign.getGui(), ( 1, 2 ), ( 1, 1 ) )

	def __onRecTops( self, roleList, scoreList, playerOrder ): #��������
		for index, pySort in self.__pySortItems.iteritems(): #��ջ�������
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
		���ذ�ť������ʾ
		"""
		toolbox.infoTip.hide()

	def __onRecTotalNum( self, totalNum ):
		self.totalNumber = totalNum

	def __onScoreChange( self, score ):
		"""
		��һ��ָı�,˵���ش���ȷ
		"""
		self.__pyStScore.text = str( score )

	def __onAnswerState( self, questID, answerState ):
		if questID != self.questID :return
		if answerState: #���
			util.setGuiState( self.__pyAnswerSign.getGui(), ( 1, 2 ), ( 1, 1 ) )
		else: #���
			util.setGuiState( self.__pyAnswerSign.getGui(), ( 1, 2 ), ( 1, 2 ) )
		self.__pyContPanel.setCheckers() #���ܶԴ�ѡ�����ѡ
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
		ʹ��������Ϭ
		"""
		scoreRate = 1
		if self.isUseLuckStar:
			scoreRate = 2
		BigWorld.player().quiz_useGold( self.questID, scoreRate )
		self.isUseHead = True
		self.__pyBtnHeart.enable = False

	def __onUseLuckStar( self, pyLuckStar ):
		"""
		ʹ��������
		"""
		if self.isUseLuckStar: return
		if self.isSelectAnswer: return
		pyLuckStar.isUsed = True
		index = pyLuckStar.index
		ECenter.fireEvent( "EVT_ON_QUIZ_USE_LUCKSTAR", index )

	def __onSelectAnswer( self ):
		"""
		ѡ����
		"""
		self.isSelectAnswer = True

	def __countDown( self ):
		"""
		���뵹��ʱ,�ڵ���10-20���ڲ��ô��⣬0-10���ô��⣬������Ҫ��Ӧ����
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
			if self.alreadyNume >= self.totalNumber: #��Ŀ��������Ҷ������꣬���Զ��˳�����رմ���
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
		# "�Ƿ�ȷ���˳�֪ʶ�ʴ�"
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
		for index, pySort in self.__pySortItems.iteritems(): #��ջ�������
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
		ѡ���
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
		����ʣ��ʱ����������
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

class SortItem( MultiColListItem ): #�����ؼ�
	def __init__( self, sortItem ):
		MultiColListItem.__init__( self, sortItem )

	def setSortInfo( self, index, tuple ):
		if tuple == ( 0, 0 ): #�����Ϣ
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
	isUsed = property( _getSelected, _setSelected )								# ����ѡ��״̬
