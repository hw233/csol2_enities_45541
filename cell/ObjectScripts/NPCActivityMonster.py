# -*- coding: gb18030 -*-
# $Id: NPC108Star.py,v 1.15 2008-07-28 09:19:09 zhangyuxing Exp $

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from csconst import g_maps_info
import BigWorld
import Monster
import csdefine
import Language
import Resource.AIData
import csconst

g_aiDatas = Resource.AIData.aiData_instance()

class NPCActivityMonster( Monster.Monster ):
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
			if playerEntity.getState() == csdefine.ENTITY_STATE_FIGHT:
				playerEntity.setGossipText(cschannel_msgs.MONSTERACTIVITY_VOICE_5)
				playerEntity.sendGossipComplete( selfEntity.id )
				return
			if selfEntity.getState() != csdefine.ENTITY_STATE_FREE:
				playerEntity.endGossip( selfEntity )
				return
			spaceLabel = playerEntity.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			playerEntity.setGossipText(cschannel_msgs.MONSTERACTIVITY_VOICE_6% g_maps_info[spaceLabel] )
			playerEntity.addGossipOption(  "NPCStart.s1", cschannel_msgs.GOSSIP_11 )
			playerEntity.addGossipOption(  "NPCStart.s2", cschannel_msgs.GOSSIP_12 )
			playerEntity.sendGossipComplete( selfEntity.id )


		elif dlgKey == "NPCStart.s1":
			if selfEntity.getState() != csdefine.ENTITY_STATE_FREE:
				playerEntity.endGossip( selfEntity )
				return

			selfEntity.setAINowLevel( 1 )
			selfEntity.changeToMonster( playerEntity.level, playerEntity.id )

			selfEntity.callMonsters( playerEntity )
			playerEntity.endGossip( selfEntity )


		elif dlgKey == "NPCStart.s2":
			playerEntity.endGossip( selfEntity )