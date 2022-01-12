# -*- coding: gb18030 -*-

from SpaceDomainCopyTeam import SpaceDomainCopyTeam

class SpaceDomainYXLM( SpaceDomainCopyTeam ):
	"""
	Ӣ�����˸���
	"""
	def __init__( self ):
		SpaceDomainCopyTeam.__init__( self )
		
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
		SpaceDomainCopyTeam.teleportEntity( self, position, direction, baseMailbox, params )
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