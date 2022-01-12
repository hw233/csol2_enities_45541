# -*- coding:gb18030 -*-

import BigWorld
import time
import csdefine
import csconst
import csstatus
from bwdebug import *

class TeamCampTurnWarInterface:
	"""
	阵营车轮战接口
	"""
	def __init__( self ):
		self.campTurnWar_isJoin = False
		
	def campTurnWar_onMemberLeave( self, memInfo ):
		"""
		"""
		if self.campTurnWar_isJoin and self.id not in BigWorld.globalData["CampTurnWarHasSpaceTeam"]:		# 队伍已经开启了车轮战副本的话，不做如下处理，因为此处理只针对匹配和报名阶段
			BigWorld.globalData["TongManager"].onPlayerLeaveTeam( self.id )
			self.__setJoinFlag( False )
			self.__onMemLeaveTeam()
			memInfo[ "playerBase" ].client.campTurnWar_onLeaveTeam()
			
	def campTurnWar_onChangeCaptain( self, newCaptainID ):
		"""
		"""
		if self.campTurnWar_isJoin:			# 如果队伍在车轮战期间，给队长设置个标记，限制其加队友
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
		# 帮会车轮战系统相关处理
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
		成功报名帮会车轮战
		"""
		self.__setJoinFlag( True )
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.campTurnWar_onSignUp()
			
	def campTurnWar_onTeamMemPrepared( self, playerName ):
		"""
		define method
		队伍有人准备好了
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.campTurnWar_onTeamMemPrepared( playerName )
			
	def campTurnWar_onPlayerEnter( self, playerName ):
		"""
		define method
		有人点了出战
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.campTurnWar_onPlayerEnter( playerName )
			
	def campTurnWar_onTeamMatched( self, tTeamMailbox, memDBIDs  ):
		"""
		define method
		找到匹配队伍了
		
		@param tTeamMailbox: 对方队伍的Mailbox
		@param memDBIDs: 经过管理器排序的自己队伍的DBID列表
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
		
		# 发给自己队员的客户端
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			print "===================================>>>>>22", playerBase.id
			playerBase.client.campTurnWar_onReceiveSelfInfo( allMemberInfo )
		
		# 发给敌方队伍
		tTeamMailbox.campTurnWar_onReceiveEnemyInfo( allMemberInfo )
		
	def campTurnWar_onReceiveEnemyInfo( self, teamMemInfos ):
		"""
		define method
		接受敌方队伍的成员信息
		
		@param teamMemInfos : 对方队伍的成员信息
		@type teamMemInfos : [ { "playerName","headTextureID" } ]
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.campTurnWar_onReceiveEnemyInfo( teamMemInfos )
			
	def __onMemLeaveTeam( self ):
		"""
		队员离队相关处理
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			if playerBase:
				playerBase.client.campTurnWar_onLeaveTeam()
			
	def __setJoinFlag( self, isJoin ):
		"""
		设置参加车轮战的标记
		
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
		车轮战结束
		"""
		self.__setJoinFlag( False )