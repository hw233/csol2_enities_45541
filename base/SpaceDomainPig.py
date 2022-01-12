# -*- coding: gb18030 -*-


from SpaceDomainCopyTeam import SpaceDomainCopyTeam

class SpaceDomainPig( SpaceDomainCopyTeam ):
	"""
	嘟嘟猪活动
	"""
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		"""
		spaceItem = self.findSpaceItem( params, False )
		if spaceItem:
			spaceItem.logon( baseMailbox )
		else:
			baseMailbox.logonSpaceInSpaceCopy()


