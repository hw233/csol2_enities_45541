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
		���˾�������Ӿ�������Ὰ����
		�ϴβ�����û���INT32��param1
		�ۼƲ�����û���INT32��param2
		
		�����ᣬ�����̨�������̨:
		�ϴβ����������INT32��param1
		�����ò�������INT32��param2
		"""
		records = []
		self.__isInited = True
		self.param2 = param2
		player = BigWorld.player()
		if self.matchType in INTEL_MATCHS: #���ھ�����,�����ϴλ��֣��ۼƻ���
			lastIntel = labelGather.getText( "RelationShip:AthlePanel","lastInteg" )%param1
			totalIntel = labelGather.getText( "RelationShip:AthlePanel","totalInteg" )%self.param2
			currPoint = 0
			if self.matchType == csdefine.MATCH_TYPE_PERSON_COMPETITION:
				currPoint = player.personalScore
			elif self.matchType == csdefine.MATCH_TYPE_TEAM_COMPETITION:
				currPoint = player.teamCompetitionPoint
			else:
				currPoint = player.tongCompetitionScore
			curUseInteg = labelGather.getText( "RelationShip:AthlePanel","curUseInteg" )%str( currPoint ) #��ǰ���û���
			records = [lastIntel, totalIntel, curUseInteg]
		else: #��̨�࣬�ϴβ������Σ�������Σ���ǰ���
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
		���˾�������Ӿ�������Ὰ����
		�ϴβ�����û���INT32��param
		
		�����ᣬ�����̨�������̨:
		�ϴβ����������INT32��param
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
		�����ȼ��θı�
		"""
		minLevel = levelStep[0]
		maxLevel = levelStep[1]
		levels = "%d--%d"%( minLevel, maxLevel )
		curStep = labelGather.getText( "RelationShip:AthlePanel","levelStep" )%levels
		self.__pyInfoPanel.setStepInfo( curStep )
	
	def onResultChange( self, rank ):
		"""
		��������ı�
		"""
		self.__pyInfoPanel.onResultChange( rank )
	
	def setRemainTime( self, times ):
		"""
		ʣ��ʱ��ı�
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
		elif self.matchType in [csdefine.MATCH_TYPE_TEAM_ABA, csdefine.MATCH_TYPE_PERSON_ABA]:#��ʾ60���Ӻ��� 
			remainTime += 75*60

		if remainTime < 0:
			minsDay -= 1
		
		self.__pyTimePanel.setRemainTime( minsDay, remainTime )
	
	def onGatherTrigger( self ):
		self.__pyTimePanel.onGatherTrigger()

	def setIniteInfos( self ):
		"""
		��ʼ����Ϣ
		"""
		self.__pyInfoPanel.setIniteInfos( self.matchType )

	def onHide( self ) :
		"""
		��������ʱ������
		"""
		TabPanel.onHide( self )
		self.__pyTimePanel.cancelCountdown()
	
	def cancelCountdown( self ):
		self.__pyTimePanel.cancelCountdown()
	
	def setGatherState( self ):
		"""
		���ü��ϰ�ť״̬
		"""
		self.__pyTimePanel.setGatherState( self.matchType )
	
	def onTeamChallengeRecruit( self ):
		"""
		������ļ
		"""
		self.__pyInfoPanel.onTeamChallengeRecruit()
	
	def onTeamRecruitCompelete( self ):
		"""
		��ļ���
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
		
		
		self.remTimes = {csdefine.MATCH_TYPE_PERSON_COMPETITION:[0, 0], #callbackid��remaintime
					csdefine.MATCH_TYPE_TEAM_COMPETITION:[0, 0],
					csdefine.MATCH_TYPE_TONG_COMPETITION:[0, 0],
					csdefine.MATCH_TYPE_PERSON_ABA:[0, 0],
					csdefine.MATCH_TYPE_TEAM_ABA:[0, 0],
					csdefine.MATCH_TYPE_TONG_ABA:[0, 0],
				}
		
	def __onApply( self, pyBtn ):
		"""
		����
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
		����
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
		���õ���ʱ
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
		���뵹��ʱ
		"""
		matchType = self.pyBinder.matchType
		remainTime = self.remTimes[matchType][1]
		if remainTime > 5*60: #����ʱ��
			if not self.__pyBtnGather.visible:
				self.__pyBtnApply.visible = True
			if matchType in [csdefine.MATCH_TYPE_TEAM_COMPETITION, csdefine.MATCH_TYPE_TONG_COMPETITION]: #��Ӿ���
				self.__pyBtnApply.enable = remainTime <= 60*60
				if remainTime > 60*60:
					remainTime -= 60*60
					hours, minus, secs = self.__getTimeBySecs( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupStartBySecs" )%( hours, minus, secs )
				else:
					hours, minus, secs = self.__getTimeBySecs( remainTime - 60*5 )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupEndBySecs" )%( hours, minus, secs )
			elif matchType == csdefine.MATCH_TYPE_PERSON_COMPETITION: #���˾���
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
			elif matchType == csdefine.MATCH_TYPE_TONG_ABA: #�����̨
				self.__pyBtnApply.enable = remainTime <= 15*60
				if remainTime > 60*15:
					remainTime -= 60*15
					hours, minus, secs = self.__getTimeBySecs( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupStartBySecs" )%( hours, minus, secs )
				else:
					hours, minus, secs = self.__getTimeBySecs( remainTime - 60*5 )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupEndBySecs" )%( hours, minus, secs )
			else: #�����ᡢ�����̨
				self.__pyBtnApply.enable = remainTime <= 15*60
				if remainTime > 60*15:
					remainTime -= 60*15
					hours, minus, secs = self.__getTimeBySecs( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupStartBySecs" )%( hours, minus, secs )
				else:
					hours, minus, secs = self.__getTimeBySecs( remainTime )
					self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupEndBySecs" )%( hours, minus, secs )
		elif remainTime <= 5*60 and remainTime > 0: #5���Ӽ���ʱ��
			hours, minus, secs = self.__getTimeBySecs( remainTime )
			if not matchType in [csdefine.MATCH_TYPE_TEAM_ABA, csdefine.MATCH_TYPE_PERSON_ABA]:
				self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "enterbySecs" )%( hours, minus, secs )
				if self.__pyBtnGather.visible:
					self.__pyBtnApply.visible = False
			else:
				self.__pyRtTime.text = labelGather.getText( "RelationShip:AthlePanel", "signupEndBySecs" )%( hours, minus, secs )
		else:
			if matchType in [csdefine.MATCH_TYPE_TEAM_ABA, csdefine.MATCH_TYPE_PERSON_ABA]: #������������̨�ǿ�ʼ�����ͼ���
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
		���ֵ���ʱ
		"""
		matchType = self.pyBinder.matchType
		remainTime = self.remTimes[matchType][1]
		if remainTime > 5: #����ʱ��
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
		ȡ������ʱ
		"""
		matchType = self.pyBinder.matchType
		Timer.cancel( self.remTimes[matchType][0] )
		self.remTimes[matchType] = [0, 0]

	def setGatherState( self, matchType ):
		"""
		���ü��ϰ�ť״̬
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
		��ļ��Ա
		"""
		if pyBtn is None:return
		BigWorld.player().challengeTeamRecruit()
	
	def __onCancelRecr( self, pyBtn ):
		"""
		ȡ����ļ
		"""
		if pyBtn is None:return
		BigWorld.player().challengeTeamCancelRecruit()
	
	def updateRecord( self, records ):
		"""
		��һ�γ�ʼ����Ϣ
		"""
		for index, record in enumerate( records ):
			pyRtInfo = self.__pyRtInfos.get( index, None )
			if pyRtInfo is None:continue
			pyRtInfo.text = record
	
	def setStepInfo( self, stepInfo ):
		"""
		���ñ�������
		"""
		self.__pyRtInfos[3].text = stepInfo
	
	def onResultChange( self, rank ):
		"""
		XXXǿ֪ͨ
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
		��ʼ����Ϣ
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