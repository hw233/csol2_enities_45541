# -*- coding: gb18030 -*-
import BigWorld

class UseDomainForTeamInter( object ):
	"""
	用于domian的team接口
	不一定是队伍副本才继承这个，这个接口只是表示路队伍相关的副本
	"""
	def __init__( self ):
		object.__init__( self )
		self.kickNotOnlineMembers = {}
	
	def setTeamRelation( self, teamEntityID, spaceNumber ):
		"""
		设置某个space与队伍的关系
		"""
		BigWorld.globalData[ "TeamManager" ].teamRemoteCall( teamEntityID, "addSpaceCopyInfos", ( self.name, spaceNumber ) )
	
	def removeTeamRelation( self, teamEntityID ):
		"""
		删除某个space的队伍关系
		"""
		BigWorld.globalData[ "TeamManager" ].teamRemoteCall( teamEntityID, "decSpaceCopyInfos", ( self.name, ) )
	
	def nofityNotOnlineKick( self, spaceNumber, playerDBID ):
		"""
		define method
		副本内不在线的队员被踢
		"""
		self.kickNotOnlineMembers[ playerDBID ] = spaceNumber
	
	def isKickNotOnlineMember( self, spaceNumber, playerDBID ):
		"""
		是不是队伍踢出去的玩家
		"""
		if self.kickNotOnlineMembers.has_key( playerDBID ):
			if self.kickNotOnlineMembers[ playerDBID ] == spaceNumber:
				return True
			else:
				return False
	
	def clearKickNotOnlineMember( self, playerDBID ):
		"""
		清掉指定玩家的踢离数据
		"""
		if self.kickNotOnlineMembers.has_key( playerDBID ):
			del self.kickNotOnlineMembers[ playerDBID ]
	
	def nofityTeamDestroy( self, spaceNumber, teamEntityID ):
		"""
		define method
		通知队伍解散
		"""
		spaceItem = self.getSpaceItem( spaceNumber )
		if spaceItem:
			spaceItem.baseMailbox.nofityTeamDestroy( teamEntityID )
#

class UseTeamForDomainInter( object ):
	# 队伍接口
	def __init__( self ):
		object.__init__( self )
		self.openCopyInfos = {} # 队伍所开启的副本信息
		
	def addSpaceCopyInfos( self, spaceType, spaceNumber ):
		"""
		define method
		添加队伍开启副本的信息
		"""
		self.openCopyInfos[ spaceType ] = spaceNumber
	
	def decSpaceCopyInfos( self, spaceType ):
		"""
		define method
		去掉队伍开启副本的信息
		"""
		if self.openCopyInfos.has_key( spaceType ):
			del self.openCopyInfos[ spaceType ]
	
	def desSpaceCopyNotify( self ):
		"""
		通知副本队伍解散
		"""
		for k, n in self.openCopyInfos.iteritems():
			BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( k, "nofityTeamDestroy", ( n, self.id ) )
	
	def kcikNotOnline( self, playerDBID ):
		"""
		通过副本副本离线的某个玩家被踢出副本
		"""
		for k, n in self.openCopyInfos.iteritems():
			BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( k, "nofityNotOnlineKick", ( n, playerDBID ) )