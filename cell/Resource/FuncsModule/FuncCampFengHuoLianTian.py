# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus
import csconst
from ActivityRecordMgr import g_activityRecordMgr
from ObjectScripts.GameObjectFactory import g_objFactory

CAN_JOIN_CAMP_FENG_HUO_LEVEL = 40

class FuncCampFengHuoLianTianSignUp( Function ):
	"""
	阵营烽火连天副本报名
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		"""
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		
			
		#玩家没有组队
		if player.getLevel() < CAN_JOIN_CAMP_FENG_HUO_LEVEL:
			player.statusMessage( csstatus.CAMP_FENG_HUO_LIAN_TIAN_LEVEL_NOT_ENOUGH )
			return
			
		BigWorld.globalData["CampMgr"].onRequestCampFengHuoSignUp( player.getCamp(), player.databaseID, player.base )
		
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
		return BigWorld.globalData.has_key( "campFengHuo_startSignUp" )

class FuncEnterCampFengHuoLianTian( Function ):
	"""
	进入阵营烽火连天副本
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		"""
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		
			
		#玩家没有组队
		if player.getLevel() < CAN_JOIN_CAMP_FENG_HUO_LEVEL:
			player.statusMessage( csstatus.CAMP_FENG_HUO_LIAN_TIAN_LEVEL_NOT_ENOUGH )
			return
			
		spaceKey = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		player.set( "CampFengHuoLianTianEnterInfos", ( spaceKey, player.position, player.direction ) )
		BigWorld.globalData["CampMgr"].onRoleRequestEnterCampFHLT( player.getCamp(), player.databaseID, player.base )
		
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
		return BigWorld.globalData.has_key( "campFengHuo_start" )
