# -*- coding: gb18030 -*-


import BigWorld
import NPC


class TiShouNPC( NPC.NPC ):
	"""
	"""	
	def __init__( self ):
		"""
		"""
		NPC.NPC.__init__( self )
		
		
	
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
			selfEntity.queryTSInfo( playerEntity.id )
		else:
			playerEntity.endGossip( selfEntity )