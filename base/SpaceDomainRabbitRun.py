# -*- coding: gb18030 -*-


from SpaceDomainCopy import SpaceDomainCopy

class SpaceDomainRabbitRun( SpaceDomainCopy ):
	"""
	С�ÿ��ܻ
	"""
	def __init__( self ):
		SpaceDomainCopy.__init__( self )


	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		"""
		baseMailbox.logonSpaceInSpaceCopy()

