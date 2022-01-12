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
	�����ȶһ���Ʒ
	"""
	def __init__( self, section ):
		"""
		@param param: ��ʵ�����Լ����͸�ʽ; param1 - param5
		@type  param: pyDataSection
		"""
		self.itemID01 	= section.readInt( "param1" )										#��ƷID
		self.itemID02 	= section.readInt( "param2" )										#��ƷID
		self.honor		= section.readInt( "param3" )										#����ֵ


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
		���һ�������Ƿ����ʹ��

		@param player: ���
		@type  player: Entity
		@param  talkEntity: һ����չ�Ĳ���
		@type   talkEntity: entity
		@return: True/False
		@rtype:	bool
		"""
		return True

