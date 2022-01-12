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
		��ʼ��
		"""
		MonsterBuilding.__init__( self )
	
	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ
		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		# �����ǳ���
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

		# �������ˣ��Ƿ�ͬһ���ս����Ӫ�ж�
		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) :
			if entity.yiJieFaction != 0 and self.battleCamp == entity.yiJieFaction :
				return csdefine.RELATION_FRIEND
			else :
				return csdefine.RELATION_ANTAGONIZE
		
		return csdefine.RELATION_NEUTRALLY