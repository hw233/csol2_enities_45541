# -*- coding:gb18030 -*-

from Function import Function
import csstatus
import csdefine
from bwdebug import *
import Const
import BigWorld

class FuncGetFruit( Function ):
	"""
	七夕魅力果树种子领取
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._itemID = section.readInt( "param1" )

	def valid( self, playerEntity, talkEntity = None ):
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

	def do( self, playerEntity, talkEntity = None ):
		"""
		执行一个功能

		@param playerEntity: 玩家
		@type  playerEntity: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		playerEntity.endGossip( talkEntity )
		if talkEntity is None:
			ERROR_MSG( "player( %s ) talk entity is None." % player.getName() )
			return
		# 判定活动是否开启
		if not BigWorld.globalData.has_key( "FruitStart" ):
			playerEntity.statusMessage( csstatus.ROLE_TANABATA_QUIZ_NOT_START )
			return

		# 判定玩家是否领取当天的奖励
		lastTakeTime = playerEntity.queryRoleRecord( "getFruitTime" )
		lt = time.localtime()
		curT = str( lt[1] ) + "+" + str( lt[2] )

		if lastTakeTime == curT:
			playerEntity.client.onStatusMessage( csstatus.FRUIT_HAVE_GET, "" )
			return

		item = playerEntity.createDynamicItem( self._itemID )
		if item is None: return

		checkReult = playerEntity.checkItemsPlaceIntoNK_( [item] )
		if checkReult != csdefine.KITBAG_CAN_HOLD:
			playerEntity.statusMessage( csstatus.FRUIT_GET_BAG_FULL )
			return
		playerEntity.addItem( item, reason = csdefine.ADD_ITEM_GET_FRUIT )
		playerEntity.setRoleRecord( "getFruitTime", curT )