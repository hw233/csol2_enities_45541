# -*- coding: gb18030 -*-


from SpaceDomainCopyTeam import SpaceDomainCopyTeam

class SpaceDomainPig( SpaceDomainCopyTeam ):
	"""
	����
	"""
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		"""
		spaceItem = self.findSpaceItem( params, False )
		if spaceItem:
			spaceItem.logon( baseMailbox )
		else:
			baseMailbox.logonSpaceInSpaceCopy()


