# -*- coding: gb18030 -*-
# $Id: Exp $

from Monster import Monster


class MonsterShuijing( Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )


	def onDie( self, killerID ):
		"""
		virtual method.

		死亡事情处理。
		
		"""
		if self.className == "20752011":	#红水晶死亡，使用自曝（这个方式比技能合适）
			for i in self.entitiesInRangeExt( 5.0, "Role", self.position ):
				i.setHP( int( i.HP * 0.8 ) )
			for i in self.entitiesInRangeExt( 5.0, "Pet", self.position ):
				i.setHP( int( i.HP * 0.8 ) )

		Monster.onDie( self, killerID )
		
		