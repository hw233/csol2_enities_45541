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
		������븱��
		"""
		CopyItem.enter( self, domain, position, direction, baseMailbox, params )
	
	def logon( self, baseMailbox, params ):
		"""
		��ҵ�½
		"""
		baseMailbox.logonSpaceInSpaceCopy()
	
	def closeCopyItem( self, params ):
		"""
		�رո���
		"""
		CopyItem.closeCopyItem( self, params )
		BigWorld.globalData[ "TeamManager" ].teamRemoteCall( self.copyKey, "decSpaceCopyInfos", ( self._domain.name, ) )

class SpaceDomainCopyMapsTeam( SpaceDomainCopyMaps ):
	"""
	���ͼ��Ӹ���
	"""
	def __init__( self ):
		SpaceDomainCopyMaps.__init__( self )
		self._spaceNumberToKey = {}
	
	def _getCoyKeyFromParams( self, params ):
		"""
		�Ӳ��������ȡ������key
		"""
		return params.get( "teamID" )
	
	def createNewItem( self, teamID ):
		return CopyItemTeam( self, teamID )
	
	def nofityNotOnlineKick( self, copyKey, playerDBID ):
		"""
		define method
		�����ڲ����ߵĶ�Ա����
		"""
		self.kickNotOnlineMembers[ playerDBID ] = copyKey
	
	def nofityTeamDestroy( self, spaceNumber, teamEntityID ):
		"""
		define method
		֪ͨ�����ɢ
		"""
		self.closeCopyItem( {"teamID":teamEntityID} )
	
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		define method.
		��������µ�¼��ʱ�򱻵��ã������������ָ����space�г��֣�һ�������Ϊ���������ߵĵ�ͼ����
		@param baseMailbox: entity ��base mailbox
		@type baseMailbox : MAILBOX, 
		@param params: һЩ���ڸ�entity����space�Ķ��������(domain����)
		@type params : PY_DICT = None
		"""
		copyKey = self._getCoyKeyFromParams( params )
		copyItem = self.findCoyItem( copyKey )
		if copyItem and not self.isKickNotOnlineMember( copyItem.copyKey, params[ "dbID" ] ):
			copyItem.logon( baseMailbox, params )
		else:
			baseMailbox.logonSpaceInSpaceCopy()