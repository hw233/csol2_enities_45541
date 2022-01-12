# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import csconst
import csstatus
import time

class FuncSetCityRevenueRate( Function ):
	"""
	1.2	调整税率
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

	def do( self, player, talkEntity = None ):
		"""
		进入猰貐副本。
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		spaceName = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if player.tong_holdCity == spaceName:
			if player.isTongChief():
				BigWorld.globalData[ "TongManager" ].onRequestSetCityRevenueRate(player.base, player.tong_dbID, spaceName)
			else:
				player.statusMessage( csstatus.TONG_CITY_REVENUE_NO_CHIEF )
		else:
			player.statusMessage( csstatus.TONG_CITY_REVENUE_ERR )
				
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
		return True
