# -*- coding: gb18030 -*-
from SpawnPointActivity import SpawnPointActivity

class SpawnPointCampLocationNPC( SpawnPointActivity ):
	def __init__( self ):
		SpawnPointActivity.__init__( self )
	
	def onLocationOccuped( self ):
		"""
		define method
		�ݵ㱻��ռ
		"""
		self.getScript().onLocationOccuped( self )
		
	def recoverLocation( self ):
		"""
		define method
		�ݵ�ָ�
		"""
		self.getScript().onLocationOccuped( self )