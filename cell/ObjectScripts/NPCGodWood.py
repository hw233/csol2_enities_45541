# -*- coding: gb18030 -*-

from Monster import Monster

class NPCGodWood( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )

	def onHPChanged( self, selfEntity ):
		"""
		HP���ı�ص�
		"""
		selfEntity.getCurrentSpaceBase().cell.onGodWoodHPChange( selfEntity.HP, selfEntity.HP_Max )