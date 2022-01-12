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
		与玩家对话；未声明(不能声明)的方法，因此重载此方法的上层如果需要访问自己的私有属性请自己判断self.isReal()。

		@param   selfEntity: 与自己对应的Entity实例，传这个参数是为了方便以后的扩充
		@type    selfEntity: Entity
		@param playerEntity: 说话的玩家
		@type  playerEntity: Entity
		@param       dlgKey: 对话关键字
		@type        dlgKey: str
		@return: 无
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
		根据给定的section，初始化（读取）entity属性。
		注：只有在createEntity()时需要把值自动对entity进行初始化时才有必要放到此函数初始化，
		也就是说，这里初始化的所有属性都必须是在相应的.def中声明过的。

		@param section: PyDataSection, 根据一定的格式存储了entity属性的section
		"""
		Monster.Monster.onLoadEntityProperties_( self, section )