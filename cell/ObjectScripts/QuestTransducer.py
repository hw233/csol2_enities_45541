# -*- coding: gb18030 -*-
#
# $Id: QuestTransducer.py,v 1.8 2008-05-19 07:26:36 phw Exp $

"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
import csdefine

# ȫ�ֵ����Գ�ʼ����Ӧ��
g_propsMap = (
				( "visible",					lambda section, key: section[key].asInt ),			# �Ƿ�ɼ�
				( "radius",						lambda section, key: section[key].asFloat ),		# �����뾶
			)

START_QUEST = [20101032, 20101039, 20101046, 20101053, 20101060, 20101061, 20101062, 20101063]

class QuestTransducer( NPCObject ):
	"""
	���񴫸�����
	������ҽӽ�������ʱ�Զ��������������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		NPCObject.__init__( self )

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		NPCObject.onLoadEntityProperties_( self, section )
		self.setEntityProperty( "visible",		section["visible"].asInt )			# �Ƿ�ɼ�
		self.setEntityProperty( "radius",		section["radius"].asFloat )			# �����뾶

	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
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
		if entity.__class__.__name__ != "Role":
			return
		if not entity.isReal():
			INFO_MSG( "Dest entity(%i/%s) not a real entity, I will foreward the call." % ( entity.id, entity.getName() ) )
			# Զ�̽ű�����
			# ֮���Բ�������ͬonEnterTrapExt()�ӿڣ���Ϊ�˱���onEnterTrapExt()���ӻ���
			# ��Ϊ���ʹ��ͬһ��onEnterTrapExt()�ӿڣ�����Ҫ�жϴ�������entity������һ��entity����mailbox��
			entity.forwardScriptCall( self.className, "remoteEnterTrap", ( selfEntity.id, entity.id, range, userData ) )
			return
		for questID in self._questFinishList:
			q = self.getQuest( questID )
			if q.query( entity ) == csdefine.QUEST_STATE_FINISH:
				q.complete( entity, 0 )

		for questID in self._questStartList:
			q = self.getQuest( questID )
			if q.query( entity ) == csdefine.QUEST_STATE_NOT_HAVE:
				q.accept( entity )
#				if questID in START_QUEST :	# ���ܵ���һ����������ʱ���������
#					entity.delayCall( 1, "showQuestLog", questID )

	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		����ҶԻ���δ����(��������)�ķ�����������ش˷������ϲ������Ҫ�����Լ���˽���������Լ��ж�self.isReal()��

		@param   selfEntity: ���Լ���Ӧ��Entityʵ���������������Ϊ�˷����Ժ������
		@type    selfEntity: Entity
		@param playerEntity: ˵�������
		@type  playerEntity: Entity
		@param       dlgKey: �Ի��ؼ���
		@type        dlgKey: str
		@return: ��
		"""
		# ��ǰɶ����������������Ϊ�˽�ֹ�ײ�ĵ���
		return # the end

# end of QuestTransducer.py
