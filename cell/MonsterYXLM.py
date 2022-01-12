# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from MonsterBelongTeam import MonsterBelongTeam
from MonsterBuilding import MonsterBuilding
from interface.CombatUnit import CombatUnit
from bwdebug import *

class MonsterYXLM( MonsterBelongTeam, MonsterBuilding ) :
	"""
	Ӣ�����˹���������أ�
	"""
	def __init__( self ):
		MonsterBelongTeam.__init__( self )
		MonsterBuilding.__init__( self )
		self.setEntityType( csdefine.ENTITY_TYPE_MONSTER_BELONG_TEAM )
		self.getSpaceCell().registMonster( self.className, self )
	
	def getSpaceCell( self ):
		sMB = self.getCurrentSpaceBase()
		if sMB:
			try:
				return BigWorld.entities[sMB.id]
			except KeyError:
				return sMB.cell
			
	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		�����˺���
		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skillID: ����ID
		@type     skillID: INT
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: INT
		@param     damage: �˺���ֵ
		@type      damage: INT
		"""
		if self.hasFlag( csdefine.ENTITY_FLAG_SPEAKER ):
			return
		if self.hasFlag( csdefine.ENTITY_FLAG_CAN_NOT_SELECTED ):		#���ɱ�ѡ��Ĺ�������������﹥��������������Һͳ��﹥����
			obj = BigWorld.entities.get( casterID )
			if obj and ( obj.isEntityType( csdefine.ENTITY_TYPE_PET ) or obj.isEntityType( csdefine.ENTITY_TYPE_ROLE ) ):
				return

		state = self.getState()
		subState = self.getSubState()
		hasCaster = BigWorld.entities.has_key( casterID )

		# ����״̬ʱ���޵�״̬ ������
		if subState == csdefine.M_SUB_STATE_GOBACK or state == csdefine.ENTITY_STATE_DEAD or \
		( hasCaster and BigWorld.entities[ casterID ].getState() == csdefine.ENTITY_STATE_DEAD ):
			return

		if not( damageType & csdefine.DAMAGE_TYPE_FLAG_BUFF ) and hasCaster:	# ����buff�˺���ʩ���ߴ���
			killerEntity = BigWorld.entities[casterID]
			# ��һ�����ӳ�޶ȣ���Ȼ�����ս��״̬
			if killerEntity.getState() != csdefine.ENTITY_STATE_DEAD:
				if damageType & csdefine.DAMAGE_TYPE_FLAG_BUFF != csdefine.DAMAGE_TYPE_FLAG_BUFF:
					self.addDamageList( killerEntity.id, damage )
		
			# ����˺�����0
			if damage > 0 and casterID != self.id:
				self.bootyOwner = ( casterID, 0 )
				if not self.firstBruise:
					self.firstBruise = 1
					self.onFirstBruise( killerEntity, damage, skillID )
		else:
			# û�й���Դ���˺���buff����
			pass
		# ���֪ͨ�ײ㣬��Ϊ�����֪ͨ�˵ײ㣬��ô�����ﱻһ����ɱ��ʱ��ܿ�����������û����ս��״̬
		# ����������Ļ�����Щ�����Ͳ�������Ч������
		CombatUnit.receiveDamage( self, casterID, skillID, damageType, damage )
	
	def sendSAICommand( self, recvIDs, type, sid ):
		"""
		����saiָ��
		"""
		self.getSpaceCell().sendSAICommand( recvIDs, type, sid, self )
	
	def recvSAICommand( self, type, sid, sendEntity ):
		"""
		define method.
		����һ��entity��������s ai
		"""
		self.setTemp( "SEND_SAI_ENTITY", sendEntity )
		self.insertSAI( sid )

	def openVolatileInfo( self ):
		"""
		virtual method.
		��������Ϣ���͹���
		"""
		MonsterBuilding.openVolatileInfo( self )

	def closeVolatileInfo( self ):
		"""
		virtual method.
		�ر�������Ϣ���͹���
		"""
		MonsterBuilding.closeVolatileInfo( self )
		
	def moveToPosFC( self, endDstPos, targetMoveSpeed, targetMoveFace ):
		"""
		�����ƶ�
		"""
		MonsterBuilding.moveToPosFC( self, endDstPos, targetMoveSpeed, targetMoveFace )
	
	def checkViewRange( self, entity ):
		"""
		virtual method
		���entity�Ƿ�����Ұ��Χ
		�ж�entity�Ƿ����Լ�����Ұ��Χ֮��
		return 	:	True	��
		return	:	False	����
		"""
		if entity.spaceID != self.spaceID:
			return False
		return True
