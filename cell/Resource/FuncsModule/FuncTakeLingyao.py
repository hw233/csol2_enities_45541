# -*- coding: gb18030 -*-
#

"""
"""
from Function import Function
import BigWorld
import csdefine
import time
import csstatus

class FuncTakeLingyao( Function ):
	"""
	领取灵药
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._itemID = section.readInt( "param1" )

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
		lastTakeTime = player.queryRoleRecord( "takeLingyaoTime" )

		lt = time.localtime()
		curT = str(lt[1]) + "+" + str(lt[2] )

		if lastTakeTime == curT:
			player.client.onStatusMessage( csstatus.LINGYAO_FORBID_GET_ALREADY, "" )
			return

		if player.getNormalKitbagFreeOrderCount() < 1:
			player.client.onStatusMessage( csstatus.KITBAG_IS_FULL, "" )
			return

		lingyaoItem = player.createDynamicItem( self._itemID )
		lingyaoCount = lingyaoItem.getOnlyLimit()
		if not player.addItemAndNotify_( lingyaoItem, csdefine.ADD_ITEM_TAKELINGYAO ):
			player.client.onStatusMessage( csstatus.LINGYAO_IS_FULL, str(( lingyaoCount, )) )
			return
		player.setRoleRecord( "takeLingyaoTime", curT )


	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		@return: True/False
		@rtype:	bool
		"""
		return True


