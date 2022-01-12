# -*- coding: gb18030 -*-

from Monster import Monster
import csdefine
from bwdebug import *
from Attack import Attack

class MonsterBelongTeam( Monster, Attack ):
	def __init__( self ):
		Monster.__init__( self )
		Attack.__init__( self )
	
	def queryRelation( self, entity ):
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, entity )
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			return csdefine.RELATION_NEUTRALLY

		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			# GM观察者模式
			if entity.effect_state & csdefine.EFFECT_STATE_WATCHER:
				return csdefine.RELATION_NOFIGHT
			
			if entity.teamID == self.belong:
				return csdefine.RELATION_FRIEND
			else:
				return csdefine.RELATION_ANTAGONIZE

		return csdefine.RELATION_NEUTRALLY
