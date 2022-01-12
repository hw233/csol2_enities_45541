# -*- coding:gb18030 -*-

import csstatus
import csconst
import BigWorld
import utils
from bwdebug import *
from Function import Function

class FuncTongCityWarFinalEnter( Function ):
	"""
	进入帮会夺城战决赛战场
	"""
	def __init__( self, section ):
		self.spaceKey = section.readString( "param1" )

	def do( self, player, talkEntity = None ):
		"""
		进入战场
		"""
		player.endGossip( talkEntity )
		
		if not player.isJoinTong():
			player.statusMessage( csstatus.TONG_CITY_WAR_FINAL_NOT_TONG )
			player.endGossip( talkEntity )
			return
		# 记录进入战场前的位置信息
		spaceKey = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		player.set( "cityWarFianlEnterInfos", ( spaceKey, player.position, player.direction ) )
		
		BigWorld.globalData[ "TongManager" ].requestEnterCityWarFinal( player.tong_dbID, player.base, player.getCamp(), player.spaceType, self.spaceKey )

	def valid( self, player, talkEntity = None ):
		"""
		检查一个功能是否可以使用
		"""
		return BigWorld.globalData.has_key( "TONG_CITY_WAR_FINAL_END_TIME" )

class FuncCityWarFinalBaseTeleport( Function ):
	"""
	夺城战决赛中据点间的传送
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self.className = section.readString( "param1" )

		self.position = None
		self.direction = None
		
		position = section.readString( "param2" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param1 " % ( self.__class__.__name__, position ) )
		else:
			self.position = pos
		
		direction = section.readString( "param3" )
		dir = utils.vector3TypeConvert( direction )
		if dir is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param2 " % ( self.__class__.__name__, direction ) )
		else:
			self.direction = dir

	def do( self, player, talkEntity = None ):
		"""
		"""
		player.endGossip( talkEntity )
		player.teleportToSpace( self.position, self.direction, talkEntity, talkEntity.spaceID )

	def valid( self, player, talkEntity = None ):
		"""
		"""
		if talkEntity.belong and player.queryTemp( "CITY_WAR_FINAL_BELONG", 0 ) != talkEntity.belong:
			return False
		if self.className not in talkEntity.sameBelongs:
			return False
		return True