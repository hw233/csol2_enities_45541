# -*- coding: gb18030 -*-
#
# $Id: $

import BigWorld
import csdefine
from MonsterBuilding import MonsterBuilding


class MonsterYiJieZhanChangTower(MonsterBuilding):
	"""
	"""
	def __init__( self ):
		"""
		初始化
		"""
		MonsterBuilding.__init__( self )
	
	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系
		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		# 对手是宠物
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return MonsterBuilding.queryRelation( self, entity )
		
		if entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			owner = entity.getOwner()
			if owner is None:
				return csdefine.RELATION_NOFIGHT
			else:
				entity = owner

		# 对手是人，是否同一异界战场阵营判定
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
			if entity.yiJieFaction != 0 and self.battleCamp == entity.yiJieFaction :
				return csdefine.RELATION_FRIEND
			else :
				return csdefine.RELATION_ANTAGONIZE
		
		return csdefine.RELATION_NEUTRALLY