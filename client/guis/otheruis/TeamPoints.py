# -*- coding: gb18030 -*-
#
# $Id: CopyInfo.py fangpengjun $

from guis import *
from guis.common.RootGUI import RootGUI
from guis.common.PyGUI import PyGUI
from guis.tooluis.CSRichText import CSRichText
from guis.tooluis.richtext_plugins.PL_Font import PL_Font
from guis.controls.StaticText import StaticText
from LabelGather import labelGather
import ShareTexts
import event.EventCenter as ECenter
import Time
import csdefine
import Timer

from csconst import TEAM_COMPETITION_TIME
from csconst import FAMILY_COMPETITION_TIME
from csconst import ROLE_COMPETITION_TIME

from csconst import SAVE_MODEL_TIME
from csconst import END_TIME



class TeamPoints( RootGUI ):
	def __init__( self ):
		panel = GUI.load( "guis/otheruis/teampoints/points.gui" )
		uiFixer.firstLoadFix( panel )
		RootGUI.__init__( self, panel )
		self.h_dockStyle = "RIGHT"
		self.v_dockStyle = "TOP"
		self.moveFocus = False
		self.posZSegment = ZSegs.L4
		self.activable_ = False
		self.escHide_ = False
		self.focus = False
		self.__pyPoints = {}
		self.__triggers = {}
		self.__registerTriggers()
		self.__pyCurrentTime = StaticText( panel.lbTimeMsg )
		self.__pyCurrentTime.left = 0.0
		self.__pyCurrentTime.text = ""
		self._teamConpeteTimerID = 0
		self.endTime = 0

	# ----------------------------------------------------------------
	# private
	# ----------------------------------------------------------------
	def __registerTriggers( self ) :
		self.__triggers["EVT_ON_TEAM_COMPETITION_START"]			= self.__onTeamCompStart 		#组队竞赛开始
		self.__triggers["EVT_ON_RECIEVE_TEAM_COMPETITION_POINT"]	= self.__onRecTeamPoints 		#接收队伍积分
		self.__triggers["EVT_ON_RECIEVE_TEAM_COMPETITION_UPDATE"]	= self.__onUpdatePoints 		#更新队伍积分
		self.__triggers["EVT_ON_TEAM_COMPETITION_END"]				= self.__onTeamCompEnd 			#组队竞赛结束
		self.__triggers["EVT_ON_ENTER_TEAM_COMPETITION_SPACE"]		= self.__onEnterTeamCompSpace   #进入组队竞赛赛场
		self.__triggers["EVT_ON_LEAVE_TEAM_COMPETITION_SPACE"]		= self.__onLeaveCompSpace		#离开组队竞赛赛场
		self.__triggers["EVT_ON_ENTER_ROLE_COMPETITION_SPACE"]		= self.__onEnterRoleCompSpace	#进入个人竞赛赛场
		self.__triggers["EVT_ON_LEAVE_ROLE_COMPETITION_SPACE"]		= self.__onLeaveCompSpace	#离开个人竞赛赛场
		self.__triggers["EVT_ON_TONG_COMPETITION_START"]			= self.__onTongCompStart 		#帮会竞技开始
		self.__triggers["EVT_ON_ENTER_FAMILY_COMPETITION_SPACE"]	= self.__onEnterFamilyCompSpace	#进入帮会竞技赛场
		self.__triggers["EVT_ON_LEAVE_FAMILY_COMPETITION_SPACE"]	= self.__onLeaveCompSpace	#离开帮会竞技赛场
		self.__triggers["EVT_ON_RECIEVE_ROLE_COMPETITION_POINT"]	= self.__onRecRolePoints 		#接收个人竞技积分
		self.__triggers["EVT_ON_RECIEVE_TONG_COMPETITION_POINT"]	= self.__onRecTongCompPoints	#接收帮会竞技积分
		self.__triggers["EVT_ON_RECIEVE_ROLE_COMPETITION_REMAIN"]	= self.__onRecRoleRemainCount	#接收个人竞技剩余复活次数
		self.__triggers["EVT_ON_RECIEVE_TONG_COMPETITION_UPDATE"]	= self.__onUpdateTongCompPoints #更新帮会竞技积分
		self.__triggers["EVT_ON_RECIEVE_TEAM_COMPETITION_REMAIN"]	= self.__onUpdateTeamRecTimes	#组队竞技复活次数
		self.__triggers["EVT_ON_RECIEVE_TONG_COMPETITION_REMAIN"]	= self.__onRecTongRemainCount	#帮会竞技剩余复活次数
		self.__triggers["EVT_ON_ROLE_COMPETITION_END"]	= self.__onRoleCompetitionEnd				#个人竞技结束
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.registerEvent( eventMacro, self )

	def __deregisterTriggers( self ) :
		"""
		deregister event triggers
		"""
		for eventMacro in self.__triggers.iterkeys() :
			ECenter.unregisterEvent( eventMacro, self )

	# ------------------------------------------------------------------
	def __onTeamCompStart( self ):
