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
		���캯����
		"""
		SpaceCopy.__init__( self )
		self.hasClearNoFight = False		# ����Ƿ��Ѿ��������ɫ����սЧ��
		startTime = BigWorld.globalData[ "TeamChallengeCurrentRoundTime" ]
		closeEnterTime = startTime + csconst.TEAM_CHALLENGE_TIME_PREPARE * 60 - time.time()
		destroyTime = startTime + ( csconst.TEAM_CHALLENGE_TIME_PREPARE + csconst.TEAM_CHALLENGE_TIME_UNDERWAY ) * 60 - time.time()
		
		self.addTimer( closeEnterTime, 0, TIME_ARG_PREPARE )
		self.addTimer( destroyTime, 0, TIME_ARG_ROUND )
		self.setTemp( "challengeIsClose", False )
	
	def onTimer( self, timeID, userArg ):
		if userArg == TIME_ARG_PREPARE:
			# ׼��ʱ�����
			if len( self.teamChallengeInfos.dbidToMailBox ) == 0:
				# ���û������ڸ���
				self.getScript().closeSpace( self )
				return
				
			teamNum = len( self.teamChallengeInfos.infos.keys() )
			teamIDs = self.teamChallengeInfos.infos.keys()
			if teamNum ==  0:
				# û������룬�رո���
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
			# һ�ֱ���������ʱ��
			teamIDs = self.teamChallengeInfos.infos.keys()
			teamNum = len( teamIDs )
			if teamNum == 1:
				# ���߹�����ʤ���Ķ���
				BigWorld.globalData[ "TeamChallengeMgr" ].teamWin( teamIDs[ 0 ] )
				
			elif teamNum == 2:
				BigWorld.globalData[ "TeamChallengeMgr" ].teamDraw( teamIDs[ 0 ], teamIDs[ 1 ] )
				
			self.getScript().closeSpace( self )
				
		SpaceCopy.onTimer( self, timeID, userArg )
	
	def addWatchPlayer( self, teamID, playerMailBox ):
		# define method
		# ��ӹ�ս�б�
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
		shownDetails ����������ʾ����
		[ 
			0: ʣ��ʱ��
			1: ʣ��С��
			2: ʣ��С������
			3: ʣ��BOSS
			4: ��������
			5: ʣ��ħ�ƻ�����
			6: ʣ�����Ӱʨ����
			7: ��һ��ʣ��ʱ��(���Ȫm؅)
			9: ��ɽ�󷨲���
			10: ��������
			11: �з�����
		]
		"""
		return [ 10, 11 ]

