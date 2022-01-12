# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
import time
import BigWorld
import random
import csstatus
import csdefine
from Function import Function
from csconst import Start_Positions
import csconst
import Const

from VehicleHelper import getCurrVehicleID

class FuncRabbitRun( Function ):
	"""
	小兔快跑
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self._param1 = section.readInt( "param1" )

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

		if player.level < self._param1:
			player.statusMessage( csstatus.ROLE_HAS_NOT_RACEHORSE_LEVEL )
			return

		if player.isActivityCanNotJoin( csdefine.ACTIVITY_RUN_RABBIT ) :
			player.statusMessage( csstatus.ROLE_HAS_FULL_RABBITRUN_TODAY )
			return

		if not BigWorld.globalData.has_key( "AS_RabbitRun" ):
			if BigWorld.globalData.has_key( "AS_RabbitRun_Start_Time" ):
				if BigWorld.globalData["AS_RabbitRun_Start_Time"] - csconst.RABBIT_RUN_WAIT_TIME + csconst.RABBIT_RUN_ACTIVITY_TIME > time.time():
					player.client.onStatusMessage( csstatus.RABBITRUN_HAS_START, "" )
				else:
					player.client.onStatusMessage( csstatus.RABBITRUN_NOT_BEGIN, "" )
			else:
				player.client.onStatusMessage( csstatus.RABBITRUN_NOT_BEGIN, "" )
			return

		if player.vehicle or getCurrVehicleID( player ):
			player.client.onStatusMessage( csstatus.RABBITRUN_FORBID_VEHICLE_STATE, "" )
			return

		if player.qieCuoState != csdefine.QIECUO_NONE:
			player.client.onStatusMessage( csstatus.RABBITRUN_FORBID_PK_STATE, "" )
			return

		# 潜行状态下不允许进入
		if player.effect_state & csdefine.EFFECT_STATE_PROWL:
			player.client.onStatusMessage( csstatus.RABBITRUN_FORBID_NOT_FREE_STATE, "")
			return

		if player.getState() != csdefine.ENTITY_STATE_FREE:
			player.client.onStatusMessage( csstatus.RABBITRUN_FORBID_NOT_FREE_STATE, "" )
			return
		
		if player.intonating():
			player.client.onStatusMessage( csstatus.RABBITRUN_FORBID_INTONATING, "" )
			return
		
		count = player.countItemTotal_( csconst.RABBIT_RUN_ITEM_RADISH )
		if count > 0:
			player.client.onStatusMessage( csstatus.RABBITRUN_FORBID_RADISH, "" )
			return

		count = player.getNormalKitbagFreeOrderCount()
		if count < 3:
			player.client.onStatusMessage( csstatus.RABBITRUN_NEED_KITBAG_3_FREE, "" )
			return

		if player.pcg_hasActPet():
			player.client.onStatusMessage( csstatus.RABBITRUN_NEED_NO_PET, "" )
			return
		
		player.addActivityCount( csdefine.ACTIVITY_RUN_RABBIT )
		player.gotoSpace('fu_ben_rabbit_run', random.choice( Start_Positions ), (0.000000, 0.000000, -1.5) )

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
