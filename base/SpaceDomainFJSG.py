# -*- coding: gb18030 -*-


from SpaceDomainCopyTeam import SpaceDomainCopyTeam

class SpaceDomainFJSG( SpaceDomainCopyTeam ):
	"""
	�⽣��
	"""
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		"""
		baseMailbox.logonSpaceInSpaceCopy()
