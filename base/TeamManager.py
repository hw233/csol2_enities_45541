# -*- coding: gb18030 -*-
#
# $Id: TeamManager.py,v 1.3 2007-11-16 03:44:02 zhangyuxing Exp $

import BigWorld
from bwdebug import *

class TeamManager(BigWorld.Base):
	def __init__( self ):
		BigWorld.Base.__init__(self)
		self.member = {}

		# 注册ENTITY
		# 加载空间配置
		self.registerGlobally("TeamManager", self._onRegisterManager)
		self.deregisterListeners = []

	#-----------------------------------------------------------
	# private
	def _onRegisterManager(self, complete):
		"""
		注册全局Base的回调函数。
		@param complete:	完成标志
		@type complete:		bool
		"""
		if not complete:
			ERROR_MSG( "Register TeamManager Fail!" )
			# again
			self.registerGlobally("TeamManager", self._onRegisterManager)
		else:
			BigWorld.globalData["TeamManager"] = self		# 注册到所有的服务器中
			INFO_MSG("Register TeamManager Success!")

	def register( self, teamID, teamMailBox ):
		"""
		<define>
		注册队伍

		过程：
		　记录队伍ID和MAILBOX

		@param teamID: 队伍ID
		@type teamID: OBJECT_ID
		@param teamMailBox: 队伍BASE
		@type teamMailBox: mailbox
		"""
		self.member[teamID] = teamMailBox

	def deregister( self, teamID ):
		"""
		<define>
		删除队伍

		过程：
		　从队伍列中删除队伍信息

		@param teamID: 队伍ID
		@type teamID: OBJECT_ID
		"""
		if self.member.has_key(teamID):
			self.member.pop( teamID )

		for i in self.deregisterListeners:
			i.onTeamDeregister( teamID )


	def rejoinTeam( self, teamID, playerDBID, playerBase ):
		"""
		<define>
		玩家上线

		过程：
		　向队伍管理器查找队伍，如果有有队伍，通知队伍本玩家上线

		@param teamID: 队伍ID
		@type teamID: OBJECT_ID
		@param playerDBID: 玩家DBID
		@type playerDBID: DATABASE_ID
		@param playerBase: 玩家BASE
		@type playerBase: mailbox
		"""
		if not self.member.has_key( teamID ):
			playerBase.clearTeamInfo()
			return

		self.member[teamID].logon( playerDBID, playerBase )

	def addDeregisterListener( self, mailbox ):
		"""
		define method
		增加对队伍解散感兴趣的听众
		"""
		self.deregisterListeners.append( mailbox )

	def setMessage( self, teamID, statuID ):
		# define method
		# 给指定的队伍发送提示信息
		if self.member.has_key( teamID ):
			self.member[teamID].setMessage( statuID )

	# ---------------------------------------------------------
	# 组队擂台
	# ---------------------------------------------------------
	def teamChallengeAddMember( self, teamID, playerDBID, playerName, playerLevel, playerBase, playerRaceclass, headTextureID ):
		# define method
		# 组队擂台加队员
		self.member[teamID].teamChallengeRequestJoin( playerDBID, playerName, playerLevel, playerBase, playerRaceclass, headTextureID )

	def teamChallengeChampion( self, teamID, entityDBIDs, minL, maxL, rewardTime ):
		# define method
		# 组队擂台冠军赛
		self.member[teamID].teamChallengeChampion( entityDBIDs, minL, maxL, rewardTime )

	def teamChallengeGather( self, teamID, round ):
		# define method
		# 组队擂队集合
		self.member[teamID].teamChallengeGather( round )

	def teamChallengeCloseGather( self, teamList ):
		# define method
		# 关闭组队擂队集合
		for teamID in teamList:
			if self.member.has_key( teamID ):
				self.member[ teamID ].teamChallengeCloseGather()

	def teamChallengeSetResult( self, teamList, result ):
		# define method
		# 设置组队擂队结果
		for teamID in teamList:
			if self.member.has_key( teamID ):
				self.member[ teamID ].teamChallengeSetResult( result )

	def removeDeregisterListener( self, mailbox ):
		"""
		define method
		删除对队伍解散感兴趣的听众
		"""
		for i in self.deregisterListeners:
			if i.id == mailbox.id:
				self.deregisterListeners.remove( i )
				break

	def teamChallengeUpLevel( self, teamID, maxLevel, minLevel ):
		# define method
		# 更新比赛等级
		if self.member.has_key( teamID ):
			self.member[ teamID ].teamChallengeUpLevel( maxLevel, minLevel )

	def teamChallengeUpInfo( self, teamList, result ):
		# define method
		# 更新当前队伍的排行
		for teamID in teamList:
			if self.member.has_key( teamID ):
				self.member[ teamID ].teamChallengeUpInfo( result )

	def teamChallengeClose( self, teamList ):
		# define method
		# 组队擂台活动结束
		for teamID in teamList:
			if self.member.has_key( teamID ):
				self.member[ teamID ].teamChallengeClose()

	def teamRemoteCall( self, teamID, rFuncName, args ) :
		"""
		<Define method>
		远程调用队伍的指定方法
		@type		teamID : OBJECT_ID
		@param		teamID : 队伍的ID
		@type		rFuncName : STRING
		@param		rFuncName : 队伍的远程方法名称
		@type		args : PY_ARGS
		@param		args : 远程方法参数组成的元组
		"""
		if teamID in self.member :
			getattr( self.member[teamID], rFuncName )( *args )
		else :
			WARNING_MSG( "Team(ID:%i) not found. Remote method is %s" % ( teamID, rFuncName ) )

#
# $Log: not supported by cvs2svn $
# Revision 1.2  2007/10/09 07:55:45  phw
# method modified: rejoinTeam(), playerBase.teamNotHas() -> playerBase.clearTeamInfo()
#
# Revision 1.1  2006/11/29 02:05:51  panguankong
# 添加了队伍系统
#