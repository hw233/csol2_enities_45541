# -*- coding: gb18030 -*-

"""
"""
import csstatus
import cschannel_msgs
import ShareTexts as ST
import sys
import csdefine
from Function import Function

class FuncTreasureMap( Function ):
	"""
	实现与NPC对话时得到一张模糊的纸条
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._reqLevel = section.readInt( "param1" )
		self._reqMoney = section.readInt( "param2" )
		self._itemID = section.readInt( "param3" )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		if self._reqLevel > player.level:
			player.statusMessage( csstatus.ROLE_TELPORT_NOT_ENOUGH_LEVEL, self._reqLevel )
			return
		if self._reqMoney > 0:
			if not player.payMoney( self._reqMoney, csdefine.CHANGE_MONEY_TREASUREMAP ):
				player.setGossipText( cschannel_msgs.TONGCITYWAR_VOICE_15 )
				player.sendGossipComplete( talkEntity.id )
				return
		item = player.createDynamicItem( self._itemID )
		player.addItem( item, csdefine.ADD_ITEM_QUEST )			# 给玩家一个模糊的纸条
		item.generateLocation( player )	# 生成宝藏位置坐标
		Function.do( self, player, talkEntity )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

