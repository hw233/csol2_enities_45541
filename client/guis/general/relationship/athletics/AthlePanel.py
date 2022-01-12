# -*- coding: gb18030 -*-
#
# $Id: SysSetting.py, fangpengjun Exp $

"""
implement KeySetting window class
"""
from guis import *
from guis.common.Window import Window
from guis.controls.TabCtrl import TabCtrl
from guis.controls.TabCtrl import TabButton
from guis.controls.TabCtrl import TabPanel
from guis.controls.TabCtrl import TabPage
from guis.tooluis.CSRichText import CSRichText
import ActivitySchedule
ActivityInstance = ActivitySchedule.g_activitySchedule
from MatchPanel import MatchPanel
from RecrtOKCancelBox import RecrtOKCancelBox
from LabelGather import labelGather
import csstring
import csdefine
import csconst
from Time import Time
from Function import Functor
from config.client.msgboxtexts import Datas as mbmsgs

indexMap = {4:csdefine.MATCH_TYPE_PERSON_ABA,				# 武道大会
				5:csdefine.MATCH_TYPE_TEAM_ABA,				# 组队擂台
				6:csdefine.MATCH_TYPE_TONG_ABA,				# 帮会擂台
				2:csdefine.MATCH_TYPE_TEAM_COMPETITION,		# 队伍竞技
				3:csdefine.MATCH_TYPE_TONG_COMPETITION,		# 帮会竞技
				1:csdefine.MATCH_TYPE_PERSON_COMPETITION,	# 个人竞技
			
			}

