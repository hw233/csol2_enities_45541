# -*- coding: gb18030 -*-
#
# 领取双倍奖励任务
#

from Function import Function
import BigWorld
import csdefine

class FuncMultiRewardQuest( Function ):
	"""
	领取活动奖励物品
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.itemID = section.readInt( "param1" )
		self.questID = section.readInt( "param2" )
		self.multiRate = section.readInt( "param3" )

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		item = player.findItemFromNKCK_( self.itemID )
		player.removeItem_( item.order, 1, csdefine.DELETE_ITEM_CIFU )	# 移除掉所需的物品
		player.setTemp( 'multi_rewards', 2 )
		player.questAcceptForce( player.id, self.questID, 0 )
		player.questsTable[self.questID].set( 'multi_rewards', self.multiRate )
		player.removeTemp( 'multi_rewards' )
		player.endGossip( talkEntity )
		

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
		item = player.findItemFromNKCK_( self.itemID )
		val1 = item is not None
		val2 = player.has_quest( self.questID )
		val3 = player.getQuest( self.questID ) is not None and player.getQuest( self.questID ).checkRequirement( player )
		return val1 and not val2 and val3
		