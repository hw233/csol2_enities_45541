# -*- coding: gb18030 -*-
#
# $Id: FuncTeleport.py,v 1.16 2008-07-24 08:46:32 kebiao Exp $

"""
"""
from Function import Function
from bwdebug import *
import random
import math
import csstatus
import csdefine
import items
import time
import re
import sys
import csconst
import BigWorld

class FuncPotentialMeleeReward( Function ):
	"""
	潜能乱斗奖励
	"""
	def __init__( self, section ):
		"""
		param1: spaceName
		param2: x, y, z
		param3: d1, d2, d3
		param4: radius

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
		# phw 20091212: 这个代码，在极端的情况下，有些玩家是有可能无法领取奖励的
		# 原因是tempMapping属性是cell_private的，如果玩家与NPC不在同一个cellapp，则无法获取数据（会产生异常）
		rewardPlayers = talkEntity.queryTemp( "rewardPlayers" )
		rewardedPlayers = talkEntity.queryTemp( "rewardedPlayers" )
		if rewardedPlayers == None:
			rewardedPlayers = []
			talkEntity.setTemp( "rewardedPlayers", rewardedPlayers )
				
		DEBUG_MSG( "可以领取奖励的人:%s" % rewardPlayers )
		if not player.databaseID in rewardPlayers:
			if player.databaseID in rewardedPlayers:
				player.statusMessage( csstatus.POTENTIAL_MELEE_REWARD_NOT_FOUND )
			else:
				player.statusMessage( csstatus.POTENTIAL_MELEE_REWARD_NOT_FOUND1 )
			return

		item = items.instance().createDynamicItem( 60101004, 1 )
		item.set( "level", talkEntity.queryTemp( "playerLevel" ) )
		spaceLabel = BigWorld.getSpaceDataFirstForKey( player.spaceID, csconst.SPACE_SPACEDATA_KEY )
		
		if spaceLabel == "fu_ben_exp_melee":
			item.set( "aType", csdefine.ACTIVITY_JING_YAN_LUAN_DOU )
		else:
			item.set( "aType", csdefine.ACTIVITY_QIAN_NENG_LUAN_DOU )
			
		if player.checkItemsPlaceIntoNK_( [ item ] ) == csdefine.KITBAG_CAN_HOLD:
			player.addItemAndNotify_( item, csdefine.ADD_ITEM_POTENTIALMELEE )
			rewardPlayers.remove( player.databaseID )
			rewardedPlayers.append( player.databaseID )
			return
			
		player.statusMessage( csstatus.NPC_TRADE_KITBAG_IS_FULL )

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
#
# $Log: not supported by cvs2svn $
#
