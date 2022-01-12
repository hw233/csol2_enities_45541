# -*- coding: gb18030 -*-

import BigWorld


class Domain_Fight:
	"""
	ս���������
	"""
	def buildEnemyRelation( self, combatUnitA, combatUnitB ):
		"""
		�����ж�ս����ϵ
		"""
		assert combatUnitA.planesID == combatUnitB.planesID
		combatUnitA.addEnemy( combatUnitB.id )
		combatUnitB.addEnemy( combatUnitA.id )

	def buildGroupEnemyRelation( self, combatUnitA, enmitys ):
		"""
		����һ��ж�ս����ϵ
		"""
		for enmityI in enmitys:
			assert combatUnitA.planesID == enmityI.planesID
			combatUnitA.addEnemy( enmityI.id )
			enmityI.addEnemy( combatUnitA.id )

	
	def buildGroupEnemyRelationByIDs( self, combatUnitA, enmityIDs ):
		"""
		����һ��ж�ս����ϵ
		"""
		for id in enmityIDs:
			enmityI = BigWorld.entities.get( id )
			if enmityI:
				assert combatUnitA.planesID == enmityI.planesID
				combatUnitA.addEnemy( id )
				enmityI.addEnemy( combatUnitA.id )
	
	
	def breakEnemyRelation( self, combatUnitA, combatUnitB ):
		"""
		����ж�ս����ϵ
		"""
		combatUnitA.removeEnemy( combatUnitB.id )
		combatUnitB.removeEnemy( combatUnitA.id )

	def removeEnemyByID( self, combatUnitA, enmityBID ):
		"""
		����ж�ս����ϵ
		"""
		combatUnitA.removeEnemy( enmityBID )

	def breakGroupEnemyRelationByIDs( self, combatUnitA, enmityIDs ):
		"""
		���һ��ж�ս����ϵ
		"""
		for id in enmityIDs:
			enmityI = BigWorld.entities.get( id )
			combatUnitA.removeEnemy( id )
			if enmityI:
				enmityI.removeEnemy( combatUnitA.id )


g_fightMgr = Domain_Fight()