#		self.__clearPoints()
		if self.visible:return
		self.visible = True

	def __onRecTeamPoints( self, teamID, leaderName, point, place ):
		teamColor = ( 255, 255, 255, 255 )
		if BigWorld.player().teamID == teamID:
			teamColor = 0, 255, 0, 255
		else:
			teamColor = 255, 0, 0, 255
		if not self.__pyPoints.has_key( teamID ) and leaderName != "":
			pointui = GUI.load( "guis/otheruis/teampoints/point.gui" )
			uiFixer.firstLoadFix( pointui )
			pyRtPoint = CSRichText( pointui )
			pyRtPoint.text = PL_Font.getSource( labelGather.getText( "TeamPoints:main", "teamPoint", leaderName, point ), fc = teamColor )
			pyRtPoint.place = place #排序
			self.__pyPoints[teamID] = pyRtPoint
			self.addPyChild( pyRtPoint )
		else:
			if leaderName == "":
				if self.__pyPoints.has_key( teamID ):
					self.__pyPoints.pop( teamID )
			else:
				pyRtPoint = self.__pyPoints.get( teamID )
				if pyRtPoint is None:return
				pyRtPoint.place = place
				pyRtPoint.text = PL_Font.getSource( labelGather.getText( "TeamPoints:main", "teamPoint", leaderName, point ), fc = teamColor )
		self.height = len( self.__pyPoints )*20.0 + self.__pyCurrentTime.bottom
		self.__layoutItems()

	def __onRecRolePoints( self, gradeList ):
		for pyRtPoint in self.__pyPoints.values():
			if pyRtPoint == self.__pyPoints[7]:
				pass
			else:
				pyRtPoint.text = ""
		place = 0
		teamColor = ( 255, 255, 255, 255 )
		for iInfo in gradeList:
			place = place + 1
			if BigWorld.player().playerName == iInfo[0]:
				teamColor = 0, 255, 0, 255
			else:
				teamColor = 255, 0, 0, 255
			if not self.__pyPoints.has_key( place ):
				pointui = GUI.load( "guis/otheruis/teampoints/point.gui" )
				uiFixer.firstLoadFix( pointui )
				pyRtPoint = CSRichText( pointui )
				pyRtPoint.text = PL_Font.getSource( labelGather.getText( "RolePoints:main", "rolePoint", iInfo[0], iInfo[1] ), fc = teamColor )
				pyRtPoint.place = place #排序
				self.__pyPoints[place] = pyRtPoint
				self.addPyChild( pyRtPoint )
			else:
				pyRtPoint = self.__pyPoints.get( place )
				if pyRtPoint is None:return
				pyRtPoint.text = PL_Font.getSource( labelGather.getText( "RolePoints:main", "rolePoint", iInfo[0], iInfo[1] ), fc = teamColor )
		self.height = len( self.__pyPoints )*20.0 + self.__pyCurrentTime.bottom
		self.__layoutItems()
		
	def __onRecRoleRemainCount( self, remainTuple ):
		roleColor = (0, 255, 0, 255)
		if BigWorld.player().id == remainTuple[0]:
			place = 7
			if not self.__pyPoints.has_key( place ):
				pointui = GUI.load( "guis/otheruis/teampoints/point.gui" )
				uiFixer.firstLoadFix( pointui )
				pyRtPoint = CSRichText( pointui )
				pyRtPoint.text = PL_Font.getSource( labelGather.getText( "RolePoints:main", "remainCount", remainTuple[1]), fc = roleColor )
				pyRtPoint.place = place
				self.__pyPoints[ place ] = pyRtPoint
				self.addPyChild( pyRtPoint )
			else:
				pyRtPoint = self.__pyPoints.get( place )
				if pyRtPoint is None:return
				pyRtPoint.text = PL_Font.getSource( labelGather.getText( "RolePoints:main", "remainCount", remainTuple[1]), fc = roleColor )
		self.height = len( self.__pyPoints )*20.0 + self.__pyCurrentTime.bottom
		self.__layoutItems()

	def __onTongCompStart( self ):
		if self.visible:return
		self.visible = True

	def __onRecTongCompPoints( self, tongDBID, tongName, point, place ):
		teamColor = ( 255, 255, 255, 255 )
		if BigWorld.player().tong_dbID == tongDBID:
			teamColor = 0, 255, 0, 255
		else:
			teamColor = 255, 0, 0, 255
		if not self.__pyPoints.has_key( tongDBID ):
			pointui = GUI.load( "guis/otheruis/teampoints/point.gui" )
			uiFixer.firstLoadFix( pointui )
			pyRtPoint = CSRichText( pointui )
			pyRtPoint.text = PL_Font.getSource( labelGather.getText( "TongCompPoints:main", "tongCompPoint", tongName, point ), fc = teamColor )
			pyRtPoint.place = place #排序
			self.__pyPoints[place] = pyRtPoint
			self.addPyChild( pyRtPoint )
		else:
			pyRtPoint = self.__pyPoints.get( place )
			if pyRtPoint is None:return
			pyRtPoint.text = PL_Font.getSource( labelGather.getText( "TongCompPoints:main", "tongCompPoint", tongName, point ), fc = teamColor )
		self.height = len( self.__pyPoints )*20.0 + self.__pyCurrentTime.bottom
		
	def __onRecTongRemainCount( self, leftDeathTimes ):
		"""
		帮会竞技复活次数界面显示
		"""
		roleColor = (0, 255, 0, 255)
		place = 7
		if not self.__pyPoints.has_key( place ):
			pointui = GUI.load( "guis/otheruis/teampoints/point.gui" )
			uiFixer.firstLoadFix( pointui )
			pyRtPoint = CSRichText( pointui )
			pyRtPoint.text = PL_Font.getSource( labelGather.getText( "TongCompPoints:main", "leftDeathTimes", leftDeathTimes ), fc = roleColor )
			pyRtPoint.place = place
			self.__pyPoints[ place ] = pyRtPoint
			self.addPyChild( pyRtPoint )
		else:
			pyRtPoint = self.__pyPoints.get( place )
			if pyRtPoint is None:return
			pyRtPoint.text = PL_Font.getSource( labelGather.getText( "TongCompPoints:main", "leftDeathTimes", leftDeathTimes ), fc = roleColor )
		self.height = len( self.__pyPoints )*20.0 + self.__pyCurrentTime.bottom
		self.__layoutItems()


	def __onUpdateTongCompPoints( self ):
		"""
		"""
		self.__layoutItems( 0 )

	def __onUpdatePoints( self ):
		"""
		"""
		self.__layoutItems( 0 )
	
	def __onUpdateTeamRecTimes( self, times ):
		"""
		组队竞技复活次数
		"""
		roleColor = (0, 255, 0, 255)
		place = 255
		if not self.__pyPoints.has_key( place ):
			pointui = GUI.load( "guis/otheruis/teampoints/point.gui" )
			uiFixer.firstLoadFix( pointui )
			pyRtPoint = CSRichText( pointui )
			pyRtPoint.text = PL_Font.getSource( labelGather.getText( "RolePoints:main", "remainCount", times ), fc = roleColor )
			pyRtPoint.place = place
			self.__pyPoints[ place ] = pyRtPoint
			self.addPyChild( pyRtPoint )
		else:
			pyRtPoint = self.__pyPoints.get( place )
			if pyRtPoint is None:return
			pyRtPoint.text = PL_Font.getSource( labelGather.getText( "RolePoints:main", "remainCount", times ), fc = roleColor )
		self.height = len( self.__pyPoints )*20.0 + self.__pyCurrentTime.bottom
		self.__layoutItems()

	def __layoutItems( self, startIndex = 0 ) :
		offset = self.__pyCurrentTime.bottom
		itemCount = len( self.__pyPoints )
		if itemCount == 0 : return
		if startIndex >= itemCount : return
		pyPoints = self.__pyPoints.values()
		pyPoints.sort( key = lambda pyPoint: pyPoint.place, reverse = False )
		pyPoint = pyPoints[startIndex]
		pyPoint.left = 0
		if startIndex == 0 :
			pyPoint.top = offset
		else :
			pyPoint.top = pyPoints[startIndex - 1].bottom + offset
		for pyNextPoint in pyPoints[( startIndex + 1 ):] :
			pyNextPoint.left = 0
			pyNextPoint.top = pyPoint.bottom
			pyPoint = pyNextPoint

	def __onTeamCompEnd( self ):
		if self.visible:
			self.visible = False
		self.__clearPoints()

	def __onEnterCompSpace( self, endTime ):
		"""
		"""
		if not self.visible:
			self.visible = True
