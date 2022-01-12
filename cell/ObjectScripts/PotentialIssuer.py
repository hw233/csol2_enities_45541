# -*- coding: gb18030 -*-
#
# $Id: PotentialIssuer.py,v 1.3 2008-06-19 08:55:14 kebiao Exp $


"""
pet's foster

2007/11/08 : writen by huangyongwei
"""

import csdefine
import cschannel_msgs
import ShareTexts as ST
import BigWorld
import csdefine
import NPC
import time
from bwdebug import *
from Resource.QuestLoader import QuestsFlyweight
quest = QuestsFlyweight.instance()

class PotentialIssuer( NPC.NPC ):
	"""
	Ǳ������NPC
	"""

	def __init__( self ):
		NPC.NPC.__init__( self )

	def questSelect( self, selfEntity, playerEntity, questID ):
		"""
		����ѡ��һ������
		"""
		quest = self.getQuest( questID )
		if quest.getType() == csdefine.QUEST_TYPE_POTENTIAL:
			quest.gossipWith( playerEntity, selfEntity, "Talk" )
		else:
			NPC.NPC.questSelect( self, selfEntity, playerEntity, questID )
		
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
		if self.questQuestionHandle( selfEntity, playerEntity, dlgKey ):
			return
		if dlgKey == "Talk":
			qcount = self.embedQuests( selfEntity, playerEntity )
			for qid in self._questStartList:
				if quest[ qid ].getType() == csdefine.QUEST_TYPE_POTENTIAL:
					state = self.questQuery( selfEntity, playerEntity, qid )
					playerEntity.addGossipQuestOption( qid, state )
			if self.dialog:
				self.dialog.doTalk( dlgKey, playerEntity, selfEntity )	
			playerEntity.sendGossipComplete( selfEntity.id )							
		else:
			if dlgKey[0:3] == "key":
				if self.dialog:
					self.dialog.doTalk( dlgKey, playerEntity, selfEntity )
					playerEntity.sendGossipComplete( selfEntity.id )
			else:
				for qid in self._questStartList:
					if quest[ qid ].getType() == csdefine.QUEST_TYPE_POTENTIAL:
						quest[ qid ].gossipWith( playerEntity, selfEntity, dlgKey )
					
	def embedQuests( self, selfEntity, player ):
		"""
		Ƕ��ָ��������п�����ʾ������
		"""
		quests = []
		for id in self._questStartList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			state = self.questQuery( selfEntity, player, id )
			#����ʾ���������ӻ����Ѿ���ɵ�����
			if state != csdefine.QUEST_STATE_NOT_ALLOW and state != csdefine.QUEST_STATE_COMPLETE:
				if self.hasFinishQuest( id ) and state == csdefine.QUEST_STATE_FINISH:
					#����������ͬʱҲ�ǽ��Ķ��������Ѿ����Խ��� ��ô�����뿪ʼ�б�
					continue
				if quest.getType() == csdefine.QUEST_TYPE_POTENTIAL:
					continue
				#���������NPC �����С�����Ŀ��δ��ɶԻ�������ʾ������ѡ���ҵ������ʾ������Ŀ��δ��ɶԻ���

				if state == csdefine.QUEST_STATE_FINISH:
					#������ʾ������
					continue
				if not quest.hasOption():
					continue
				quests.append( id )
				player.addGossipQuestOption( id, state )

		for id in self._questFinishList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			if quest.getType() == csdefine.QUEST_TYPE_POTENTIAL:
				continue				
			
			state = self.questQuery( selfEntity, player, id )
			#��ʾ�����ѽӣ���δ�������Ŀ�� �������ѽӣ������������Ŀ��
			if state in [csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH]:
				if self.hasStartQuest( id ) and state != csdefine.QUEST_STATE_FINISH:   #���NPCͬʱҲ�Ƿ������������ˣ���ôֻ��������ɿɽ�������
					continue
				quests.append( id )
				player.addGossipQuestOption( id, state )
		return quests					

	def questQuery( self, selfEntity, playerEntity, questID ):
		"""
		��ѯ��Ҷ�ĳһ������Ľ���״̬��
		@return: ����ֵ������鿴common���QUEST_STATE_*
		@rtype:  UINT8
		"""
		quest = self.getQuest( questID )
		if quest.getType() == csdefine.QUEST_TYPE_POTENTIAL:
			qids = playerEntity.findQuestByType( csdefine.QUEST_TYPE_POTENTIAL )	
			if len( qids ) > 0:
				questID = qids[0]
				
		return NPC.NPC.questQuery( self, selfEntity, playerEntity, questID )

	def getQuestStateLevel( self, player ):
		"""
		"""
		return NPC.NPC.getQuestStateLevel( self, player)
		
# $Log: not supported by cvs2svn $
# Revision 1.2  2008/02/18 08:52:47  kebiao
# Ǳ���������
#
# Revision 1.1  2008/01/28 06:12:36  kebiao
# no message
#
#