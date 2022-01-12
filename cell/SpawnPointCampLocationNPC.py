# -*- coding: gb18030 -*-
from SpawnPointActivity import SpawnPointActivity

class SpawnPointCampLocationNPC( SpawnPointActivity ):
	def __init__( self ):
		SpawnPointActivity.__init__( self )
	
	def onLocationOccuped( self ):
		"""
		define method
		据点被攻占
		"""
		self.getScript().onLocationOccuped( self )
		
	def recoverLocation( self ):
		"""
		define method
		据点恢复
		"""
		self.getScript().onLocationOccuped( self )