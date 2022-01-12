# -*- coding: gb18030 -*-

import BigWorld


class Domain_Fight:
	"""
	战斗规则管理
	"""
	def buildEnemyRelation( self, combatUnitA, combatUnitB ):
		"""
		建立敌对战斗关系
		"""
		assert combatUnitA.planesID == combatUnitB.planesID
		combatUnitA.addEnemy( combatUnitB.id )
		combatUnitB.addEnemy( combatUnitA.id )

	def buildGroupEnemyRelation( self, combatUnitA, enmitys ):
		"""
		建立一组敌对战斗关系
		"""
		for enmityI in enmitys:
			assert combatUnitA.planesID == enmityI.planesID
			combatUnitA.addEnemy( enmityI.id )
			enmityI.addEnemy( combatUnitA.id )

	
	def buildGroupEnemyRelationByIDs( self, combatUnitA, enmityIDs ):
		"""
		建立一组敌对战斗关系
		"""
		for id in enmityIDs:
			enmityI = BigWorld.entities.get( id )
			if enmityI:
				assert combatUnitA.planesID == enmityI.planesID
				combatUnitA.addEnemy( id )
				enmityI.addEnemy( combatUnitA.id )
	
	
	def breakEnemyRelation( self, combatUnitA, combatUnitB ):
		"""
		解除敌对战斗关系
		"""
		combatUnitA.removeEnemy( combatUnitB.id )
		combatUnitB.removeEnemy( combatUnitA.id )

	def removeEnemyByID( self, combatUnitA, enmityBID ):
		"""
		解除敌对战斗关系
		"""
		combatUnitA.removeEnemy( enmityBID )

	def breakGroupEnemyRelationByIDs( self, combatUnitA, enmityIDs ):
		"""
		解除一组敌对战斗关系
		"""
		for id in enmityIDs:
			enmityI = BigWorld.entities.get( id )
			combatUnitA.removeEnemy( id )
			if enmityI:
				enmityI.removeEnemy( combatUnitA.id )


g_fightMgr = Domain_Fight()
