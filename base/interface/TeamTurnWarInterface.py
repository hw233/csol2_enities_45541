# -*- coding:gb18030 -*-

import BigWorld
import time
import csdefine
import csconst
import csstatus
from bwdebug import *

class TeamTurnWarInterface:
	"""
	���鳵��ս�ӿ�
	"""
	def __init__( self ):
		self.turnWar_isJoin = False
		
	def turnWar_onMemberLeave( self, memInfo ):
		"""
		"""
		if self.turnWar_isJoin and self.id not in BigWorld.globalData["TurnWarHasSpaceTeam"]:		# �����Ѿ������˳���ս�����Ļ����������´�����Ϊ�˴���ֻ���ƥ��ͱ����׶�
			BigWorld.globalData["TongManager"].onPlayerLeaveTeam( self.id )
			self.__setJoinFlag( False )
			self.__onMemLeaveTeam()
			memInfo[ "playerBase" ].client.turnWar_onLeaveTeam()
			
	def turnWar_onChangeCaptain( self, newCaptainID ):
		"""
		"""
		if self.turnWar_isJoin:			# ��������ڳ���ս�ڼ䣬���ӳ����ø���ǣ�������Ӷ���
			captainInfo = self._getPlayerInfoByID( self.captainID )
			if captainInfo:
				captainBase = captainInfo["playerBase"]
				if captainBase:
					captainBase.cell.turnWar_setJoinFlag( False )
			
			captainInfo = self._getPlayerInfoByID( newCaptainID )
			captainBase = captainInfo["playerBase"]
			if captainBase:
				captainBase.cell.turnWar_setJoinFlag( True )
				
	def turnWar_onMemLogout( self ):
		"""
		"""
		if self.turnWar_isJoin and self.id not in BigWorld.globalData["TurnWarHasSpaceTeam"]:
			BigWorld.globalData["TongManager"].onPlayerLeaveTeam( self.id )
			self.__setJoinFlag( False )
			self.__onMemLeaveTeam()
			
	def turnWar_onDisband( self ):
		"""
		"""
		# ��ᳵ��սϵͳ��ش���
		if self.turnWar_isJoin and self.id not in BigWorld.globalData["TurnWarHasSpaceTeam"]:
			BigWorld.globalData["TongManager"].onPlayerLeaveTeam( self.id )
			self.__onMemLeaveTeam()
			
			captainInfo = self._getPlayerInfoByID( self.captainID )
			captainBase = captainInfo["playerBase"]
			if captainBase:
				captainBase.cell.turnWar_setJoinFlag( False )
	
	def turnWar_onSignUpTong( self ):
		"""
		define method
		�ɹ�������ᳵ��ս
		"""
		self.__setJoinFlag( True )
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.turnWar_onSignUpTong()
			
	def turnWar_onTeamMemPrepared( self, playerName ):
		"""
		define method
		��������׼������
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.turnWar_onTeamMemPrepared( playerName )
			
	def turnWar_onPlayerEnter( self, playerName ):
		"""
		define method
		���˵��˳�ս
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.turnWar_onPlayerEnter( playerName )
			
	def turnWar_onTeamMatched( self, tTeamMailbox, memDBIDs  ):
		"""
		define method
		�ҵ�ƥ�������
		
		@param tTeamMailbox: �Է������Mailbox
		@param memDBIDs: ����������������Լ������DBID�б�
		"""
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
			playerBase.client.turnWar_onReceiveSelfInfo( allMemberInfo )
		
		# �����з�����
		tTeamMailbox.turnWar_onReceiveEnemyInfo( allMemberInfo )
		
	def turnWar_onReceiveEnemyInfo( self, teamMemInfos ):
		"""
		define method
		���ܵз�����ĳ�Ա��Ϣ
		
		@param teamMemInfos : �Է�����ĳ�Ա��Ϣ
		@type teamMemInfos : [ { "playerName","headTextureID" } ]
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.turnWar_onReceiveEnemyInfo( teamMemInfos )
			
	def __onMemLeaveTeam( self ):
		"""
		��Ա�����ش���
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			if playerBase:
				playerBase.client.turnWar_onLeaveTeam()
			
	def __setJoinFlag( self, isJoin ):
		"""
		���òμӳ���ս�ı��
		
		@param isJoin : bool
		"""
		self.turnWar_isJoin = isJoin
		captainInfo = self._getPlayerInfoByID( self.captainID )
		if not captainInfo:
			return
		captainBase = captainInfo["playerBase"]
		if captainBase:
			captainBase.cell.turnWar_setJoinFlag( isJoin )
			
	def turnWar_onWarOver( self ):
		"""
		define method
		����ս����
		"""
		self.__setJoinFlag( False )