# -*- coding: gb18030 -*-
import BigWorld
from SpaceDomainCopy import SpaceDomainCopy
import csdefine

class SpaceDomainYXLMPVP( SpaceDomainCopy ):
	"""
	英雄联盟副本
	"""
	def __init__( self ):
		SpaceDomainCopy.__init__( self )
	
	def createSpaceItem( self, param ):
		"""
		virtual method.
		模板方法；使用param参数创建新的spaceItem
		"""
		teamInfos = param.get( "teamInfos" )
		spaceItem = SpaceDomainCopy.createSpaceItem( self, param )
		for teamID in teamInfos:
			self.keyToSpaceNumber[teamID] = spaceItem.spaceNumber
			
	#	self.keyToSpaceNumber[ teamInfos ] = spaceItem
		BigWorld.globalData[ "TeamManager" ].teamRemoteCall( teamInfos[0], "addSpaceCopyInfos", ( self.name, spaceItem.spaceNumber ) )
		BigWorld.globalData[ "TeamManager" ].teamRemoteCall( teamInfos[1], "addSpaceCopyInfos", ( self.name, spaceItem.spaceNumber ) )
		return spaceItem
	
	def removeSpaceItem( self, spaceNumber ):
		"""
		virtual method.
		模板方法；删除spaceItem
		"""
		SpaceDomainCopy.removeSpaceItem( self, spaceNumber )
		for teamID, number in self.keyToSpaceNumber.iteritems():
			if number == spaceNumber:
				BigWorld.globalData[ "TeamManager" ].teamRemoteCall( teamID, "decSpaceCopyInfos", ( self.name, ) )
				del self.keyToSpaceNumber[ teamID ]
	
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		传送一个entity到指定的space中
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity 的base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: 一些关于该entity进入space的额外参数； (domain条件)
		@type params : PY_DICT = None
		"""
		SpaceDomainCopy.teleportEntity( self, position, direction, baseMailbox, params )
		self.teleportTeamMembers( position, direction, baseMailbox, params )
	
	def teleportTeamMembers( self, position, direction, baseMailbox, params ):
		"""
		把队友传入副本
		"""
		if params.has_key( "membersMailboxs" ):
			membersMailboxs = params.pop( "membersMailboxs" )
			
			for tMB in membersMailboxs:
				if tMB.id == baseMailbox.id:
					continue
					
				tMB.cell.gotoSpace( self.name, position, direction )
	
	def nofityTeamDestroy( self, spaceNumber, teamEntityID ):
		"""
		通知队伍解散
		"""
		spaceItem = self.getSpaceItem( spaceNumber )
		if spaceItem:
			spaceItem.baseMailbox.nofityTeamDestroy( teamEntityID )
	
		
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		副本是由一定规则开放的， 因此不允许登陆后能够呆在一个
		不是自己开启的副本中， 遇到此情况应该返回到上一次登陆的地方
		"""
		spaceItem = self.findSpaceItem( params, False )
		dbid = params[ "dbID" ]
		if spaceItem:
			if not self.isKickNotOnlineMember( spaceItem.spaceNumber, dbid ):
				spaceItem.logon( baseMailbox )
				self.clearKickNotOnlineMember( dbid )
				return
		
		self.clearKickNotOnlineMember( dbid )	
		baseMailbox.logonSpaceInSpaceCopy()