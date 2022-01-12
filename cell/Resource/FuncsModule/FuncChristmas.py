# -*- coding: gb18030 -*-
#

from Function import Function
import BigWorld
import csdefine

import Const
import items
import csconst
import random
import csstatus

g_items = items.instance()

class FuncChristmasSocks( Function ):
	"""
	领取圣诞袜子
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )	# 圣诞袜子ID01
		self._param2 = section.readInt( "param2" )	# 圣诞袜子ID02

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
		
		if player.level < 10:
			player.client.onStatusMessage( csstatus.CHRISTMAS_SOCKS_FORBID_LEVEL, "" )
			return
		spaceLabel = BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY )
		if spaceLabel in Const.CHRISTMAS_AREA_FLAGS:
			flag = Const.CHRISTMAS_AREA_FLAGS[spaceLabel]
		else:
			flag = 31
		if player.isActivityCanNotJoin( csdefine.ACTIVITY_CMS_SOCKS ) :
			player.client.onStatusMessage( csstatus.CHRISTMAS_SOCKS_FORBID_REPEAT, "" )
			return
		
		item = g_items.createDynamicItem( random.choice( [self._param1, self._param2] ), 1 )
		
		item.set( "level", player.level )
		
		checkReult = player.checkItemsPlaceIntoNK_( [item] )
		if checkReult != csdefine.KITBAG_CAN_HOLD :
			player.client.onStatusMessage( csstatus.KITBAG_IS_FULL, "" )
			return
		player.addActivityCount( csdefine.ACTIVITY_CMS_SOCKS )
		player.addItem( item, csdefine.ADD_ITEM_QUEST )



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