class AthlePanel( TabPanel, TabCtrl ):
	
	def __init__( self, panel, pyBinder = None ):
		TabPanel.__init__( self, panel )
		TabCtrl.__init__( self, panel )
		self.isInited = False	#是否为第一次请求数据
		self.__triggers = {}
		self.__registerTriggers()
		self.__initialize( panel )
		self.__synTimeCBID = 0		#同步时间
		self.__pyRecrtBox = None
	
	def __initialize( self, panel ):
		index = 1
		while True :											#初始化TabCtrl
			tabName = "btn_" + str( index )
			tab = getattr( panel, tabName, None )
			if tab is None : break
			panelName = "panel_" + str( index )
			tabpanel = getattr( panel, panelName, None )
			if tabpanel is None : break
			pyBtn = BorderBtn( tab )
			pyBtn.setStatesMapping( UIState.MODE_R1C3 )
			pyBtn.text = labelGather.getText( "RelationShip:AthlePanel", tabName )
			pyPanel = MatchPanel( tabpanel, indexMap[index] )
			pyPage = TabPage( pyBtn, pyPanel )
			self.addPage( pyPage )
			index += 1
		self.onTabPageSelectedChanged.bind( self.__onTabSelectChanged )
		self.pySelPage = self.pyPages[5]

	# ----------------------------------------------------------------
	# events
	# ----------------------------------------------------------------
	def generateEvents_( self ) :
		"""
		产生事件
		"""
		TabCtrl.generateEvents_( self )
		self.__onTabPageSelectedChanged = self.createEvent_( "onTabPageSelectedChanged" )		# 当选页改变时被触发
	
	def __registerTriggers( self ):
		self.__triggers["EVT_ON_INIITE_MATCH_RECORD"] = self.__onIniteRecord
		self.__triggers["EVT_ON_UPDATE_MATCH_RECORD"] = self.__onUpdateRecord
		self.__triggers["EVT_ON_COMPET_LEVEL_STEPS_CHANGE"] = self.__onLevelStepChange
		self.__triggers["EVT_ON_COMPET_RESULT_CHANGE"] = self.__onCompResultChange
		self.__triggers["EVT_ON_COMPET_GATHER_TRIGGER"] = self.__onGatherTrigger
		self.__triggers["EVT_ON_TEAM_CHALLENGE_ON_RECRUIT"] = self.__onTeamChallengeRecruit
		self.__triggers["EVT_ON_TEAM_CHALLENGE_ON_RECRUIT_COMPLETE"] = self.__onTeamRecruitCompelete
		self.__triggers["EVT_ON_TEAM_CHALLENGE_ON_RECRUIT_CANCEL"] = self.__onTeamRecruitCompelete
		self.__triggers["EVT_ON_TEAM_CHALLENGE_TEAM_BE_RECRUIT"] = self.__onTeamChallengeBeRecruit
		self.__triggers["EVT_ON_TEAM_CHALLENGE_TEAM_RECRUIT_SUCCESS"] = self.__onTeamChallengeRecruitSuss
		
		for key in self.__triggers :
			ECenter.registerEvent( key, self )

	def __deregisterTriggers( self ) :
		for key in self.__triggers :
			GUIFacade.unregisterEvent( key, self )
			
	# ------------------------------------------------------------
	def __onTabSelectChanged( self, pyCtrl ):
		"""
		分页选择
		"""
		pySelPage = pyCtrl.pySelPage
		if pySelPage is None:return
		selIndex = pySelPage.index
		matchPanel = pySelPage.pyPanel
		matchName = pySelPage.pyBtn.text
		if matchPanel.matchType == csdefine.MATCH_TYPE_TONG_ABA:
			matchName += "赛"
		for pySelPage in pyCtrl.pyPages:
			pyPanel = pySelPage.pyPanel
			if pyPanel.matchType == matchPanel.matchType:
				pyPanel.setGatherState()
				times = self.__getMatchTimes( matchName )
				if times is None:return
				if times[0] > 0:
					pyPanel.setRemainTime( times )
				else:
					BigWorld.cancelCallback( self.__synTimeCBID )
					self.__synTimeCBID = BigWorld.callback( 0, Functor( self.__setRemainTime, pyPanel, times ) )
			else:
				pyPanel.cancelCountdown()
	
	def __setRemainTime( self, pyPanel, times ):
		if pyPanel is None:return
		pyPanel.setRemainTime( times )
		self.__synTimeCBID = BigWorld.callback( 30, Functor( self.__setRemainTime, pyPanel, times ) )
		
	def __onIniteRecord( self, matchType, param1, param2 ):
		"""
		初始化比赛记录
		"""
		self.isInited = True
		for pyPage in self.pyPages:
			matchPanel = pyPage.pyPanel
			if matchPanel.matchType == matchType:
				matchPanel.initeRecord( param1, param2 )
	
	def __onUpdateRecord( self, matchType, param ):
		"""
		更新比赛信息
		"""
		for pyPage in self.pyPages:
			matchPanel = pyPage.pyPanel
			if matchPanel.matchType == matchType:
				matchPanel.updateRecord( param )
	
	def __onLevelStepChange( self, matchType, levelStep ):
		"""
		等级段改变
		"""
		for pyPage in self.pyPages:
			matchPanel = pyPage.pyPanel
			if matchPanel.matchType == matchType:
				matchPanel.onLevelStepChange( levelStep )

	def __onCompResultChange( self, matchType, result ):
		"""
		赛段级别改变
		"""
		for pyPage in self.pyPages:
			matchPanel = pyPage.pyPanel
			if matchPanel.matchType == matchType:
				matchPanel.onResultChange( result )
	
	def __onGatherTrigger( self, matchType ):
		"""
		触发集合信息
		"""
		for pyPage in self.pyPages:
			matchPanel = pyPage.pyPanel
			if matchPanel.matchType == matchType:
				matchPanel.onGatherTrigger()
	
	def __onTeamChallengeRecruit( self ):
		"""
		队伍招募
		"""
		for pyPage in self.pyPages:
			matchPanel = pyPage.pyPanel
			if matchPanel.matchType == csdefine.MATCH_TYPE_TEAM_ABA:
				matchPanel.onTeamChallengeRecruit()
	
	def __onTeamRecruitCompelete( self ):
		"""
		招募完成
		"""
		for pyPage in self.pyPages:
			matchPanel = pyPage.pyPanel
			if matchPanel.matchType == csdefine.MATCH_TYPE_TEAM_ABA:
				matchPanel.onTeamRecruitCompelete()
	
	def __onTeamChallengeBeRecruit( self, teamID ):
		player = BigWorld.player()
		if self.__pyRecrtBox:
			self.__pyRecrtBox.hide()
			self.__pyRecrtBox = None
		def onResult( id ):
			if id == RS_OK:
				player.cell.challengeTeamRecruitResult( teamID, True )
			else:
				player.cell.challengeTeamRecruitResult( teamID, False )
		self.__pyRecrtBox = RecrtOKCancelBox()
		self.__pyRecrtBox.show( 30, mbmsgs[ 0x0eea ], "", onResult, pyOwner = self )
	
	def __onTeamChallengeRecruitSuss( self ):
		if self.__pyRecrtBox:
			self.__pyRecrtBox.hide( True )
			self.__pyRecrtBox = None
	
	def onUpdateLevel( self, oldLevel, level ) :
		for pyPage in self.pyPages:
			matchPanel = pyPage.pyPanel
			matchType = matchPanel.matchType
			if matchType == csdefine.MATCH_TYPE_TONG_ABA: #帮会擂台55级以上可以打开界面
				pyPage.enable = level >= 55
			else:
				pyPage.enable = level >= 60
	
	def __getMatchTimes( self, matchName ):
		"""
		通过比赛名称，获取比赛开始、结束时间
		"""
		minsDay = 0 #相差天数
		while minsDay <= 6:
			actTables = {}
			if minsDay == 0:
				actTables = ActivityInstance._todayActivityTable
			else:
				actTables = ActivityInstance.getDayActivityTable( minsDay )
			for actTable in actTables.values():
				if actTable[2] == matchName and actTable[3] == 1:
					startHour = actTable[0] #活动开始小时
					startMins = actTable[1] #开始分钟
					duraTime = actTable[10] #持续时间
					return [minsDay, startHour, startMins, duraTime]
			minsDay += 1
	# ---------------------------------------------------------------
	# public
	# ---------------------------------------------------------------
	def onEvent( self, macroName, *args ) :
		self.__triggers[macroName]( *args )
	
	def onShow( self ):
		TabPanel.onShow( self )
		pLevel = BigWorld.player().getLevel()
		if pLevel < 60:
			self.pySelPage = self.pyPages[5]
		else:
			self.pySelPage = self.pyPages[0]
		self.__onTabSelectChanged( self )
		for pySelPage in self.pyPages:
			matchPanel = pySelPage.pyPanel
			matchType = matchPanel.matchType
			if matchType == csdefine.MATCH_TYPE_TONG_ABA: #帮会擂台55级以上可以打开界面
				pySelPage.enable = pLevel >= 55
			else:
				pySelPage.enable = pLevel >= 60
			pyPanel = pySelPage.pyPanel
			pyPanel.setIniteInfos()
		
	def onHide( self ) :
		TabPanel.onHide( self )
	
	def cancelTimer( self ):
		for pyPage in self.pyPages:
			matchPanel = pyPage.pyPanel
			matchPanel.cancelCountdown()
		BigWorld.cancelCallback( self.__synTimeCBID )
	
	def reset( self ):
		for pyPage in self.pyPages:
			matchPanel = pyPage.pyPanel
			if matchPanel.matchType == csdefine.MATCH_TYPE_TEAM_ABA:
				matchPanel.reset()
		BigWorld.cancelCallback( self.__synTimeCBID )

# ------------------------------------------------------------------
class BorderBtn( TabButton ):
	def __init__( self, borderBtn ):
		TabButton.__init__( self, borderBtn )
		self.__pyRich = CSRichText( borderBtn.rtText)
		self.__pyRich.maxWidth = 20.0
		self.__pyRich.spacing = -1
		self.__pyRich.foreColor = ( 255,227,184,255 )
		
	def onStateChanged_( self, state ):
		TabButton.onStateChanged_( self, state )
		if state == UIState.SELECTED:
			self.__pyRich.foreColor = ( 142, 216, 217, 255 )
		else:
			self.__pyRich.foreColor = ( 255,227,184,255 )

	def _getText( self ):
		return self.__pyRich.text

	def _setText( self, text ):
		textLen = len( csstring.toWideString( text ) )
		if textLen >= 4:
			self.__pyRich.spacing = -2.0
		else:
			self.__pyRich.spacing = 4.0
		self.__pyRich.text = text

	text = property( _getText, _setText )