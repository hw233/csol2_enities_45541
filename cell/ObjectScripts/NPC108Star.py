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
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
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
			# 这里可能有点问题，只把状态存储在player身上会造成多次刷怪的问题，例如CSOL-9575
			# （比如一个人拉走星宿，其他人杀小怪，星宿可能会回跑并脱离战斗状态），
			# 再挑战星宿会再刷一波小怪 但策划说不是问题，因此暂时不处理。 commented by mushuang
			playerEntity.endGossip( selfEntity )