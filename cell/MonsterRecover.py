# -*- coding: gb18030 -*-
# $Id: Exp $

from Monster import Monster
import ECBExtend
import csdefine

BOSS_ID = "20154003"	# ���㶽��

class MonsterRecover( Monster ):
	"""
	����25���Ϊ�����ָ�15%Ѫ�����ָ����Լ���������
	"""
	def __init__( self ):
		"""
		"""
		Monster.__init__( self )
		self.addTimer( 25.0, 0, ECBExtend.MONSTER_RECOVER_CBID )

	def onRecoverTimer( self, controllerID, userData ):
		"""
		MONSTER_RECOVER_CBID��callback������
		"""
		if self.getState() == csdefine.ENTITY_STATE_DEAD:	# ����Ѿ�����
			return
		
		for entity in self.entitiesInRangeExt( 30.0, "Monster", self.position ):
			if entity.className == BOSS_ID:
				entity.setHP( min( entity.HP_Max, int( entity.HP + entity.HP_Max * 0.15 ) ) )
				self.destroy()
