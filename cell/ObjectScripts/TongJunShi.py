# -*- coding: gb18030 -*-
#
# $Id: NPC.py,v 1.65 2008-09-03 07:04:17 kebiao Exp $

"""
NPC基类
"""

import BigWorld
from bwdebug import *
import csdefine
import csstatus
from NPC import NPC

MIN_SIGN_LEVEL = 99999999			#最低等级
LEVEL_MINUS = 10					#等级限制

class TongJunShi( NPC ):
	"""
	帮会军师
	"""
	def __init__( self ):
		"""
		初始化从XML读取信息
		"""
		NPC.__init__( self )

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
		if selfEntity.ownTongDBID != playerEntity.tong_dbID:
			playerEntity.statusMessage( csstatus.TONG_NPC_IS_TARGET_TONG_NPC )
			return
		elif selfEntity.locked:
			playerEntity.statusMessage( csstatus.TONG_NPC_LOCKED )
			return			
		NPC.gossipWith( self, selfEntity, playerEntity, dlgKey )

	def questStatus( self, selfEntity, playerEntity ):
		"""
		查询一个游戏对象所有任务相对于玩家的状态，状态将通过回调返回给client相对应的GameObject。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 玩家
		@type  playerEntity: Entity
		@return: 无
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
			if ( player.level - quest.getLevel() > LEVEL_MINUS and quest.getStyle() == csdefine.QUEST_STYLE_NORMAL  ) and (questId in self._questStartList ):								#低于玩家10及以上的可接任务将不显示任务标识
				continue
			curState = quest.query( player )
			questType = quest.getType()
			if questType == csdefine.QUEST_TYPE_TONG_FETE and not selfEntity.feteOpen :
				curState = csdefine.QUEST_STATE_NOT_ALLOW
			stateL = [csdefine.QUEST_STATE_NOT_HAVE, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH]

			if  (questId in self._questStartList and curState in[csdefine.QUEST_STATE_NOT_ALLOW, csdefine.QUEST_STATE_NOT_HAVE] ) or (questId in self._questFinishList and curState in stateL[1:] ):
				tempId = quest.getType()*10 + curState	# *10主要用于计算出和配置对应的signID
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
		嵌入指定玩家所有可以显示的任务。
		"""
		#quests = []
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
				#如果接任务NPC 任务有“任务目标未完成对话”，显示该任务选项，玩家点击后显示“任务目标未完成对话”
				if state == csdefine.QUEST_STATE_FINISH:
					#否则不显示该任务
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
			#显示任务已接，但未完成任务目标 和任务已接，且已完成任务目标
			if state in [csdefine.QUEST_STATE_NOT_FINISH, csdefine.QUEST_STATE_FINISH, csdefine.QUEST_STATE_DIRECT_FINISH]:
				if self.hasStartQuest( id ) and state != csdefine.QUEST_STATE_FINISH:   #如果NPC同时也是发行这个任务的人，那么只有任务完成可交才做事
					continue
				player.addGossipQuestOption( id, state )
		#return quests
		
# NPC.py
