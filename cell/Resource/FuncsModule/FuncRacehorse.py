# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
import time
import BigWorld

import csstatus

import csdefine
from Function import Function
from VehicleHelper import getCurrVehicleID

import Const

MAX_RACE_MEMBERS = 	400			#最大400人参与赛马


class SignUpRacehorse( Function ):
	"""
	赛马报名
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

		if player.isActivityCanNotJoin( csdefine.ACTIVITY_SAI_MA ) :
			player.statusMessage( csstatus.ROLE_HAS_RACED_TODAY )
			return

		if not BigWorld.globalData.has_key( "AS_Racehorse" ):
			player.client.onStatusMessage( csstatus.RACEHORSE_NOT_BEGIN, "" )
			return

		if BigWorld.globalData["Racehorse_member_count"] > MAX_RACE_MEMBERS:
			player.client.onStatusMessage( csstatus.RACEHORSE_AMOUNTS_IS_FULL, "" )
			return

		if player.vehicle or getCurrVehicleID( player ):
			player.client.onStatusMessage( csstatus.RACEHORSE_FORBID_VEHICLE_STATE, "" )
			return

		if player.qieCuoState != csdefine.QIECUO_NONE:
			player.client.onStatusMessage( csstatus.RACEHORSE_FORBID_PK_STATE, "" )
			return


		if player.getState() != csdefine.ENTITY_STATE_FREE:
			player.client.onStatusMessage( csstatus.ROLE_RACE_STATE_FORBID, "" )
			return
		
		if player.intonating():
			player.client.onStatusMessage( csstatus.ROLE_RACE_INTONATING, "" )
			return
		

		player.setTemp( "raceType", 0 )		# 用以区分赛马场类型：普通、帮会赛马
		BigWorld.globalData['RacehorseManager'].enterRacehorseMap( player.base )


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

class CreateTongRacehorse( Function ):
	"""
	创建帮会赛马
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

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

		if not player.isTongChief():
			player.statusMessage( csstatus.ROLE_NOT_TONG_GRADE_CHIEF )
			return

		if player.level < 20:
			player.client.onStatusMessage( csstatus.TONG_RACEHORSE_FORBID_CHAIRMAN_LEVEL, "" )
			return
			
		items = player.findItemsByIDFromNKCK( Const.TONG_RACE_ITEM )
		if items == []:
			player.client.onStatusMessage( csstatus.TONG_RACEHORSE_ITEM_IS_NONE, "" )
			return
		#player.removeItem_( items[0].order, 1, csdefine.DELETE_ITEM_CREATETONGRACEHORSE  )

		tongMailbox = player.tong_getSelfTongEntity()
		if tongMailbox:
			tongMailbox.requestCreateTongRace( player.base )

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
		return player.isTongChief()



class EnterTongRacehorse( Function ):
	"""
	进入帮会赛马
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		pass

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
		if player.level < 20:
			player.client.onStatusMessage( csstatus.RACEHORSE_FORBID_LEVEL, "" )
			return
		if player.isActivityCanNotJoin( csdefine.ACTIVITY_SAI_MA ) :
			player.statusMessage( csstatus.ROLE_HAS_RACED_TODAY )
			return
		player.setTemp( "raceType", 1 )		# 用以区分赛马场类型：普通、帮会赛马
		BigWorld.globalData['RacehorseManager'].enterTongRacehorseMap( player.base, player.tong_dbID )



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


class FuncRacehorseRewardItem( Function ):
	"""
	领取赛马物品奖励
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		from Love3 import g_rewards
		self.g_rewards = g_rewards

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
		place = player.query( "raceHorse_place", 0 )
		if not player.isActivityCanNotJoin( csdefine.ACTIVITY_SAI_MA ) :	
			player.statusMessage( csstatus.ROLE_HAS_NOT_RACED_TODAY )
			return
		if place == 0:
			player.statusMessage( csstatus.ROLE_RACE_NOT_PLACE )
			return
		v_player = virtual_Role( player, place )
		if BigWorld.globalData["RacehorseType"] == "sai_ma_chang_01":
			awarder = self.g_rewards.fetch( csdefine.RCG_RACE_HORSE, v_player )
		elif BigWorld.globalData["RacehorseType"] == "sai_ma_chang_03":
			awarder = self.g_rewards.fetch( csdefine.RCG_RACE_HORSE_CHRIS, v_player )
			
		if  player.checkItemsPlaceIntoNK_( awarder.items ) == csdefine.KITBAG_NO_MORE_SPACE:
			player.statusMessage( csstatus.NPC_TRADE_SPACE_NOT_ENOUGH )
			return
		player.set( "raceHorse_place", 0 )
		awarder.award( v_player, csdefine.REWARD_RACE_HORSE_ITEMS )
		# g_rewardMgr.rewards( player, csdefine.REWARD_RACE_HORSE_ITEMS )

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

class virtual_Role:
	"""
	以特定序列封装的虚拟角色类
	"""
	def __init__( self, player, level ):
		self.level = level
		self.player = player
		self.client = player.client
		
	def addItemAndNotify_( self, itemInstance, reason ):
		"""
		virtual add Item
		"""
		return self.player.addItemAndNotify_( itemInstance, reason )
		
	def addMoney( self, money, reason ):
		"""
		virtual add money
		"""
		return self.player.addMoney( money, reason )
		
	def addExp( self, exp, reason ):
		"""
		virtual add exp
		"""
		return self.player.addExp( exp, reason )
		
	def tong_addContribute( self, contribute ):
		"""
		virtual add contribute
		"""
		self.player.tong_addContribute( contribute )