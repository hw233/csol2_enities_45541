# -*- coding: gb18030 -*-
import BigWorld
from SpaceDomainCopy import SpaceDomainCopy
import csdefine

class SpaceDomainYXLMPVP( SpaceDomainCopy ):
	"""
	Ӣ�����˸���
	"""
	def __init__( self ):
		SpaceDomainCopy.__init__( self )
	
	def createSpaceItem( self, param ):
		"""
		virtual method.
		ģ�巽����ʹ��param���������µ�spaceItem
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
		ģ�巽����ɾ��spaceItem
		"""
		SpaceDomainCopy.removeSpaceItem( self, spaceNumber )
		for teamID, number in self.keyToSpaceNumber.iteritems():
			if number == spaceNumber:
				BigWorld.globalData[ "TeamManager" ].teamRemoteCall( teamID, "decSpaceCopyInfos", ( self.name, ) )
				del self.keyToSpaceNumber[ teamID ]
	
	def teleportEntity( self, position, direction, baseMailbox, params ):
		"""
		define method.
		����һ��entity��ָ����space��
		@type position : VECTOR3, 
		@type direction : VECTOR3, 
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ�������� (domain����)
		@type params : PY_DICT = None
		"""
		SpaceDomainCopy.teleportEntity( self, position, direction, baseMailbox, params )
		self.teleportTeamMembers( position, direction, baseMailbox, params )
	
	def teleportTeamMembers( self, position, direction, baseMailbox, params ):
		"""
		�Ѷ��Ѵ��븱��
		"""
		if params.has_key( "membersMailboxs" ):
			membersMailboxs = params.pop( "membersMailboxs" )
			
			for tMB in membersMailboxs:
				if tMB.id == baseMailbox.id:
					continue
					
				tMB.cell.gotoSpace( self.name, position, direction )
	
	def nofityTeamDestroy( self, spaceNumber, teamEntityID ):
		"""
		֪ͨ�����ɢ
		"""
		spaceItem = self.getSpaceItem( spaceNumber )
		if spaceItem:
			spaceItem.baseMailbox.nofityTeamDestroy( teamEntityID )
	
		
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		��������һ�����򿪷ŵģ� ��˲������½���ܹ�����һ��
		�����Լ������ĸ����У� ���������Ӧ�÷��ص���һ�ε�½�ĵط�
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