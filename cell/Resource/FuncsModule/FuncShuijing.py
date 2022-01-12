# -*- coding: gb18030 -*-
#


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import math
import random
import Math
import csstatus
import utils
from bwdebug import *

from ObjectScripts.GameObjectFactory import g_objFactory

ENTERN_SHUIJING_MENBER_DISTANCE = 30.0
#SHUIJING_POSITION = ( 15.221, 19.823, -21.644 )
SHUIJING_POSITION = ( -37.092, 0.116, 40.691 )


class FuncShuijing( Function ):
	"""
	进入水晶副本
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.level = section.readInt( "param1" )										#进入等级
		self.recordKey = "shuijing_record"
		self.spaceName = "shuijing"


	def do( self, player, talkEntity = None ):
		"""
		进入水晶副本。
		规则：
			创建条件：（把队员都拉进来）
				这个队伍当前没有副本。
				要求进入者是队长。
				达到等级要求。
				队伍人数大于3人。
				队伍成员没有进入过副本的。
			进入条件：（只有自己一个人进去）
				有组队。
				有队伍副本存在。

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
					
		#玩家等级不够
		if self.level > player.level:
			player.statusMessage( csstatus.SHUIJING_LEVEL_NOT_ARRIVE, self.level )
			return
		
		if not BigWorld.globalData.has_key('AS_shuijingStart') or not BigWorld.globalData["AS_shuijingStart"]:
			#水晶活动没有开启
			player.statusMessage( csstatus.SHUIJING_IS_NOT_OPEN )
			return
		
		#玩家没有组队
		if not player.isInTeam():
			player.statusMessage( csstatus.SHUIJING_NEED_TEAM )
			return

		if BigWorld.globalData.has_key( 'Shuijing_%i'%player.getTeamMailbox().id ):
			if player.isActivityCanNotJoin( csdefine.ACTIVITY_SHUI_JING )  and player.query( "lastShuijintTeamID", 0 ) != player.getTeamMailbox().id:
				player.statusMessage( csstatus.SHUIJING_FORBID_TWICE )
				return
			shuijingKey = BigWorld.globalData[ "Shuijing_%i"%player.getTeamMailbox().id ]
			BigWorld.globalData[ "ShuijingManager" ].reEnter( shuijingKey, player.base )
#			player.gotoSpace(self.spaceName, SHUIJING_POSITION, (0,0,0))
		else:
			#队伍没有副本，则走创建流程
			if not player.isTeamCaptain():
				player.statusMessage( csstatus.ROLE_IS_NOT_CAPTAIN )
				return
			
			entities = []
			dbidList = []
			pList = player.getAllMemberInRange( ENTERN_SHUIJING_MENBER_DISTANCE )
#			if not len( pList ) >= 3 :
			if len( pList ) != 3 :
				player.statusMessage( csstatus.SHUIJING_ROLE_IS_ENOUGH_MEMBER )
				return
			for i in pList:
				if i.level < self.level:
					player.statusMessage( csstatus.ROLE_MEMBER_HAS_NOT_SHUIJING_LEVEL )
					return
				if i.isActivityCanNotJoin( csdefine.ACTIVITY_SHUI_JING ) :
					player.statusMessage( csstatus.SHUIJING_HAS_ENTERED_TODAY )
					return
				entities.append( i.base )
				dbidList.append( i.databaseID )
			pList.remove( player )
			player.set( "lastShuijintTeamID", player.getTeamMailbox().id )
			player.set( "shuijing_checkPoint", 1 )
#			player.gotoSpace(self.spaceName, SHUIJING_POSITION, (0,0,0))
			for i in pList:
				i.set( "lastShuijintTeamID", player.getTeamMailbox().id )
				i.set( "shuijing_checkPoint", 1 )
#				i.gotoSpace(self.spaceName, SHUIJING_POSITION, (0,0,0))
			
			BigWorld.globalData[ "ShuijingManager" ].onRequestShuijing( entities, dbidList, player.getLevel(), player.getTeamMailbox() )

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

class FuncShuijingCallEntity( Function ):
	"""
	水晶副本对话召唤出多个怪物同时开始第一关刷怪
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.classNameList = section.readString( "param1" ).split( ";" )						# className列表
		self.mountList = section.readString( "param2" ).split( ";" )							# 每个className对应的怪物数量
		self.positionAndDirectionLists = section.readString( "param3" ).split( ";" )

	def do( self, player, talkEntity = None ):
		"""
		水晶副本对话召唤出多个怪物同时开始第一关刷怪

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.endGossip( talkEntity )
		try:
			spaceEntity = BigWorld.entities[ player.getCurrentSpaceBase().id ]
		except KeyError, errStr :
			EXCEHOOK_MSG( errStr )
			return
		spaceEntity.startSpawnMonsterByTalk( player.id, self.classNameList, self.mountList, self.positionAndDirectionLists )

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
		try:
			spaceEntity = BigWorld.entities[ player.getCurrentSpaceBase().id ]
		except KeyError, errStr :
			EXCEHOOK_MSG( errStr )
			return
		if spaceEntity.queryTemp( "shuijing_callEntity", 0 ):
			return True
		else:
			return False

class FuncLeaveShuijing( Function ):
	"""
	离开水晶副本
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
		if player.isInTeam():
			if player.shuijingKey:
				BigWorld.globalData[ "ShuijingManager" ].playerLeave( player.shuijingKey, player.base )
			player.endGossip( talkEntity )
			return
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

