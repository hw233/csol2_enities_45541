# -*- coding:gb18030 -*-

from Function import Function
from bwdebug import *
import csdefine
import csstatus
import csconst
import BigWorld

class FuncConstCityWar( Function ):
	"""
	申请争夺城市竞拍
	"""
	def __init__( self, section ):
		self.tonglevel = section.readInt( "param1" )	#帮会需要级别
		self.tongAction = section.readInt( "param2" )	#帮会需要行动力
		self.repMoney = section.readInt( "param3" )  	#需要金钱
		
	def do( self, player, talkEntity = None ):
		# 执行一个功能
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
			
		if not player.isJoinTong():
			player.statusMessage( csstatus.TONG_CITY_WAR_NOT_TONG )
			player.endGossip( talkEntity )
			return
			
		if not player.isTongChief() and not player.isTongDeputyChief():
			player.statusMessage( csstatus.TONG_CITY_WAR_GRADE_INVALID )
		else:
			cityName = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
			BigWorld.globalData[ "TongManager" ].cityWarQueryIsCanSignUp( player.base, player.tong_dbID, self.tonglevel, self.repMoney, cityName )
		
		player.endGossip( talkEntity )
			
	def valid( self, player, talkEntity = None ):
		# 检查一个功能是否可以使用
		return True
		

class FuncTongCityWarEnter( Function ):
	# 进入城市战场
	def do( self, player, talkEntity = None ):
		# 进入战场
		if player.level < 50:
			player.statusMessage( csstatus.TONG_CITY_WAR_NEED_LEVEL )
			player.endGossip( talkEntity )
			return
		
		if not player.isJoinTong():
			player.statusMessage( csstatus.TONG_CITY_WAR_NOT_TONG )
			player.endGossip( talkEntity )
			return
			
		spaceKey = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		player.set( "cityWarEnterInfos", ( spaceKey, player.position, player.direction ) )
		BigWorld.globalData[ "TongManager" ].onRoleSelectEnterWar( player.tong_dbID, player.base )
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		return BigWorld.globalData.has_key( "CityWarOverTime" )


class FuncTongCityWarLeave( Function ):
	# 帮会城市战 离开战场
	def __init__( self, section ):
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		player.tong_leaveCityWar()
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		return True

class FuncAbandonTongCity( Function ):
	"""
	放弃帮会占领的城市
	"""
	def __init__( self, section ):
		Function.__init__( self, section )
	
	def do( self, player, talkEntity = None ):
		if not player.isTongChief():
			player.statusMessage( csstatus.TONG_ABANDON_HOLD_CITY_NO_GRADE )
			player.endGossip( talkEntity )
			return
			
		city = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if not BigWorld.globalData.has_key( "holdCity.%s" % city ):
			player.statusMessage( csstatus.TONG_ABANDON_HOLD_CITY_NO_CITY )
			player.endGossip( talkEntity )			
			return
			
		tongDBID = BigWorld.globalData[ "holdCity.%s" % city ][0]
		if player.tong_dbID != tongDBID:
			player.statusMessage( csstatus.TONG_ABANDON_HOLD_CITY_NO_CITY )
			player.endGossip( talkEntity )	
			return
		cityNameCN = csconst.TONG_CITYWAR_CITY_MAPS.get( city, "" )
		if cityNameCN != "":
			player.client.tong_onAbandonTongCityNotify( city )
		player.endGossip( talkEntity )
	
	def valid( self, player, talkEntity = None ):
		return True