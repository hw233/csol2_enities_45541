# -*- coding: gb18030 -*-

from SpaceDomainCopyTeam import SpaceDomainCopyTeam

class SpaceDomainYXLM( SpaceDomainCopyTeam ):
	"""
	英雄联盟副本
	"""
	def __init__( self ):
		SpaceDomainCopyTeam.__init__( self )
		
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
		SpaceDomainCopyTeam.teleportEntity( self, position, direction, baseMailbox, params )
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