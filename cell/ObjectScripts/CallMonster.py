# -*- coding: gb18030 -*-

from Monster import Monster


class CallMonster( Monster ):
	"""
	召唤类怪物
	"""
	def __init__( self ):
		Monster.__init__( self )
		
	def onMonsterDie( self, selfEntity, killerID ):
		self.dieNotify( selfEntity, killerID )