# -*- coding: gb18030 -*-

"""
"""

import BigWorld
from bwdebug import *
from NPCObject import NPCObject
import csdefine
from QuestTransducer import QuestTransducer
import random


class RandomQuestTransducer( QuestTransducer ):
	"""
	���񴫸�����
	������ҽӽ�������ʱ�Զ����������
	"""
	def __init__( self ):
		"""
		��ʼ��
		"""
		QuestTransducer.__init__( self )

	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		QuestTransducer.onLoadEntityProperties_( self, section )
		
		position = []
		positionSection = section["randomPosition"]
		if positionSection:
			positions = positionSection.readVector3s( "item" )
			for p in positions:
				position.append( p )
		self.setEntityProperty( "randomPosition", position )											# ���λ��
		
		self.setEntityProperty( "triggerInterval",		section.readInt( "triggerInterval") )			# �������
		self.setEntityProperty( "triggerRate",			section.readFloat( "triggerRate") )				# ��������
		
		self.questID = section.readInt( "questID" )														# ����ID
		
	def initEntity( self, selfEntity ):
		"""
		virtual method. Template method.
		��ʼ���Լ���entity������
		"""
		# ����ɶ�¶�����ֻ�ǽ��õײ�Ĵ���
		pass

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
		quest = self.getQuest( self.questID )
		if quest and quest.query( entity ) == csdefine.QUEST_STATE_NOT_HAVE:
			entity.client.showQuestTrapTip( selfEntity.id )# ��������󵯳���ʾ��Ϣ
			entity.setTemp("LeaveQuestTrapError",selfEntity.id) #������ʱ��� �������뿪�ݽ��쳣 
			
	def onTipClicked( self, entity ):
		"""
		��ҵ������������˸��ʾ�Ĵ���
		@param entity:		The entity that has clicked the tip.
		"""
		quest = self.getQuest( self.questID )
		if quest and quest.query( entity ) == csdefine.QUEST_STATE_NOT_HAVE:
			quest.gossipDetail( entity, None )										# ���������ȡ����

	def onLeaveTrapExt( self, selfEntity, entity, range, userData ):
		"""
		����뿪����ʱ�Ĵ�����ر���ʾ��Ϣ
		@param selfEntity:	ȫ��ʵ�������entityʵ��
		@param entity:		The entity that has entered.
		@param range:		The range of the trigger.
		@param userData:	The user data that was passed to Entity.addProximity.
		"""
		if entity.__class__.__name__ != "Role":
			return
		if selfEntity.randomPosition :
			selfEntity.position = selfEntity.randomPosition[random.randint( 0, len( selfEntity.randomPosition ) -1 ) ]		# �ı������λ��
		try:
			entity.client.hideQuestTrapTip( selfEntity.id )# �ر���ʾ��Ϣ
			entity.removeTemp("LeaveQuestTrapError")
		except:
			ERROR_MSG("Role has onleave RandomQuestTransducer error!")	
		

# end of RandomQuestTransducer.py
