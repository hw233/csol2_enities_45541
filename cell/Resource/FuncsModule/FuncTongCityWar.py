# -*- coding:gb18030 -*-

from Function import Function
from bwdebug import *
import csdefine
import csstatus
import csconst
import BigWorld

class FuncConstCityWar( Function ):
	"""
	����������о���
	"""
	def __init__( self, section ):
		self.tonglevel = section.readInt( "param1" )	#�����Ҫ����
		self.tongAction = section.readInt( "param2" )	#�����Ҫ�ж���
		self.repMoney = section.readInt( "param3" )  	#��Ҫ��Ǯ
		
	def do( self, player, talkEntity = None ):
		# ִ��һ������
		player.endGossip( talkEntity )
		if player.iskitbagsLocked():	# ����������by����
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
		# ���һ�������Ƿ����ʹ��
		return True
		

class FuncTongCityWarEnter( Function ):
	# �������ս��
	def do( self, player, talkEntity = None ):
		# ����ս��
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
	# ������ս �뿪ս��
	def __init__( self, section ):
		Function.__init__( self, section )

	def do( self, player, talkEntity = None ):
		player.tong_leaveCityWar()
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		return True

class FuncAbandonTongCity( Function ):
	"""
	�������ռ��ĳ���
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