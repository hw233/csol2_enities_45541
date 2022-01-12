# -*- coding: gb18030 -*-
import time

from SpaceCopy import SpaceCopy
import BigWorld
import csconst
import csstatus

TIME_ARG_PREPARE = 1
TIME_ARG_ROUND = 2

class SpaceCopyTeamChallenge( SpaceCopy ):
	"""
	"""
	def __init__(self):
		"""
		构造函数。
		"""
		SpaceCopy.__init__( self )
		self.hasClearNoFight = False		# 标记是否已经清楚过角色的免战效果
		startTime = BigWorld.globalData[ "TeamChallengeCurrentRoundTime" ]
		closeEnterTime = startTime + csconst.TEAM_CHALLENGE_TIME_PREPARE * 60 - time.time()
		destroyTime = startTime + ( csconst.TEAM_CHALLENGE_TIME_PREPARE + csconst.TEAM_CHALLENGE_TIME_UNDERWAY ) * 60 - time.time()
		
		self.addTimer( closeEnterTime, 0, TIME_ARG_PREPARE )
		self.addTimer( destroyTime, 0, TIME_ARG_ROUND )
		self.setTemp( "challengeIsClose", False )
	
	def onTimer( self, timeID, userArg ):
		if userArg == TIME_ARG_PREPARE:
			# 准备时间结束
			if len( self.teamChallengeInfos.dbidToMailBox ) == 0:
				# 如果没有玩家在副本
				self.getScript().closeSpace( self )
				return
				
			teamNum = len( self.teamChallengeInfos.infos.keys() )
			teamIDs = self.teamChallengeInfos.infos.keys()
			if teamNum ==  0:
				# 没队伍进入，关闭副本
				self.getScript().closeSpace( self )
			elif teamNum ==  1:
				BigWorld.globalData[ "TeamChallengeMgr" ].teamWin( teamIDs[ 0 ] )
				for e in self._players:
					e.client.onStatusMessage( csstatus.TEAM_CHALLENGE_OPPONENT_NOT_ENTER, "" )
				self.getScript().closeSpace( self )
			else:
				if len( self.teamChallengeInfos[ teamIDs[0] ] ) == 0:
					BigWorld.globalData[ "TeamChallengeMgr" ].teamWin(  teamIDs[ 1 ] )
					for e in self._players:
						e.client.onStatusMessage( csstatus.TEAM_CHALLENGE_OPPONENT_NOT_ENTER, "" )
					self.getScript().closeSpace( self )
				
				if len( self.teamChallengeInfos[ teamIDs[1] ] ) == 0:
					BigWorld.globalData[ "TeamChallengeMgr" ].teamWin( teamIDs[ 0 ] )
					for e in self._players:
						e.client.onStatusMessage( csstatus.TEAM_CHALLENGE_OPPONENT_NOT_ENTER, "" )
					self.getScript().closeSpace( self )
					
				self.getScript().clearNoFight( self )
				
		elif userArg == TIME_ARG_ROUND:
			# 一轮比赛结束的时间
			teamIDs = self.teamChallengeInfos.infos.keys()
			teamNum = len( teamIDs )
			if teamNum == 1:
				# 告诉管理器胜利的队伍
				BigWorld.globalData[ "TeamChallengeMgr" ].teamWin( teamIDs[ 0 ] )
				
			elif teamNum == 2:
				BigWorld.globalData[ "TeamChallengeMgr" ].teamDraw( teamIDs[ 0 ], teamIDs[ 1 ] )
				
			self.getScript().closeSpace( self )
				
		SpaceCopy.onTimer( self, timeID, userArg )
	
	def addWatchPlayer( self, teamID, playerMailBox ):
		# define method
		# 添加观战列表
		teamMailBoxs = self.queryTemp( teamID, [] )
		teamMailBoxs.append( playerMailBox )
		self.setTemp( teamID, teamMailBoxs )
		
		rNum = 0
		lNum = 0
		teamIDs = self.teamChallengeInfos.infos.keys()
		if teamID in teamIDs:
			rNum = len( self.teamChallengeInfos[ teamID ] )
		
		if len( teamIDs ) == 2:
			teamIDs.remove( teamID )
			lTeamID = teamIDs[ 0 ]
			lNum = len( self.teamChallengeInfos[ lTeamID ] )
			
		playerMailBox.client.teamChallengeMember( rNum, lNum )
		
	def shownDetails( self ):
		"""
		shownDetails 副本内容显示规则：
		[ 
			0: 剩余时间
			1: 剩余小怪
			2: 剩余小怪批次
			3: 剩余BOSS
			4: 蒙蒙数量
			5: 剩余魔纹虎数量
			6: 剩余真鬼影狮数量
			7: 下一波剩余时间(拯救猰貐)
			9: 华山阵法层数
			10: 己方人数
			11: 敌方人数
		]
		"""
		return [ 10, 11 ]

