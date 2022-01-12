# -*- coding: gb18030 -*-

from gbref import rds
from Monster import Monster
class NPCYayu( Monster ):
	def __init__( self ):
		Monster.__init__( self )
		
	def onKillAllMonster( self ):
		"""
		define method
		"""
		rds.actionMgr.playActions( self.getModel(), ["start","standing"] )