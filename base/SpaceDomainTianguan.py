# -*- coding: gb18030 -*-


from SpaceDomainCopyTeam import SpaceDomainCopyTeam

class SpaceDomainTianguan( SpaceDomainCopyTeam ):
	"""
	闯天关
	"""
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		"""
		baseMailbox.logonSpaceInSpaceCopy()

