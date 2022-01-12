# -*- coding: gb18030 -*-
#
# $Id: SysSetting.py, fangpengjun Exp $

"""
implement KeySetting window class
"""
from guis import *
from guis.common.PyGUI import PyGUI
from guis.controls.TabCtrl import TabPanel
from guis.controls.ButtonEx import HButtonEx
from guis.controls.ItemsPanel import ItemsPanel
from guis.tooluis.CSRichText import CSRichText
from LabelGather import labelGather
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.tooluis.richtext_plugins.PL_NewLine import PL_NewLine
import csdefine
import datetime
import time
from Time import Time

INTEL_MATCHS = [csdefine.MATCH_TYPE_PERSON_COMPETITION, csdefine.MATCH_TYPE_TEAM_COMPETITION, csdefine.MATCH_TYPE_TONG_COMPETITION]

class MatchPanel( TabPanel ):
	
	
	def __init__( self, panel, matchType ):
		TabPanel.__init__( self, panel )
		self.matchType = matchType
		self.__itemsPanel = ItemsPanel( panel.clipPanel, panel.sbar )
		self.__itemsPanel.colSpace = 2.0
		self.__pyTimePanel = TimePanel( self )
		self.__pyInfoPanel = InfosPanel( self )
		self.__itemsPanel.addItems( [self.__pyTimePanel,self.__pyInfoPanel] )
		self.__isInited = False
		self.param2 = 0
	
	def initeRecord( self, param1, param2 ):
		"""
		个人竞技，组队竞技，帮会竞技：
		上次参赛获得积分INT32：param1
		累计参赛获得积分INT32：param2
		
		武道大会，组队擂台，帮会擂台:
		上次参赛获得名次INT32：param1
		获得最好参赛名次INT32：param2
		"""
		records = []
		self.__isInited = True
		self.param2 = param2
		player = BigWorld.player()
		if self.matchType in INTEL_MATCHS: #属于竞技类,更新上次积分，累计积分
			lastIntel = labelGather.getText( "RelationShip:AthlePanel","lastInteg" )%param1
			totalIntel = labelGather.getText( "RelationShip:AthlePanel","totalInteg" )%self.param2
			currPoint = 0
			if self.matchType == csdefine.MATCH_TYPE_PERSON_COMPETITION:
				currPoint = player.personalScore
			elif self.matchType == csdefine.MATCH_TYPE_TEAM_COMPETITION:
				currPoint = player.teamCompetitionPoint
			else:
				currPoint = player.tongCompetitionScore
			curUseInteg = labelGather.getText( "RelationShip:AthlePanel","curUseInteg" )%str( currPoint ) #当前可用积分
			records = [lastIntel, totalIntel, curUseInteg]
		else: #擂台类，上次参赛名次，最好名次，当前情况
			if param1 == csdefine.MATCH_LEVEL_NONE:
				lastInfo = "N/A"
			elif param1 == csdefine.MATCH_LEVEL_FINAL:
				lastInfo = labelGather.getText( "RelationShip:AthlePanel","finals" )
			elif param1 == csdefine.MATCH_LEVEL_SEMIFINALS:
				lastInfo = labelGather.getText( "RelationShip:AthlePanel","semifinal" )
			else:
				rank = pow( 2, param1 -1 )
				lastInfo = labelGather.getText( "RelationShip:AthlePanel","ranks" )%str( rank )
			lastRank = labelGather.getText( "RelationShip:AthlePanel","lastRank" )%lastInfo
			if param2 == csdefine.MATCH_LEVEL_NONE:
				bestInfo = "N/A"
			elif param2 == csdefine.MATCH_LEVEL_FINAL:
				bestInfo = labelGather.getText( "RelationShip:AthlePanel","finals" )
			elif param2 == csdefine.MATCH_LEVEL_SEMIFINALS:
				bestInfo = labelGather.getText( "RelationShip:AthlePanel","semifinal" )
			else:
				rank = pow( 2, param2 -1 )
				bestInfo = labelGather.getText( "RelationShip:AthlePanel","ranks" )%str( rank )
			bestRank = labelGather.getText( "RelationShip:AthlePanel","bestRank" )%bestInfo
			rankText = ""
			curRank = player.matchResults.get( self.matchType,0 )
			if curRank == csdefine.MATCH_LEVEL_NONE:
				rankText = "N/A"
			elif curRank == csdefine.MATCH_LEVEL_FINAL:
				rankText = labelGather.getText( "RelationShip:AthlePanel","finals" )
			elif curRank == csdefine.MATCH_LEVEL_SEMIFINALS:
				rankText = labelGather.getText( "RelationShip:AthlePanel","semifinal" )
			else:
				rank = pow( 2, curRank -1 )
				rankText = labelGather.getText( "RelationShip:AthlePanel","ranks" )%rank
			rankInfo = labelGather.getText( "RelationShip:AthlePanel","curComState" )%rankText
			records = [lastRank, bestRank, rankInfo]
		self.__pyInfoPanel.updateRecord( records )
	
	def updateRecord( self, param ):
		"""
		个人竞技，组队竞技，帮会竞技：
		上次参赛获得积分INT32：param
		
		武道大会，组队擂台，帮会擂台:
		上次参赛获得名次INT32：param
		"""
		records = []
		player = BigWorld.player()
		if self.matchType in INTEL_MATCHS:
			self.param2 += param
			lastIntel = labelGather.getText( "RelationShip:AthlePanel","lastInteg" )%str( param )
			totalIntel = labelGather.getText( "RelationShip:AthlePanel","totalInteg" )%str( self.param2 )
			currPoint = 0
			if self.matchType == csdefine.MATCH_TYPE_PERSON_COMPETITION:
				currPoint = player.personalScore
			elif self.matchType == csdefine.MATCH_TYPE_TEAM_COMPETITION:
				currPoint = player.teamCompetitionPoint
			else:
				currPoint = player.tongCompetitionScore
			curUseInteg = labelGather.getText( "RelationShip:AthlePanel","curUseInteg" )%str( currPoint )
			records = [lastIntel,totalIntel,curUseInteg]
		else:
			if self.param2 > param and param != 0:
				self.param2 = param
			if param == csdefine.MATCH_LEVEL_NONE:
				lastInfo = "N/A"
			elif param == csdefine.MATCH_LEVEL_FINAL:
				lastInfo = labelGather.getText( "RelationShip:AthlePanel","finals" )
			elif param == csdefine.MATCH_LEVEL_SEMIFINALS:
				lastInfo = labelGather.getText( "RelationShip:AthlePanel","semifinal" )
			else:
				rank = pow( 2, param -1 )
				lastInfo = labelGather.getText( "RelationShip:AthlePanel","ranks" )%str( rank )
			lastRank = labelGather.getText( "RelationShip:AthlePanel","lastRank" )%lastInfo
			if self.param2 == csdefine.MATCH_LEVEL_NONE:
				bestInfo = "N/A"
			elif self.param2 == csdefine.MATCH_LEVEL_FINAL:
				bestInfo = labelGather.getText( "RelationShip:AthlePanel","finals" )
			elif self.param2 == csdefine.MATCH_LEVEL_SEMIFINALS:
				bestInfo = labelGather.getText( "RelationShip:AthlePanel","semifinal" )
			else:
				rank = pow( 2, self.param2 -1 )
				bestInfo = labelGather.getText( "RelationShip:AthlePanel","ranks" )%str( rank )
			bestRank = labelGather.getText( "RelationShip:AthlePanel","bestRank" )%bestInfo
			records = [lastRank, bestRank]
		self.__pyInfoPanel.updateRecord( records )
	
	def onLevelStepChange( self, levelStep ):
		"""
		比赛等级段改变
		"""
		minLevel = levelStep[0]
		maxLevel = levelStep[1]
		levels = "%d--%d"%( minLevel, maxLevel )
		curStep = labelGather.getText( "RelationShip:AthlePanel","levelStep" )%levels
		self.__pyInfoPanel.setStepInfo( curStep )
	
	def onResultChange( self, rank ):
		"""
		比赛结果改变
		"""
		self.__pyInfoPanel.onResultChange( rank )
	
	def setRemainTime( self, times ):
		"""
		剩余时间改变
		"""
		severTime = Time.localtime()
		sHour = severTime[3]
		sMinus = severTime[4]
		sSecond = severTime[5]
		
		minsDay = times[0]
		hour = times[1]
		minus = times[2]
		
		remainTime = ( hour - sHour  ) * 3600 + ( minus - sMinus ) * 60 - sSecond + minsDay * 24 * 3600
		if self.matchType == csdefine.MATCH_TYPE_TEAM_COMPETITION:
			remainTime += 5*60
		elif self.matchType == csdefine.MATCH_TYPE_TONG_ABA:
			remainTime += 15*60
		elif self.matchType == csdefine.MATCH_TYPE_TONG_COMPETITION:
			remainTime += 60*60
		elif self.matchType in [csdefine.MATCH_TYPE_TEAM_ABA, csdefine.MATCH_TYPE_PERSON_ABA]:#提示60分钟后报名 
			remainTime += 75*60

		if remainTime < 0:
			minsDay -= 1
		
		self.__pyTimePanel.setRemainTime( minsDay, remainTime )
	
	def onGatherTrigger( self ):
		self.__pyTimePanel.onGatherTrigger()

	def setIniteInfos( self ):
		"""
		初始化信息
		"""
		self.__pyInfoPanel.setIniteInfos( self.matchType )

	def onHide( self ) :
		"""
		版面隐藏时被调用
		"""
		TabPanel.onHide( self )
		self.__pyTimePanel.cancelCountdown()
	
	def cancelCountdown( self ):
		self.__pyTimePanel.cancelCountdown()
	
	def setGatherState( self ):
		"""
		设置集合按钮状态
		"""
		self.__pyTimePanel.setGatherState( self.matchType )
	
	def onTeamChallengeRecruit( self ):
		"""
		队伍招募
		"""
		self.__pyInfoPanel.onTeamChallengeRecruit()
	
	def onTeamRecruitCompelete( self ):
		"""
		招募完成
		"""
		self.__pyInfoPanel.onTeamRecruitCompelete()
	
	def reset( self ):
		self.__pyInfoPanel.reset()
	
