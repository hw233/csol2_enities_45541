# -*- coding: gb18030 -*-
#
# $Id: $

import BigWorld
import csdefine
from bwdebug import DEBUG_MSG
from MonsterBuilding import MonsterBuilding


class MonsterYiJieZhanChangTower(MonsterBuilding):
	"""
	"""
	def __init__( self ):
		"""
		初始化
		"""
		MonsterBuilding.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_YI_JIE_ZHAN_CHANG_TOWER )
	
	def queryRelation( self, entity ):
		"""
		virtual method.
		取得自己与目标的关系
		@param entity: 任意目标entity
		@return : RELATION_*
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if self.isUseCombatCamp and entity.isUseCombatCamp:
			return MonsterBuilding.queryRelation( self, entity )
		
		if entity.utype == csdefine.ENTITY_TYPE_PET :
			owner = entity.getOwner()
			if owner.etype == "MAILBOX" :
				return csdefine.RELATION_NOFIGHT
			# 把宠物的敌对比较转嫁给它的主人
			# 虽然此关系未来可能会根据不同的状态或buff导致关系的改变，但当前并没有此需求
			entity = owner.entity

		if entity.utype == csdefine.ENTITY_TYPE_ROLE :
			if entity.yiJieFaction != 0 and self.battleCamp == entity.yiJieFaction :
				return csdefine.RELATION_FRIEND
		
		return MonsterBuilding.queryRelation( self, entity )