# -*- coding:gb18030 -*-

import BigWorld
import time
import csdefine
import csconst
import csstatus
from bwdebug import *

class TeamCampTurnWarInterface:
	"""
	��Ӫ����ս�ӿ�
	"""
	def __init__( self ):
		self.campTurnWar_isJoin = False
		
	def campTurnWar_onMemberLeave( self, memInfo ):
		"""
		"""
		if self.campTurnWar_isJoin and self.id not in BigWorld.globalData["CampTurnWarHasSpaceTeam"]:		# �����Ѿ������˳���ս�����Ļ����������´�����Ϊ�˴���ֻ���ƥ��ͱ����׶�
			BigWorld.globalData["TongManager"].onPlayerLeaveTeam( self.id )
			self.__setJoinFlag( False )
			self.__onMemLeaveTeam()
			memInfo[ "playerBase" ].client.campTurnWar_onLeaveTeam()
			
	def campTurnWar_onChangeCaptain( self, newCaptainID ):
		"""
		"""
		if self.campTurnWar_isJoin:			# ��������ڳ���ս�ڼ䣬���ӳ����ø���ǣ�������Ӷ���
			captainInfo = self._getPlayerInfoByID( self.captainID )
			if captainInfo:
				captainBase = captainInfo["playerBase"]
				if captainBase:
					captainBase.cell.campTurnWar_setJoinFlag( False )
			
			captainInfo = self._getPlayerInfoByID( newCaptainID )
			captainBase = captainInfo["playerBase"]
			if captainBase:
				captainBase.cell.campTurnWar_setJoinFlag( True )
				
	def campTurnWar_onMemLogout( self ):
		"""
		"""
		if self.campTurnWar_isJoin and self.id not in BigWorld.globalData["CampTurnWarHasSpaceTeam"]:
			BigWorld.globalData["TongManager"].onPlayerLeaveTeam( self.id )
			self.__setJoinFlag( False )
			self.__onMemLeaveTeam()
			
	def campTurnWar_onDisband( self ):
		"""
		"""
		# ��ᳵ��սϵͳ��ش���
		if self.campTurnWar_isJoin and self.id not in BigWorld.globalData["CampTurnWarHasSpaceTeam"]:
			BigWorld.globalData["TongManager"].onPlayerLeaveTeam( self.id )
			self.__onMemLeaveTeam()
			
			captainInfo = self._getPlayerInfoByID( self.captainID )
			captainBase = captainInfo["playerBase"]
			if captainBase:
				captainBase.cell.campTurnWar_setJoinFlag( False )
	
	def campTurnWar_onSignUp( self ):
		"""
		define method
		�ɹ�������ᳵ��ս
		"""
		self.__setJoinFlag( True )
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.campTurnWar_onSignUp()
			
	def campTurnWar_onTeamMemPrepared( self, playerName ):
		"""
		define method
		��������׼������
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.campTurnWar_onTeamMemPrepared( playerName )
			
	def campTurnWar_onPlayerEnter( self, playerName ):
		"""
		define method
		���˵��˳�ս
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.campTurnWar_onPlayerEnter( playerName )
			
	def campTurnWar_onTeamMatched( self, tTeamMailbox, memDBIDs  ):
		"""
		define method
		�ҵ�ƥ�������
		
		@param tTeamMailbox: �Է������Mailbox
		@param memDBIDs: ����������������Լ������DBID�б�
		"""
		print "===================================>>>>>11", self.id, tTeamMailbox.id, memDBIDs
		allMemberInfo = []
		for dbid in memDBIDs:
			tempInfo = {}
			for playerID, info in self.member:
				if dbid == info["playerDBID"]:
					tempInfo["playerName"] = info["playerName"]
					tempInfo["headTextureID"] = info["headTextureID"]
					allMemberInfo.append( tempInfo )
		
		# �����Լ���Ա�Ŀͻ���
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			print "===================================>>>>>22", playerBase.id
			playerBase.client.campTurnWar_onReceiveSelfInfo( allMemberInfo )
		
		# �����з�����
		tTeamMailbox.campTurnWar_onReceiveEnemyInfo( allMemberInfo )
		
	def campTurnWar_onReceiveEnemyInfo( self, teamMemInfos ):
		"""
		define method
		���ܵз�����ĳ�Ա��Ϣ
		
		@param teamMemInfos : �Է�����ĳ�Ա��Ϣ
		@type teamMemInfos : [ { "playerName","headTextureID" } ]
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.campTurnWar_onReceiveEnemyInfo( teamMemInfos )
			
	def __onMemLeaveTeam( self ):
		"""
		��Ա�����ش���
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			if playerBase:
				playerBase.client.campTurnWar_onLeaveTeam()
			
	def __setJoinFlag( self, isJoin ):
		"""
		���òμӳ���ս�ı��
		
		@param isJoin : bool
		"""
		self.campTurnWar_isJoin = isJoin
		captainInfo = self._getPlayerInfoByID( self.captainID )
		if not captainInfo:
			return
		captainBase = captainInfo["playerBase"]
		if captainBase:
			captainBase.cell.campTurnWar_setJoinFlag( isJoin )
			
	def campTurnWar_onWarOver( self ):
		"""
		define method
		����ս����
		"""
		self.__setJoinFlag( False )