# -------------------------------------------------------------------
import Timer
class TimePanel( PyGUI ):
	
	def __init__( self, pyBinder ):
		panel = GUI.load( "guis/general/relationwindow/athlepanel/timepanel.gui" )
		uiFixer.firstLoadFix( panel )
		PyGUI.__init__( self, panel )
		self.pyBinder = pyBinder
		self.__pyRtTime = CSRichText( panel.rtTime )
		self.__pyRtTime.align = "C"
		self.__pyRtTime.text = ""
		self.__pyBtnApply = HButtonEx( panel.btnApply )
		self.__pyBtnApply.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnApply, "RelationShip:AthlePanel", "apply" )
		self.__pyBtnApply.onLClick.bind( self.__onApply )
		
		self.__pyBtnGather = HButtonEx( panel.btnGather )
		labelGather.setPyBgLabel( self.__pyBtnGather, "RelationShip:AthlePanel", "gather" )
		self.__pyBtnGather.visible = False
		self.__pyBtnGather.setExStatesMapping( UIState.MODE_R4C1 )
		self.__pyBtnGather.onLClick.bind( self.__onGather )
		
		
		self.remTimes = {csdefine.MATCH_TYPE_PERSON_COMPETITION:[0, 0], #callbackid，remaintime
					csdefine.MATCH_TYPE_TEAM_COMPETITION:[0, 0],
					csdefine.MATCH_TYPE_TONG_COMPETITION:[0, 0],
					csdefine.MATCH_TYPE_PERSON_ABA:[0, 0],
					csdefine.MATCH_TYPE_TEAM_ABA:[0, 0],
					csdefine.MATCH_TYPE_TONG_ABA:[0, 0],
				}
		
	def __onApply( self, pyBtn ):
		"""
		报名
		"""
		matchType = self.pyBinder.matchType
		player = BigWorld.player()
		applies = { csdefine.MATCH_TYPE_PERSON_COMPETITION: player.roleCompetitionSignUp,
				csdefine.MATCH_TYPE_TEAM_COMPETITION: player.teamCompetitionSignUp,
				csdefine.MATCH_TYPE_TONG_COMPETITION: player.tongCompetitionSignUp,
				csdefine.MATCH_TYPE_PERSON_ABA: player.wuDaoSignUp,
				csdefine.MATCH_TYPE_TEAM_ABA: player.challengeTeamSignUp,
				csdefine.MATCH_TYPE_TONG_ABA: player.tongAbaSignUp
				}
		applyFunc = applies.get( matchType, None )
		if applyFunc is None:return
		applyFunc()
	
	def __onGather( self, pyBtn ):
		"""
		集合
		"""
		matchType = self.pyBinder.matchType
		player = BigWorld.player()
		gathers = { csdefine.MATCH_TYPE_PERSON_COMPETITION: player.cell.roleCompetitionGather,
				csdefine.MATCH_TYPE_TEAM_COMPETITION: player.cell.teamCompetitionGather,
				csdefine.MATCH_TYPE_TONG_COMPETITION: player.cell.tongCompetitionGather,
				csdefine.MATCH_TYPE_PERSON_ABA: player.cell.wuDaoGather,
				csdefine.MATCH_TYPE_TEAM_ABA: player.cell.teamChallengeGather,
				csdefine.MATCH_TYPE_TONG_ABA: player.cell.tongAbaGather
				}
		gatherFunc = gathers.get( matchType, None )
		if gatherFunc is None:return
		gatherFunc()
	
	def setRemainTime( self, minsday, remaintime ):
		"""
		设置倒计时
		"""
		matchType = self.pyBinder.matchType
		Timer.cancel( self.remTimes[matchType][0] )
		self.remTimes[matchType][0] = 0
		if minsday <=0:
			self.remTimes[matchType][1] = remaintime
			self.remTimes[matchType][0] = Timer.addTimer( 0, 1, self.__countdownBySecd )
		else:
			self.remTimes[matchType][1] = remaintime/60
			self.remTimes[matchType][0] = Timer.addTimer( 0, 60, self.__countdownByMinus )
			
	def __countdownBySecd( self ):
		"""
		按秒倒计时
		"""
		matchType = self.pyBinder.matchType
		remainTime = self.remTimes[matchType][1]
		if remainTime > 5*60: #报名时间
			if not self.__pyBtnGather.visible:
				self.__pyBtnApply.visible = True
			if matchType in [csdefine.MATCH_TYPE_TEAM_COMPETITION, csdefine.MATCH_TYPE_TONG_COMPETITION]: #组队竞技
				self.__pyBtnApply.enable = remainTime <= 60*60
				if remainTime > 60*60:
					remainTime -= 60*60
					hours, minus, secs = self.__getTimeBySecs( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupStartBySecs" )%( hours, minus, secs )
				else:
					hours, minus, secs = self.__getTimeBySecs( remainTime - 60*5 )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupEndBySecs" )%( hours, minus, secs )
			elif matchType == csdefine.MATCH_TYPE_PERSON_COMPETITION: #个人竞技
				self.__pyBtnApply.enable = remainTime <= 60*62
				if remainTime > 60*62:
					remainTime -= 60*62
					hours, minus, secs = self.__getTimeBySecs( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupStartBySecs" )%( hours, minus, secs )
				elif remainTime < 60 * 7 and remainTime > 60 * 5:
					hours, minus, secs = self.__getTimeBySecs( 0 )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupStartBySecs" )%( hours, minus, secs )
				else:
					hours, minus, secs = self.__getTimeBySecs( remainTime - 60*7 )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupEndBySecs" )%( hours, minus, secs )
			elif matchType == csdefine.MATCH_TYPE_TONG_ABA: #帮会擂台
				self.__pyBtnApply.enable = remainTime <= 15*60
				if remainTime > 60*15:
					remainTime -= 60*15
					hours, minus, secs = self.__getTimeBySecs( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupStartBySecs" )%( hours, minus, secs )
				else:
					hours, minus, secs = self.__getTimeBySecs( remainTime - 60*5 )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupEndBySecs" )%( hours, minus, secs )
			else: #武道大会、组队擂台
				self.__pyBtnApply.enable = remainTime <= 15*60
				if remainTime > 60*15:
					remainTime -= 60*15
					hours, minus, secs = self.__getTimeBySecs( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupStartBySecs" )%( hours, minus, secs )
				else:
					hours, minus, secs = self.__getTimeBySecs( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupEndBySecs" )%( hours, minus, secs )
		elif remainTime <= 5*60 and remainTime > 0: #5分钟集合时间
			hours, minus, secs = self.__getTimeBySecs( remainTime )
			if not matchType in [csdefine.MATCH_TYPE_TEAM_ABA, csdefine.MATCH_TYPE_PERSON_ABA]:
				self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "enterbySecs" )%( hours, minus, secs )
				if self.__pyBtnGather.visible:
					self.__pyBtnApply.visible = False
			else:
				self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupEndBySecs" )%( hours, minus, secs )
		else:
			if matchType in [csdefine.MATCH_TYPE_TEAM_ABA, csdefine.MATCH_TYPE_PERSON_ABA]: #武道大会和组队擂台是开始比赛就集合
				remainTime += 2*60
				if remainTime > 0:
					hours, minus, secs = self.__getTimeBySecs( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "enterbySecs" )%( hours, minus, secs )
					if self.__pyBtnGather.visible:
						self.__pyBtnApply.visible = False
				else:
					self.__setCancelTime( matchType )
			else:
				self.__setCancelTime( matchType )
		self.remTimes[matchType][1] -= 1
	
	def __countdownByMinus( self ):
		"""
		按分倒计时
		"""
		matchType = self.pyBinder.matchType
		remainTime = self.remTimes[matchType][1]
		if remainTime > 5: #报名时间
			self.__pyBtnApply.enable = remainTime <= 60
			if not self.__pyBtnGather.visible:
				self.__pyBtnApply.visible = True
			if matchType in INTEL_MATCHS:
				if remainTime > 60:
					remainTime -= 60
					days, hours, minus = self.__getTimeByMinus( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupStartByMinus" )%( days, hours, minus)
				else:
					days, hours, minus = self.__getTimeByMinus( remainTime - 5 )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupEndByMinus" )%( days, hours, minus)
			else:
				self.__pyBtnApply.enable = remainTime <= 15
				if remainTime > 15:
					remainTime -= 15
					days, hours, minus = self.__getTimeByMinus( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupStartByMinus" )%( days, hours, minus)
				else:
					days, hours, minus = self.__getTimeByMinus( remainTime - 5 )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupEndByMinus" )%( days, hours, minus)
		elif remainTime <= 5 and remainTime > 0:
			self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "enterbyMinus" )%( days, hours, minus)
			if self.__pyBtnGather.visible:
				self.__pyBtnApply.visible = False
		else:
			self.__setCancelTime( matchType )
		self.remTimes[matchType][1] -= 1
	
	def __setCancelTime( self, matchType ):
		Timer.cancel( self.remTimes[matchType][0] )
		self.remTimes[matchType][0] = 0
		self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "waitFresh" )
		self.__pyBtnApply.enable = False

	def __getTimeBySecs( self, remainTime ):
		hours = remainTime/3600
		minus = ( remainTime%3600 )/60
		secs = (remainTime%3600)%60
		return hours, minus, secs
	
	def __getTimeByMinus( self, remainTime ):
		days = remainTime/1440
		hours = ( remainTime%1440 )/60
		minus = ( remainTime%1440 )%60
		return days, hours, minus
	
	def cancelCountdown( self ):
		"""
		取消倒计时
		"""
		matchType = self.pyBinder.matchType
		Timer.cancel( self.remTimes[matchType][0] )
		self.remTimes[matchType] = [0, 0]

	def setGatherState( self, matchType ):
		"""
		设置集合按钮状态
		"""
		player = BigWorld.player()
		if not rds.statusMgr.isInWorld() : return
		gatherState = player.challengeHasFlagGather( matchType )
		self.__pyBtnGather.enable = gatherState
		self.__pyBtnGather.visible = gatherState
		self.__pyBtnApply.visible = not gatherState
	
	def onGatherTrigger( self ):
		self.__pyBtnGather.visible = True
		self.__pyBtnGather.enable = True
		self.__pyBtnApply.visible = False
	
# ------------------------------------------------------------------------
from guis.controls.StaticText import StaticText

class InfosPanel( PyGUI ):
	def __init__( self, pyBinder ):
		panel = GUI.load( "guis/general/relationwindow/athlepanel/infopanel.gui" )
		uiFixer.firstLoadFix( panel )
		PyGUI.__init__( self, panel )
		self.pyBinder = pyBinder
		self.__pyBtnRecr = HButtonEx( panel.btnRecr )
		self.__pyBtnRecr.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnRecr, "RelationShip:AthlePanel", "recruit" )
		self.__pyBtnRecr.onLClick.bind( self.__onRecruit )
		
		self.__pyBtnCancel = HButtonEx( panel.btnCancel )
		self.__pyBtnCancel.setExStatesMapping( UIState.MODE_R4C1 )
		labelGather.setPyBgLabel( self.__pyBtnCancel, "RelationShip:AthlePanel", "cancelRecr" )
		self.__pyBtnCancel.onLClick.bind( self.__onCancelRecr )
		
		self.__pyHourglass = PyGUI( panel.hourglass )
		self.__pyHourglass.visible = False
		
		self.__pyStWarning = StaticText( panel.stWarning )
		self.__pyStWarning.text = ""
		self.isRecruit = False
		
		self.__pyRtInfos = {}
		for name, item in panel.children:
			if name.startswith( "rtInfo_" ):
				index = int( name.split("_")[1])
				pyRtInfo = CSRichText( item )
				pyRtInfo.align = "C"
				pyRtInfo.text = ""
				self.__pyRtInfos[index] = pyRtInfo
	
	def __onRecruit( self, pyBtn ):
		"""
		招募队员
		"""
		if pyBtn is None:return
		BigWorld.player().challengeTeamRecruit()
	
	def __onCancelRecr( self, pyBtn ):
		"""
		取消招募
		"""
		if pyBtn is None:return
		BigWorld.player().challengeTeamCancelRecruit()
	
	def updateRecord( self, records ):
		"""
		第一次初始化信息
		"""
		for index, record in enumerate( records ):
			pyRtInfo = self.__pyRtInfos.get( index, None )
			if pyRtInfo is None:continue
			pyRtInfo.text = record
	
	def setStepInfo( self, stepInfo ):
		"""
		设置比赛赛段
		"""
		self.__pyRtInfos[3].text = stepInfo
	
	def onResultChange( self, rank ):
		"""
		XXX强通知
		"""
		infoText = ""
		if rank == csdefine.MATCH_LEVEL_NONE:
			infoText = "N/A"
		elif rank == csdefine.MATCH_LEVEL_FINAL:
			infoText = labelGather.getText( "RelationShip:AthlePanel","finals" )
		elif rank == csdefine.MATCH_LEVEL_SEMIFINALS:
			infoText = labelGather.getText( "RelationShip:AthlePanel","semifinal" )
		else:
			rank = pow( 2, rank -1 )
			infoText = labelGather.getText( "RelationShip:AthlePanel","ranks" )%str( rank )
		self.__pyRtInfos[2].text = labelGather.getText( "RelationShip:AthlePanel","curComState" )%infoText
	
	def setIniteInfos( self, matchType ):
		"""
		初始化信息
		"""
		player = BigWorld.player()
		lastInfo = ""
		totalInfo = ""
		curInfo = ""
		stepInfo = ""
		if matchType in INTEL_MATCHS:
			lastInfo = labelGather.getText( "RelationShip:AthlePanel","lastInteg" )%"N/A"
			totalInfo = labelGather.getText( "RelationShip:AthlePanel","totalInteg" )%"N/A"
			currPoint = 0
			if matchType == csdefine.MATCH_TYPE_PERSON_COMPETITION:
				currPoint = player.personalScore
			elif matchType == csdefine.MATCH_TYPE_TEAM_COMPETITION:
				currPoint = player.teamCompetitionPoint
			else:
				currPoint = player.tongCompetitionScore
			curInfo = labelGather.getText( "RelationShip:AthlePanel","curUseInteg" )%str( currPoint )
		else:
			lastInfo = labelGather.getText( "RelationShip:AthlePanel","lastRank" )%"N/A"
			totalInfo = labelGather.getText( "RelationShip:AthlePanel","bestRank" )%"N/A"
			curRank = player.matchResults.get( matchType, 0 )
			infoText = ""
			if curRank == csdefine.MATCH_LEVEL_NONE:
				infoText = "N/A"
			elif curRank == csdefine.MATCH_LEVEL_FINAL:
				infoText = labelGather.getText( "RelationShip:AthlePanel","finals" )
			elif curRank == csdefine.MATCH_LEVEL_SEMIFINALS:
				infoText = labelGather.getText( "RelationShip:AthlePanel","semifinal" )
			else:
				rank = pow( 2, curRank -1 )
				infoText = labelGather.getText( "RelationShip:AthlePanel","ranks" )%str( rank )
			curInfo = labelGather.getText( "RelationShip:AthlePanel","curComState" )%infoText
		levelSteps = player.levelSteps
		levelStep = levelSteps.get( matchType, ( 0, 0 ) )
		if levelStep == ( 0, 0 ):
			stepInfo = labelGather.getText( "RelationShip:AthlePanel","levelStep" )%"N/A"
		else:
			levels = "%d--%d"%( levelStep[0], levelStep[1] )
			stepInfo = labelGather.getText( "RelationShip:AthlePanel","levelStep" )%levels
		self.updateRecord( [lastInfo, totalInfo, curInfo, stepInfo] )
		isCaptain = player.isCaptain()
		self.__pyBtnRecr.visible = matchType == csdefine.MATCH_TYPE_TEAM_ABA and isCaptain and not self.__pyBtnCancel.visible
		self.__pyBtnCancel.visible = matchType == csdefine.MATCH_TYPE_TEAM_ABA and isCaptain and self.isRecruit
	
	def onTeamChallengeRecruit( self ):
		self.isRecruit = True
		self.__pyHourglass.visible = True
		self.__pyStWarning.text = labelGather.getText( "RelationShip:AthlePanel","onRecruit" )
		self.__pyBtnCancel.visible = True
		self.__pyBtnRecr.visible = False
	
	def onTeamRecruitCompelete( self ):
		self.isRecruit = False
		self.__pyHourglass.visible = False
		self.__pyStWarning.text = ""
		self.__pyBtnCancel.visible = False
		self.__pyBtnRecr.visible = True
	
	def reset( self ):
		self.isRecruit = False
		self.__pyHourglass.visible = False
		self.__pyStWarning.text = ""
		self.__pyBtnCancel.visible = False
		self.__pyBtnRecr.visible = False