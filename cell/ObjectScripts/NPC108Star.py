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

class NPC108Star( Monster.Monster ):
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
		if selfEntity.state == csdefine.ENTITY_STATE_FIGHT:
				playerEntity.setGossipText(  cschannel_msgs.NIU_MO_WANG_VOICE_11)
				playerEntity.sendGossipComplete( selfEntity.id )
				return

		if dlgKey == "Talk":
			quest = playerEntity.getQuest( selfEntity.connectQuestID )
			if quest is None: return
			state = quest.query( playerEntity )

			if ( state == csdefine.QUEST_STATE_NOT_HAVE or state == csdefine.QUEST_STATE_NOT_ALLOW ) and \
				not playerEntity.questIsCompleted( selfEntity.connectQuestID ):
				playerEntity.setGossipText(cschannel_msgs.MONSTERACTIVITY_VOICE_1)
				playerEntity.sendGossipComplete( selfEntity.id )
			elif state == csdefine.QUEST_STATE_NOT_FINISH or playerEntity.questIsCompleted( selfEntity.connectQuestID ):
				playerEntity.setGossipText( cschannel_msgs.MONSTERACTIVITY_VOICE_2)
				playerEntity.addGossipOption(  "NPCStart.s1", cschannel_msgs.GOSSIP_14 )
				playerEntity.sendGossipComplete( selfEntity.id )

			elif state == csdefine.QUEST_STATE_FINISH:
				playerEntity.setGossipText(  cschannel_msgs.MONSTERACTIVITY_VOICE_3)
				playerEntity.sendGossipComplete( selfEntity.id )
			elif state == csdefine.QUEST_STATE_COMPLETE:
				playerEntity.setGossipText(  cschannel_msgs.MONSTERACTIVITY_VOICE_4)
				playerEntity.sendGossipComplete( selfEntity.id )

		elif dlgKey == "NPCStart.s1":
			quest = playerEntity.getQuest( selfEntity.connectQuestID )
			if quest is None: return
			state = quest.query( playerEntity )
			if state == csdefine.QUEST_STATE_NOT_FINISH or playerEntity.questIsCompleted( selfEntity.connectQuestID ):

				selfEntity.setAINowLevel( 1 )

				selfEntity.changeToMonster( selfEntity.level, playerEntity.id )
				selfEntity.callMonsters( playerEntity )
			# ��������е����⣬ֻ��״̬�洢��player���ϻ���ɶ��ˢ�ֵ����⣬����CSOL-9575
			# ������һ�����������ޣ�������ɱС�֣����޿��ܻ���ܲ�����ս��״̬����
			# ����ս���޻���ˢһ��С�� ���߻�˵�������⣬�����ʱ������ commented by mushuang
			playerEntity.endGossip( selfEntity )