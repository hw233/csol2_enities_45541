# -*- coding: gb18030 -*-
# SlaveMonster.py
# $Id: 0.py,v 1.1 2008-09-01 03:34:03 kebiao Exp $

from Monster import Monster
import csdefine
import csstatus
import BigWorld
from interface.CombatUnit import CombatUnit
from TongNagual import TongNagual
import random
from bwdebug import *
import csconst 
import ECBExtend
from Domain_Fight import g_fightMgr

class TongCampaignMonster( Monster ):
	"""
	�������
	"""
	def __init__(self):
		Monster.__init__( self )
		
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		Monster.initEntity( self, selfEntity )
		selfEntity.addTimer( 17 * 60, 0, ECBExtend.DESTROY_SELF_TIMER_CBID )
		shenshouID = selfEntity.queryTemp( "shenshouID", 0 )
		if shenshouID > 0:
			shenshou = BigWorld.entities.get(shenshouID)
			if shenshou:
				g_fightMgr.buildEnemyRelation( selfEntity, shenshou )
		selfEntity.think( 0.1 )
		
	def queryRelation( self, selfEntity, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ

		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		if not selfEntity.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
			
		if selfEntity.isUseCombatCamp and entity.isUseCombatCamp:
			return Monster.queryRelation( self, selfEntity, entity )
		
		if entity.id == selfEntity.id:
			return csdefine.RELATION_FRIEND		
		elif not isinstance( entity, CombatUnit ):
			return csdefine.RELATION_FRIEND
		elif entity.isState( csdefine.ENTITY_STATE_PENDING ):
			return csdefine.RELATION_NOFIGHT
		elif entity.isState( csdefine.ENTITY_STATE_QUIZ_GAME ):
			return csdefine.RELATION_NOFIGHT
		elif entity.effect_state & csdefine.EFFECT_STATE_PROWL:	# ���entity����Ǳ��Ч��״̬
			return csdefine.RELATION_NOFIGHT
		elif entity.isEntityType( csdefine.ENTITY_TYPE_PET ):
			return csdefine.RELATION_ANTAGONIZE
		elif entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
			return csdefine.RELATION_ANTAGONIZE
		elif entity.isEntityType( csdefine.ENTITY_TYPE_MONSTER ):
			return csdefine.RELATION_ANTAGONIZE
		elif isinstance( entity, TongNagual ):
			return csdefine.RELATION_ANTAGONIZE
			
		return csdefine.RELATION_FRIEND

	def onEnterTrapExt( self, selfEntity, entity, range, controllerID ):
		"""
		Entity.onEnterTrapExt( entity, range, controllerID )
		"""
		# ����entity �����������巶Χ֮�ڣ��˺����ͻᱻ����
		state = selfEntity.getState()
		if state == csdefine.ENTITY_STATE_FIGHT:						# ��Ϣ״̬.....�ƺ�û���õ�
			# ��ս��״̬��ʱ��ȡ���ݾ�
			selfEntity.cancel( controllerID )
			return
		if selfEntity.getSubState() == csdefine.M_SUB_STATE_GOBACK:
			return

		if entity.isEntityType( csdefine.ENTITY_TYPE_ROLE ) or entity.isEntityType( csdefine.ENTITY_TYPE_PET ) or isinstance( entity, TongNagual ):	# �����ҽ����ҵ���Ұ
			# ע�⣺getState()ȡ�õ�״̬��һ����real entity��״̬
			plState = entity.getState()
			if plState == csdefine.ENTITY_STATE_PENDING or plState == csdefine.ENTITY_STATE_DEAD or plState == csdefine.ENTITY_STATE_QUIZ_GAME:
				return												# ��Ҵ�������״̬/����״̬/�ʴ�״̬��ʲôҲ����
			if state == csdefine.ENTITY_STATE_FREE or state == csdefine.ENTITY_STATE_REST:
				assert selfEntity.targetID == 0, "in csdefine.ENTITY_STATE_FREE, have attack target!"
				if entity.position.distTo( selfEntity.spawnPos ) > selfEntity.territory:
					return											# ������Ч������Χ�ڣ�ʲôҲ����
				DEBUG_MSG( "%s(%i): %s into my initiativeRange, I will attack it." % ( selfEntity.getName(), selfEntity.id, entity.getName() ) )
				DEBUG_MSG( "my position =", selfEntity.position, "role position =", entity.position, "distance =", entity.position.distTo( selfEntity.position ), "my initiativeRange =", selfEntity.initiativeRange, "range =", range )
				selfEntity.aiTargetID = entity.id
				selfEntity.doAllEventAI( csdefine.AI_EVENT_SPELL_ENTERTRAP )
				if selfEntity.targetID <= 0:
					selfEntity.doAllAI()
				selfEntity.aiTargetID = 0
	
	def campaignOver( self, selfEntity ):
		"""
		define method.
		�������
		"""
		selfEntity.destroy()

	def afterDie( self, selfEntity, killerID ):
		"""
		virtual method.

		������ص���ִ��һЩ�����ڹ�����������������顣
		"""
		Monster.afterDie( self, selfEntity, killerID )
		selfEntity.getCurrentSpaceBase().onCappaign_monsterRaidComplete( selfEntity.level, selfEntity.getName() )

	def canThink( self, selfEntity ):
		"""
		virtual method.
		�ж��Ƿ����think
		"""
		if selfEntity.state == csdefine.ENTITY_STATE_DEAD or selfEntity.isDestroyed: 									# ������ֹͣthink
			return False
		if selfEntity.getSubState() == csdefine.M_SUB_STATE_GOBACK: 					# ���Ŀǰû����ҿ����һ����ڻ��ߣ���ô�ҽ�ֹͣthink
			return False
		return True
		
#
# $Log: not supported by cvs2svn $
