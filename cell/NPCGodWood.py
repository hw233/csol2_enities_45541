# -*- coding: gb18030 -*-

from Monster import Monster

class NPCGodWood( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )

	def onHPChanged( self ):
		"""
		HP���ı�ص�
		"""
		Monster.onHPChanged( self )
		self.getCurrentSpaceBase().cell.onGodWoodHPChange( self.HP, self.HP_Max )