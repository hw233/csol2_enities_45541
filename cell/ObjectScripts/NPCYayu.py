# -*- coding: gb18030 -*-

from Monster import Monster

class NPCYayu( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		
	def onMonsterDie( self, selfEntity, killerID ):
		"""
		"""
		self.dieNotify( selfEntity, killerID )