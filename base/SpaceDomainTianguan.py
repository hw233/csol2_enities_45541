# -*- coding: gb18030 -*-


from SpaceDomainCopyTeam import SpaceDomainCopyTeam

class SpaceDomainTianguan( SpaceDomainCopyTeam ):
	"""
	�����
	"""
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		"""
		baseMailbox.logonSpaceInSpaceCopy()

