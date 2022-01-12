# -*- coding: gb18030 -*-
import BigWorld

class UseDomainForTeamInter( object ):
	"""
	����domian��team�ӿ�
	��һ���Ƕ��鸱���ż̳����������ӿ�ֻ�Ǳ�ʾ·������صĸ���
	"""
	def __init__( self ):
		object.__init__( self )
		self.kickNotOnlineMembers = {}
	
	def setTeamRelation( self, teamEntityID, spaceNumber ):
		"""
		����ĳ��space�����Ĺ�ϵ
		"""
		BigWorld.globalData[ "TeamManager" ].teamRemoteCall( teamEntityID, "addSpaceCopyInfos", ( self.name, spaceNumber ) )
	
	def removeTeamRelation( self, teamEntityID ):
		"""
		ɾ��ĳ��space�Ķ����ϵ
		"""
		BigWorld.globalData[ "TeamManager" ].teamRemoteCall( teamEntityID, "decSpaceCopyInfos", ( self.name, ) )
	
	def nofityNotOnlineKick( self, spaceNumber, playerDBID ):
		"""
		define method
		�����ڲ����ߵĶ�Ա����
		"""
		self.kickNotOnlineMembers[ playerDBID ] = spaceNumber
	
	def isKickNotOnlineMember( self, spaceNumber, playerDBID ):
		"""
		�ǲ��Ƕ����߳�ȥ�����
		"""
		if self.kickNotOnlineMembers.has_key( playerDBID ):
			if self.kickNotOnlineMembers[ playerDBID ] == spaceNumber:
				return True
			else:
				return False
	
	def clearKickNotOnlineMember( self, playerDBID ):
		"""
		���ָ����ҵ���������
		"""
		if self.kickNotOnlineMembers.has_key( playerDBID ):
			del self.kickNotOnlineMembers[ playerDBID ]
	
	def nofityTeamDestroy( self, spaceNumber, teamEntityID ):
		"""
		define method
		֪ͨ�����ɢ
		"""
		spaceItem = self.getSpaceItem( spaceNumber )
		if spaceItem:
			spaceItem.baseMailbox.nofityTeamDestroy( teamEntityID )
#

class UseTeamForDomainInter( object ):
	# ����ӿ�
	def __init__( self ):
		object.__init__( self )
		self.openCopyInfos = {} # �����������ĸ�����Ϣ
		
	def addSpaceCopyInfos( self, spaceType, spaceNumber ):
		"""
		define method
		��Ӷ��鿪����������Ϣ
		"""
		self.openCopyInfos[ spaceType ] = spaceNumber
	
	def decSpaceCopyInfos( self, spaceType ):
		"""
		define method
		ȥ�����鿪����������Ϣ
		"""
		if self.openCopyInfos.has_key( spaceType ):
			del self.openCopyInfos[ spaceType ]
	
	def desSpaceCopyNotify( self ):
		"""
		֪ͨ���������ɢ
		"""
		for k, n in self.openCopyInfos.iteritems():
			BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( k, "nofityTeamDestroy", ( n, self.id ) )
	
	def kcikNotOnline( self, playerDBID ):
		"""
		ͨ�������������ߵ�ĳ����ұ��߳�����
		"""
		for k, n in self.openCopyInfos.iteritems():
			BigWorld.globalData[ "SpaceManager" ].remoteCallDomain( k, "nofityNotOnlineKick", ( n, playerDBID ) )