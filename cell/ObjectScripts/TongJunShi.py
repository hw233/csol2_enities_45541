# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC����
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
from NPC import NPC

MIN_SIGN_LEVEL = 99999999			#��͵ȼ�
LEVEL_MINUS = 10					#�ȼ�����

class TongJunShi( NPC ):
	"""
	����ʦ
	"""
	def __init__( self ):
		"""
		��ʼ����XML��ȡ��Ϣ
		"""
		NPC.__init__( self )

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
		if selfEntity.ownTongDBID != playerEntity.tong_dbID:
			playerEntity.statusMessage( csstatus.TONG_NPC_IS_TARGET_TONG_NPC )
			return
		elif selfEntity.locked:
			playerEntity.statusMessage( csstatus.TONG_NPC_LOCKED )
			return			
		NPC.gossipWith( self, selfEntity, playerEntity, dlgKey )

	def questStatus( self, selfEntity, playerEntity ):
		"""
		��ѯһ����Ϸ�������������������ҵ�״̬��״̬��ͨ���ص����ظ�client���Ӧ��GameObject��

		@param   selfEntity: ���Լ���Ӧ��Entityʵ���������������Ϊ�˷����Ժ������
		@type    selfEntity: Entity
		@param playerEntity: ���
		@type  playerEntity: Entity
		@return: ��
		"""

		level,signID = self.getQuestStateLevel(selfEntity, playerEntity)
		playerEntity.clientEntity( selfEntity.id ).onQuestStatus( signID )
		
	def getQuestStateLevel( self, selfEntity, player ):
		"""
		"""
		signID = -1
		level = MIN_SIGN_LEVEL
		
		sign_levels = [(level,signID)]
		questList = list(self._questStartList) + list(self._questFinishList)

		for questId in questList:
			quest = self.getQuest( questId )
			if quest == None or quest.getType() == csdefine.QUEST_TYPE_MEMBER_DART:
				continue
			if player.tong_dbID != selfEntity.ownTongDBID:
				continue
			if ( player.level - quest.getLevel() > LEVEL_MINUS and quest.getStyle() == csdefine.QUEST_STYLE_NORMAL  ) and (questId in self._questStartList ):								#�������10�����ϵĿɽ����񽫲���ʾ�����ʶ
				continue
			curState = quest.query( player )
			questType = quest.getType()
			if questType == csdefine.QUEST_TYPE_TONG_FETE and not selfEntity.feteOpen :
				curState = csdefine.QUEST_STATE_NOT_ALLOW
			stateL = [csdefine.QUEST_STATE_NOT_HAVE, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH]

			if  (questId in self._questStartList and curState in[csdefine.QUEST_STATE_NOT_ALLOW, csdefine.QUEST_STATE_NOT_HAVE] ) or (questId in self._questFinishList and curState in stateL[1:] ):
				tempId = quest.getType()*10 + curState	# *10��Ҫ���ڼ���������ö�Ӧ��signID
				try:
					tempLevel = self._npcQuestSignData[ tempId ][ 'level' ]
				except KeyError:
					continue
				if tempLevel < level:
					level = tempLevel
					signID = tempId	
			sign_levels.append(( level,signID))
		sign_levels.sort()
		sign_level = sign_levels[0]
		return ( sign_level )
		
	def embedQuests( self, selfEntity, player ):
		"""
		Ƕ��ָ��������п�����ʾ������
		"""
		#quests = []
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
				#���������NPC �����С�����Ŀ��δ��ɶԻ�������ʾ������ѡ���ҵ������ʾ������Ŀ��δ��ɶԻ���
				if state == csdefine.QUEST_STATE_FINISH:
					#������ʾ������
					continue
				if not quest.hasOption():
					continue
				if quest.getType() == csdefine.QUEST_TYPE_TONG_FETE and not selfEntity.feteOpen:
					continue
				player.addGossipQuestOption( id, state )

		for id in self._questFinishList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			state = self.questQuery( selfEntity, player, id )
			#��ʾ�����ѽӣ���δ�������Ŀ�� �������ѽӣ������������Ŀ��
			if state in [csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH]:
				if self.hasStartQuest( id ) and state != csdefine.QUEST_STATE_FINISH:   #���NPCͬʱҲ�Ƿ������������ˣ���ôֻ��������ɿɽ�������
					continue
				player.addGossipQuestOption( id, state )
		#return quests
		
# NPC.py
