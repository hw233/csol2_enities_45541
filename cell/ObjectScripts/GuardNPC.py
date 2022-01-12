# -*- coding: gb18030 -*-

from bwdebug import *
from NPC import NPC
import csstatus
import csdefine

class GuardNPC( NPC ):
	"""
	����
	"""
	def __init__( self ):
		"""
		"""
		NPC.__init__( self )
		
		
	def doGoBack( self, selfEntity ):
		"""
		"""
		return selfEntity.gotoPosition(tuple( selfEntity.spawnPos ))
		
	def onWitnessed( self, selfEntity, isWitnessed ):
		"""
		This method is called when the state of this entity being witnessed changes.
		@param isWitnessed: A boolean indicating whether or not the entity is now witnessed;
		@type  isWitnessed: bool
		"""
		if isWitnessed:
			if selfEntity.initiativeRange > 0:
				self.onPlaceGuardTrap( selfEntity, 0, 0 )													# �����ݾ�
		else:
			guardProximityID = selfEntity.queryTemp( "guardProximityID", 0 )
			if guardProximityID != 0:
				selfEntity.cancel( guardProximityID )
				selfEntity.removeTemp( "guardProximityID" )
				selfEntity.removeTemp( "test_GuardProximity" )
		
	def onEnterTrapExt( self, selfEntity, entity, range, controllerID ):
		"""
		Entity.onEnterTrapExt( entity, range, controllerID )
		"""
		guardTrapID = selfEntity.queryTemp( "guardProximityID", 0 )
		if guardTrapID == 0 and controllerID != guardTrapID:
			return

		if self.checkEnterTrapEntityType( selfEntity, entity ):	# �����ҽ����ҵ���Ұ
			DEBUG_MSG( "%s(%i): %s into my initiativeRange." % ( selfEntity.getName(), selfEntity.id, entity.getName() ) )
			DEBUG_MSG( "my position =", selfEntity.position, "role position =", entity.position, "distance =", entity.position.distTo( selfEntity.position ), "my initiativeRange =", selfEntity.initiativeRange, "range =", range )
			selfEntity.aiTargetID = entity.id
			selfEntity.doAllEventAI( csdefine.AI_EVENT_ENTER_GUARD_TRAP )
			selfEntity.aiTargetID = 0
		
	def onPlaceGuardTrap( self, selfEntity, controllerID, userData ):
		"""
		timer for place trap
		called by MONENMITY_ADD_TRAP_TIMER_CBID
		"""
		if selfEntity.queryTemp( "guardProximityID", 0 ) == 0:
			selfEntity.setTemp( "test_GuardProximity", True )								# ���������Ҫ��Ҫ����շ�����ͱ�entity���뵼��onEnterTrapExt���ϵ��õ����
			id = selfEntity.addProximityExt( selfEntity.initiativeRange )						# �����һ�����壬����entity��������ʱ��onEnterTrapExt()���Զ�������
			if selfEntity.queryTemp( "test_GuardProximity", False ):
				selfEntity.setTemp( "guardProximityID", id )
				selfEntity.removeTemp( "test_GuardProximity" )
		
	def checkEnterTrapEntityType( self, selfEntity, entity ):
		"""
		�����������entity����
		"""
		# �Ƿ�Ϊ�жԹ�ϵ
		if selfEntity.queryRelation( entity ) != csdefine.RELATION_ANTAGONIZE:
			return False

		# ע�⣺getState()ȡ�õ�״̬��һ����real entity��״̬
		plState = entity.getState()
		# ��Ҵ�������״̬������״̬��ʲôҲ����
		if plState == csdefine.ENTITY_STATE_PENDING or plState == csdefine.ENTITY_STATE_QUIZ_GAME or plState == csdefine.ENTITY_STATE_DEAD:
			return False

		state = selfEntity.getState()
		if state != csdefine.ENTITY_STATE_FREE and state != csdefine.ENTITY_STATE_REST:
			return False

		# ������Ч������Χ�ڣ�ʲôҲ����
		if selfEntity.patrolList != None:
			if entity.position.distTo( selfEntity.position ) > selfEntity.territory:
				return False
		else:
			if entity.position.distTo( selfEntity.spawnPos ) > selfEntity.territory:
				return False

		# Ǳ����أ��Ƿ���⵽Ŀ��
		if not selfEntity.isRealLook( entity.id ):
			return False

		return True
		