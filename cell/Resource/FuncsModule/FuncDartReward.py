# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
from Function import Function
import time
import csdefine
import Language
import items
import csstatus
import sys

g_items = items.instance()

class FuncDartReward( Function ):
	"""
	根据声望领取运镖一周奖励
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		self.param1 = section['param1'].asInt					#势力值
		self.rewardSection = Language.openConfigSection("config/server/DartRewards.xml")

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
		if player.iskitbagsLocked():	# 背包上锁，by姜毅
			player.client.onStatusMessage( csstatus.CIB_MSG_KITBAG_LOCKED_MISSION, "" )
			return
		currentWeak = ( int(time.time()) / (3600 * 24) + 3 ) / 7

		if player.dartRewardRecord != currentWeak:
			player.dartRewardRecord = currentWeak
			prestige = player.getPrestige( self.param1 )
			for index in xrange( len( self.rewardSection ) ):
				childSection = self.rewardSection.child( index )
				minPresitige = childSection.readInt( "minPresitige" )
				maxPresitige = childSection.readInt( "maxPresitige" )
				if prestige >= minPresitige and maxPresitige >= prestige:
					itemsStr = childSection.readString( 'items' )
					if  itemsStr != "":
						for i in itemsStr.split('|'):
							itemData = i.split(":")
							for i in range(0, int(itemData[1])):
								item = g_items.createDynamicItem( int(itemData[0]), 1 )
								player.addItem( item, csdefine.ADD_ITEM_DARTREWARD )

					player.addExp( childSection.readInt( 'exp' ), csdefine.CHANGE_EXP_DARTREWARD )
					player.gainMoney( childSection.readInt( 'money' ), csdefine.CHANGE_MONEY_DARTREWARD )
					return

			player.statusMessage( csstatus.ROLE_QUEST_DART_REWARD_NOT_ENOUGH_PRESITIGE )
		else:
			player.statusMessage( csstatus.ROLE_QUEST_DART_REWARD_HAS_GET )

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
		return player.getPrestige( self.param1 ) > 0


#
# $Log: not supported by cvs2svn $
