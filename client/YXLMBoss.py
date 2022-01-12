# -*- coding: gb18030 -*-

from bwdebug import INFO_MSG
from Monster import Monster
import event.EventCenter as ECenter
from Attack import Attack


class YXLMBoss( Monster, Attack ) :
	def __init__( self ):
		Monster.__init__( self )
		Attack.__init__( self )

	def set_damage_min( self, oldValue ) :
		"""
		最小伤害值改变
		"""
		INFO_MSG( "[ID:%i]damage_min change %f" % ( self.id, self.damage_min ) )
		ECenter.fireEvent( "EVT_ON_TARGET_POWER_CHANGED", self.id, self.averageDamage() )

	def set_damage_max( self, oldValue ) :
		"""
		最大伤害值改变
		"""
		INFO_MSG( "[ID:%i]damage_max change %f" % ( self.id, self.damage_max ) )
		ECenter.fireEvent( "EVT_ON_TARGET_POWER_CHANGED", self.id, self.averageDamage() )

	def averageDamage( self ) :
		"""
		平均伤害
		"""
		return (self.damage_min + self.damage_max)/2
	
	def queryRelation( self, entity ):
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return csdefine.RELATION_NEUTRALLY

		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			return csdefine.RELATION_NEUTRALLY

		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			if entity.teamID == self.belong:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_NEUTRALLY