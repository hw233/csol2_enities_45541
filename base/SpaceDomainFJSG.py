# -*- coding: gb18030 -*-


from SpaceDomainCopyTeam import SpaceDomainCopyTeam

class SpaceDomainFJSG( SpaceDomainCopyTeam ):
	"""
	封剑神宫
	"""
	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		"""
		baseMailbox.logonSpaceInSpaceCopy()
