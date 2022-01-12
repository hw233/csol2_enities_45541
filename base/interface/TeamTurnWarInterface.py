# -*- coding:gb18030 -*-

import BigWorld
import time
import csdefine
import csconst
import csstatus
from bwdebug import *

class TeamTurnWarInterface:
	"""
	队伍车轮战接口
	"""
	def __init__( self ):
		self.turnWar_isJoin = False
		
	def turnWar_onMemberLeave( self, memInfo ):
		"""
		"""
		if self.turnWar_isJoin and self.id not in BigWorld.globalData["TurnWarHasSpaceTeam"]:		# 队伍已经开启了车轮战副本的话，不做如下处理，因为此处理只针对匹配和报名阶段
			BigWorld.globalData["TongManager"].onPlayerLeaveTeam( self.id )
			self.__setJoinFlag( False )
			self.__onMemLeaveTeam()
			memInfo[ "playerBase" ].client.turnWar_onLeaveTeam()
			
	def turnWar_onChangeCaptain( self, newCaptainID ):
		"""
		"""
		if self.turnWar_isJoin:			# 如果队伍在车轮战期间，给队长设置个标记，限制其加队友
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
		# 帮会车轮战系统相关处理
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
		成功报名帮会车轮战
		"""
		self.__setJoinFlag( True )
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.turnWar_onSignUpTong()
			
	def turnWar_onTeamMemPrepared( self, playerName ):
		"""
		define method
		队伍有人准备好了
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.turnWar_onTeamMemPrepared( playerName )
			
	def turnWar_onPlayerEnter( self, playerName ):
		"""
		define method
		有人点了出战
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.turnWar_onPlayerEnter( playerName )
			
	def turnWar_onTeamMatched( self, tTeamMailbox, memDBIDs  ):
		"""
		define method
		找到匹配队伍了
		
		@param tTeamMailbox: 对方队伍的Mailbox
		@param memDBIDs: 经过管理器排序的自己队伍的DBID列表
		"""
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
			playerBase.client.turnWar_onReceiveSelfInfo( allMemberInfo )
		
		# 发给敌方队伍
		tTeamMailbox.turnWar_onReceiveEnemyInfo( allMemberInfo )
		
	def turnWar_onReceiveEnemyInfo( self, teamMemInfos ):
		"""
		define method
		接受敌方队伍的成员信息
		
		@param teamMemInfos : 对方队伍的成员信息
		@type teamMemInfos : [ { "playerName","headTextureID" } ]
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			playerBase.client.turnWar_onReceiveEnemyInfo( teamMemInfos )
			
	def __onMemLeaveTeam( self ):
		"""
		队员离队相关处理
		"""
		for playerID, info in self.member:
			playerBase = info[ "playerBase" ]
			if playerBase:
				playerBase.client.turnWar_onLeaveTeam()
			
	def __setJoinFlag( self, isJoin ):
		"""
		设置参加车轮战的标记
		
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
		车轮战结束
		"""
		self.__setJoinFlag( False )