# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus
import items
import random

g_items = items.instance()

class FuncTakeHonorGift( Function ):
	"""
	荣誉度兑换物品
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.itemID01 	= section.readInt( "param1" )										#物品ID
		self.itemID02 	= section.readInt( "param2" )										#物品ID
		self.honor		= section.readInt( "param3" )										#荣誉值


	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		if player.honor < self.honor:
			player.client.onStatusMessage( csstatus.HONOR_NOT_ENOUGH, str(( self.honor, )) )
			return
		
		itemID = random.choice([self.itemID01, self.itemID02])
		item = g_items.createDynamicItem( itemID, 1 )
		checkResult = player.checkItemsPlaceIntoNK_( [item] )
		if checkResult != csdefine.KITBAG_CAN_HOLD:
			player.client.onStatusMessage( csstatus.KITBAG_IS_FULL, "" )
			return
		
		player.subHonor( self.honor, 0 )
		item.set( "level", player.level )
		player.addItem( item, csdefine.ADD_ITEM_FOR_HONOR_GIFT )

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

