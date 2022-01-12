# -*- coding: gb18030 -*-
import BigWorld

from SpaceDomainCopyMaps import SpaceDomainCopyMaps
from SpaceDomainCopyMaps import CopyItem

class CopyItemTeam( CopyItem ):
	def __init__( self, domain, teamID ):
		CopyItem.__init__( self, domain, teamID )
		BigWorld.globalData[ "TeamManager" ].teamRemoteCall( teamID, "addSpaceCopyInfos", ( self._domain.name, self.copyKey ) )
	
	def enter( self, domain, position, direction, baseMailbox, params ):
		"""
		申请进入副本
		"""
		CopyItem.enter( self, domain, position, direction, baseMailbox, params )
	
	def logon( self, baseMailbox, params ):
		"""
		玩家登陆
		"""
		baseMailbox.logonSpaceInSpaceCopy()
	
	def closeCopyItem( self, params ):
		"""
		关闭副本
		"""
		CopyItem.closeCopyItem( self, params )
		BigWorld.globalData[ "TeamManager" ].teamRemoteCall( self.copyKey, "decSpaceCopyInfos", ( self._domain.name, ) )

class SpaceDomainCopyMapsTeam( SpaceDomainCopyMaps ):
	"""
	多地图组队副本
	"""
	def __init__( self ):
		SpaceDomainCopyMaps.__init__( self )
		self._spaceNumberToKey = {}
	
	def _getCoyKeyFromParams( self, params ):
		"""
		从参数里面获取副本的key
		"""
		return params.get( "teamID" )
	
	def createNewItem( self, teamID ):
		return CopyItemTeam( self, teamID )
	
	def nofityNotOnlineKick( self, copyKey, playerDBID ):
		"""
		define method
		副本内不在线的队员被踢
		"""
		self.kickNotOnlineMembers[ playerDBID ] = copyKey
	
	def nofityTeamDestroy( self, spaceNumber, teamEntityID ):
		"""
		define method
		通知队伍解散
		"""
		self.closeCopyItem( {"teamID":teamEntityID} )
	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		在玩家重新登录的时候被调用，用于让玩家在指定的space中出现（一般情况下为玩家最后下线的地图）；
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数；(domain条件)
		@type params : PY_DICT = None
		"""
		copyKey = self._getCoyKeyFromParams( params )
		copyItem = self.findCoyItem( copyKey )
		if copyItem and not self.isKickNotOnlineMember( copyItem.copyKey, params[ "dbID" ] ):
			copyItem.logon( baseMailbox, params )
		else:
			baseMailbox.logonSpaceInSpaceCopy()