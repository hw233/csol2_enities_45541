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
		��ʼ��
		"""
		MonsterBuilding.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_YI_JIE_ZHAN_CHANG_TOWER )
	
	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ
		@param entity: ����Ŀ��entity
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
			# �ѳ���ĵжԱȽ�ת�޸���������
			# ��Ȼ�˹�ϵδ�����ܻ���ݲ�ͬ��״̬��buff���¹�ϵ�ĸı䣬����ǰ��û�д�����
			entity = owner.entity

		if entity.utype == csdefine.ENTITY_TYPE_ROLE :
			if entity.yiJieFaction != 0 and self.battleCamp == entity.yiJieFaction :
				return csdefine.RELATION_FRIEND
		
		return MonsterBuilding.queryRelation( self, entity )