#			for pyRtPoint in self.__pyPoints.values():
#				pyRtPoint.visible = False
		if not self.__pyCurrentTime.visible:
			self.__pyCurrentTime.visible = True
		self.endTime = int( endTime )
		if self._teamConpeteTimerID == 0:
			self.__pyCurrentTime.text = ""
			self.width = 300.0
			self._teamConpeteTimerID = Timer.addTimer( 0, 1, self.__gameTimeUpdate )

	def __onLeaveCompSpace( self ):
		"""
		离开组队竞赛赛场
		"""
		self.__pyCurrentTime.text = ""
		if self.visible:
			self.visible = False
		self.__clearPoints()
		self.height = len( self.__pyPoints )*20.0 + self.__pyCurrentTime.bottom
		self.__cancelTeamCopeteTimer()

	def __onEnterTeamCompSpace( self, endTime ):
		"""
		进入组队竞赛赛场
		"""
		self.competitionTime = TEAM_COMPETITION_TIME
		self.saveModelTime	 = SAVE_MODEL_TIME
		self.__clearPoints()
		self.__onEnterCompSpace( endTime )

	def __onEnterRoleCompSpace( self, endTime ,pkProtectTime):
		"""
		进入个人竞赛赛场
		"""
		self.competitionTime = ROLE_COMPETITION_TIME
		self.saveModelTime	 = pkProtectTime
		self.__onEnterCompSpace( endTime )
		self.__clearPoints()
		self.height = len( self.__pyPoints )*20.0 + self.__pyCurrentTime.bottom

	def __onEnterFamilyCompSpace( self, endTime ):
		"""
		进入家族竞赛赛场
		"""
		self.competitionTime = FAMILY_COMPETITION_TIME
		self.saveModelTime	 = SAVE_MODEL_TIME
		self.__onEnterCompSpace( endTime )
		self.__clearPoints()
		self.height = len( self.__pyPoints )*20.0 + self.__pyCurrentTime.bottom
		
	def __onRoleCompetitionEnd( self ):
		self.endTime = Time.Time.time()
		self.__pyCurrentTime.text = labelGather.getText( "TeamPoints:main", "actEnd" )
		self.__pyCurrentTime.color = ( 255.0, 255.0, 0.0 )

	def __gameTimeUpdate( self ):
		"""
		更新赛场剩余时间显示
		"""
		if not self.visible:
			self.__cancelTeamCopeteTimer()
			return

		remainTime = self.endTime - Time.Time.time()
		if remainTime > self.competitionTime + self.saveModelTime:
			return
		"""
		队伍进入竞技场后，活动尚未开始之前，红色文字显示： 距离活动开始还有：XX分XX秒 （小于1分钟时，不显示XX分）
		活动开始之后，绿色显示： 距离活动结束还有：XX分XX秒 （小于1分钟时，不显示XX分）
		活动结束后，黄色显示：活动已结束。 （队伍仍在竞技场中时显示）
		"""
		if remainTime > self.competitionTime:
			remainTime = remainTime - self.competitionTime
			msg = ""
			minutes = remainTime / 60
			seconds = remainTime % 60
			if minutes <= 0:
				msg = str( seconds ) + ShareTexts.CHTIME_SECOND
			else:
				msg = "%d%s%d%s" % ( minutes, ShareTexts.CHTIME_MINUTE, seconds, ShareTexts.CHTIME_SECOND )
			self.__pyCurrentTime.text = labelGather.getText( "TeamPoints:main", "tillBegin", msg )
			self.__pyCurrentTime.color = ( 255.0, 0.0, 0.0 )
		elif remainTime > 0 and remainTime <= self.competitionTime:
			msg = ""
			minutes = remainTime / 60
			seconds = remainTime % 60
			if minutes <= 0:
				msg = str( seconds ) + ShareTexts.CHTIME_SECOND
			else:
				msg = "%d%s%d%s" % ( minutes, ShareTexts.CHTIME_MINUTE, seconds, ShareTexts.CHTIME_SECOND )
			self.__pyCurrentTime.text = labelGather.getText( "TeamPoints:main", "tillEnd", msg )
			self.__pyCurrentTime.color = ( 128.0, 255.0, 0.0 )
		else:
			self.__pyCurrentTime.text = labelGather.getText( "TeamPoints:main", "actEnd" )
			self.__pyCurrentTime.color = ( 255.0, 255.0, 0.0 )

	def __cancelTeamCopeteTimer( self ): #清除计时器
		Timer.cancel( self._teamConpeteTimerID )
		self._teamConpeteTimerID = 0
		self.endTime = 0


	def __clearPoints( self ):
		"""
		清空积分面板
		"""
		if len( self.__pyPoints ) > 0:
			for pyPoint in self.__pyPoints.values():
				self.delPyChild( pyPoint )
			self.__pyPoints = {}
	# ------------------------------------------------------------ ----
	# public
	# ----------------------------------------------------------------
	def onEvent( self, eventMacro, *args ) :
		self.__triggers[eventMacro]( *args )

	def onLeaveWorld( self ):
		self.__clearPoints()
		self.visible = False