# -*- coding: gb18030 -*-
from SpawnPointNormal import SpawnPointNormal

class SpawnPointCopy( SpawnPointNormal ):
	def __init__( self ):
		SpawnPointNormal.__init__( self )
		
	def getName( self ):
		"""
		virtual method.
		@return: the name of entity
		@rtype:  STRING
		"""
		return self.className