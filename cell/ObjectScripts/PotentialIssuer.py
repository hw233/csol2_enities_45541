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
	潜能任务NPC
	"""

	def __init__( self ):
		NPC.NPC.__init__( self )

	def questSelect( self, selfEntity, playerEntity, questID ):
		"""
		请求选择一个任务
		"""
		quest = self.getQuest( questID )
		if quest.getType() == csdefine.QUEST_TYPE_POTENTIAL:
			quest.gossipWith( playerEntity, selfEntity, "Talk" )
		else:
			NPC.NPC.questSelect( self, selfEntity, playerEntity, questID )
		
	def gossipWith( self, selfEntity, playerEntity, dlgKey ):
		"""
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
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
		嵌入指定玩家所有可以显示的任务。
		"""
		quests = []
		for id in self._questStartList:
			quest = self.getQuest( id )
			if quest == None:
				continue
			state = self.questQuery( selfEntity, player, id )
			#不显示不够条件接或者已经完成的任务
			if state != csdefine.QUEST_STATE_NOT_ALLOW and state != csdefine.QUEST_STATE_COMPLETE:
				if self.hasFinishQuest( id ) and state == csdefine.QUEST_STATE_FINISH:
					#如果这个任务同时也是交的而且任务已经可以交了 那么不加入开始列表
					continue
				if quest.getType() == csdefine.QUEST_TYPE_POTENTIAL:
					continue
				#如果接任务NPC 任务有“任务目标未完成对话”，显示该任务选项，玩家点击后显示“任务目标未完成对话”

				if state == csdefine.QUEST_STATE_FINISH:
					#否则不显示该任务
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
			#显示任务已接，但未完成任务目标 和任务已接，且已完成任务目标
			if state in [csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH]:
				if self.hasStartQuest( id ) and state != csdefine.QUEST_STATE_FINISH:   #如果NPC同时也是发行这个任务的人，那么只有任务完成可交才做事
					continue
				quests.append( id )
				player.addGossipQuestOption( id, state )
		return quests					

	def questQuery( self, selfEntity, playerEntity, questID ):
		"""
		查询玩家对某一个任务的进行状态。
		@return: 返回值类型请查看common里的QUEST_STATE_*
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
# 潜能任务调整
#
# Revision 1.1  2008/01/28 06:12:36  kebiao
# no message
#
#