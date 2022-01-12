# -*- coding: gb18030 -*-
# $Id: Exp $

from Monster import Monster
import ECBExtend
import csdefine

BOSS_ID = "20154003"	# 乌足督军

class MonsterRecover( Monster ):
	"""
	出生25秒后为督军恢复15%血量，恢复后自己立即死亡
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.addTimer( 25.0, 0, ECBExtend.MONSTER_RECOVER_CBID )

	def onRecoverTimer( self, controllerID, userData ):
		"""
		MONSTER_RECOVER_CBID的callback函数；
		"""
		if self.getState() == csdefine.ENTITY_STATE_DEAD:	# 如果已经死亡
			return
		
		for entity in self.entitiesInRangeExt( 30.0, "Monster", self.position ):
			if entity.className == BOSS_ID:
				entity.setHP( min( entity.HP_Max, int( entity.HP + entity.HP_Max * 0.15 ) ) )
				self.destroy()
