# -*- coding: gb18030 -*-


from SpaceDomainCopy import SpaceDomainCopy

class SpaceDomainRabbitRun( SpaceDomainCopy ):
	"""
	小兔快跑活动
	"""
	def __init__( self ):
		SpaceDomainCopy.__init__( self )


	def teleportEntityOnLogin( self, baseMailbox, params ):
		"""
		"""
		baseMailbox.logonSpaceInSpaceCopy()

