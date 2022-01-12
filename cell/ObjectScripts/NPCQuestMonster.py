# -*- coding: gb18030 -*-
# $Id: NPC108Star.py,v 1.15 2008-07-28 09:19:09 zhangyuxing Exp $

import BigWorld
import cschannel_msgs
import ShareTexts as ST
import Monster
from bwdebug import *
import csdefine
import Language
import Resource.AIData
g_aiDatas = Resource.AIData.aiData_instance()


class NPCQuestMonster( Monster.Monster ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		Monster.Monster.__init__( self )



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
		if dlgKey == "Talk":
			quest = playerEntity.getQuest( selfEntity.connectQuestID )
			state = quest.query( playerEntity )

			if state == csdefine.QUEST_STATE_NOT_HAVE or state == csdefine.QUEST_STATE_NOT_ALLOW:
				playerEntity.setGossipText(cschannel_msgs.MONSTERACTIVITY_VOICE_7)
				playerEntity.sendGossipComplete( selfEntity.id )
			elif state == csdefine.QUEST_STATE_NOT_FINISH:
				playerEntity.setGossipText( cschannel_msgs.MONSTERACTIVITY_VOICE_8)
				playerEntity.addGossipOption(  "NPCStart.s1", cschannel_msgs.GOSSIP_14 )
				playerEntity.sendGossipComplete( selfEntity.id )

			elif state == csdefine.QUEST_STATE_FINISH:
				playerEntity.setGossipText(  cschannel_msgs.MONSTERACTIVITY_VOICE_9)
				playerEntity.sendGossipComplete( selfEntity.id )
			elif state == csdefine.QUEST_STATE_COMPLETE:
				playerEntity.setGossipText(  cschannel_msgs.MONSTERACTIVITY_VOICE_7)
				playerEntity.sendGossipComplete( selfEntity.id )

		elif dlgKey == "NPCStart.s1":
			quest = playerEntity.getQuest( selfEntity.connectQuestID )
			state = quest.query( playerEntity )
			if state == csdefine.QUEST_STATE_NOT_FINISH:
				selfEntity.setAINowLevel( 1 )
				selfEntity.changeToMonster( playerEntity.level, playerEntity.id )
			playerEntity.endGossip( selfEntity )


	def onLoadEntityProperties_( self, section ):
		"""
		virtual method. template method, call by GameObject::load().
		���ݸ�����section����ʼ������ȡ��entity���ԡ�
		ע��ֻ����createEntity()ʱ��Ҫ��ֵ�Զ���entity���г�ʼ��ʱ���б�Ҫ�ŵ��˺�����ʼ����
		Ҳ����˵�������ʼ�����������Զ�����������Ӧ��.def���������ġ�

		@param section: PyDataSection, ����һ���ĸ�ʽ�洢��entity���Ե�section
		"""
		Monster.Monster.onLoadEntityProperties_( self, section )