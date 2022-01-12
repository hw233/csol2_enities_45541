# -*- coding: gb18030 -*-
#

"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
from ObjectScripts.GameObjectFactory import g_objFactory
import csdefine

class ChallengeTransducer( NPCObject ):
	"""
	������ս��������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		NPCObject.__init__( self )
		self._spawnMonsterList = []

	def initEntity( self, selfEntity ):
		# ����ɶ�¶�����ֻ�ǽ��õײ�Ĵ���
		pass

	def remoteEnterTrap( self, selfEntityID, entityID, range, userData ):
		"""
		һ��������תonEnterTrapExt()��Ϣ�ĺ������˷����ᱻԶ�̵��ã����onEnterTrapExt()����
		"""
		selfEntity = BigWorld.entities.get( selfEntityID )
		entity = BigWorld.entities.get( entityID )
		if selfEntity is None or entity is None:
			ERROR_MSG( "remote call fail. selfEntityID = %i(%s), entityID = %i(%s)." % (
					selfEntityID, ("found", "not found")[selfEntity is None], 
					entityID,     ("found", "not found")[entity is None] ) )
			return
		self.onEnterTrapExt( selfEntity, entity, range, userData )

	def onEnterTrapExt( self, selfEntity, entity, range, userData ):
		"""
		This method is associated with the Entity.addProximity method.
		It is called when an entity enters a proximity trap of this entity.
		@param selfEntity:	ȫ��ʵ�������entityʵ��
		@param entity:		The entity that has entered.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		if entity.getEntityType() != csdefine.ENTITY_TYPE_ROLE:
			return
				
		if not entity.isReal():
			INFO_MSG( "Dest entity(%i/%s) not a real entity, I will foreward the call." % ( entity.id, entity.getName() ) )
			# Զ�̽ű�����
			# ֮���Բ�������ͬonEnterTrapExt()�ӿڣ���Ϊ�˱���onEnterTrapExt()���ӻ���
			# ��Ϊ���ʹ��ͬһ��onEnterTrapExt()�ӿڣ�����Ҫ�жϴ�������entity������һ��entity����mailbox��
			entity.forwardScriptCall( self.className, "remoteEnterTrap", ( selfEntity.id, entity.id, range, userData ) )
			return

		selfEntity.getCurrentSpaceBase().startTrapSpawnEntity( selfEntity.trapID )
		selfEntity.destroy()