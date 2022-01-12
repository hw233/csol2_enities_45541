# -*- coding: gb18030 -*-
#
# $Id: FuncQueryFamilyNPC.py,v 1.2 2008-07-19 03:53:07 kebiao Exp $

"""
"""
from Function import Function
import BigWorld
import csconst
import csdefine
import csstatus
import time

from TitleMgr import TitleMgr
g_titleLoader = TitleMgr.instance()


class FuncGetCityTongChampion( Function ):
	# 领取城战冠军奖励
	def __init__( self, section ):
		Function.__init__( self, section )
		self.championBoxID = section.readInt( "param1" )
		self.titleName = section.readString( "param2" )
	
	def do( self, player, talkEntity = None ):
		if not player.query( "tongCityWarChampion" ) or player.query( "tongCityWarChampion" )[ 0 ] < time.time():
			player.statusMessage( csstatus.TONG_CITY_WAR_REWARD_UN_CHAMPION )
			player.endGossip( talkEntity )
			return
		
		if player.query( "tongCityWarChampion" )[ 1 ]:
			player.statusMessage( csstatus.TONG_CITY_WAR_REWARD_ALREADY )
			player.endGossip( talkEntity )
			return
			
		
		# 给物品
		if self.championBoxID != 0:
			item = player.createDynamicItem( self.championBoxID )
			kitbagState = player.checkItemsPlaceIntoNK_( [item] )
			if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
				# 背包空间不够
				player.statusMessage( csstatus.CIB_MSG_CANT_OPERATER_FULL )
				player.endGossip( talkEntity.id )
				return
				
			player.addItemAndNotify_( item, csdefine.REWARD_TONG_TONG_CITY_WAR )
		
		# 给称号
		title_dict = {}
		for i in g_titleLoader._datas:
			title_dict[ g_titleLoader._datas[ i ][ "name" ] ] = i

		if self.titleName not in title_dict or self.titleName == "":
			srcEntity.client.onStatusMessage( csstatus.WIZCOMMAND_TITLE_IS_WRONG, "" )
			return
			
		player.addTitle( title_dict[ self.titleName ] )
			
		tongCityWarChampion = ( player.query( "tongCityWarChampion" )[ 0 ], True )
		player.set( "tongCityWarChampion", tongCityWarChampion )
		player.endGossip( talkEntity )
	
	def valid( self, player, talkEntity = None ):
		return True

class FuncGetCityTongChief( Function ):
	# 领取城战帮主奖励
	def __init__( self, section ):
		Function.__init__( self, section )
	
	def do( self, player, talkEntity = None ):
		if not player.isTongChief():
			self.statusMessage( csstatus.TONG_CITY_WAR_CHIEF_REWARD_GRADE )
			player.endGossip( talkEntity )
			return
		
		player.getTongManager().getCityTongChiefReward( player.tong_dbID, player.base )
		player.endGossip( talkEntity )
	
	def valid( self, player, talkEntity = None ):
		return True

class FuncGetCityTongMoney( Function ):
	# 领取帮会资金
	def __init__( self, section ):
		self._money = section.readInt( "param1" )

	def do( self, player, talkEntity = None ):
		if not player.isTongChief():
			player.statusMessage( csstatus.TONG_CITY_WAR_GET_MONEY_NO_TONG )
			player.endGossip( talkEntity )
			return
			
		city = player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if not BigWorld.globalData.has_key( "holdCity.%s" % city ):
			player.statusMessage( csstatus.TONG_CITY_WAR_GET_MONEY_NO_GRADE )
			player.endGossip( talkEntity )			
			return
			
		tongDBID = BigWorld.globalData[ "holdCity.%s" % city ][0]
		if player.tong_dbID != tongDBID:
			player.statusMessage( csstatus.TONG_CITY_WAR_GET_MONEY_NO_GRADE )
			player.endGossip( talkEntity )	
			return
		player.tong_getSelfTongEntity().requestCityTongRevenue( city, player.databaseID )
		player.endGossip( talkEntity )
		

	def valid( self, player, talkEntity = None ):
		return True


class FuncGetCityTongItem( Function ):
	"""
	领取帮会占领城市利益 经验果实
	"""
	def do( self, player, talkEntity = None ):
		player.getTongManager().getCityTongItem( player.databaseID, player.tong_dbID, player.base, player.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY ) )
		player.endGossip( talkEntity )

	def valid( self, player, talkEntity = None ):
		return True
