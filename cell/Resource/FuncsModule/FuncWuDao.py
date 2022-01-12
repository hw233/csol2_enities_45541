# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
"""
import time
import random

from Function import Function
import csdefine
import BigWorld
import csstatus
import utils
from bwdebug import *

class FuncSingUpWuDao( Function ):
	"""
	武道大会报名
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
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
		if player.level < self._param1:
			player.statusMessage( csstatus.ROLE_HAS_NOT_WUDAO_LEVEL, self._param1 )
		else:
			player.wuDaoSignUp( player.id )
			
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

class FuncWuDaoGetReward( Function ):
	"""
	武道大会领奖励
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.itemID = section.readInt( "param1" )	# 奖励的物品ID
		self.requireTitleID = section.readInt( "param2" )	# 称号ID

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		if not player.query( "wuDaoChampion" ) or player.query( "wuDaoChampion" )[ 0 ] < time.time():
			player.statusMessage( csstatus.WU_DAO_REWARD_UN_CHAMPION )
			player.endGossip( talkEntity )
			return
		
		if player.query( "wuDaoChampion" )[ 1 ]:
			player.statusMessage( csstatus.WU_DAO_REWARD_ALREADY )
			player.endGossip( talkEntity )
			return
			
		if self.itemID != 0:
			item = player.createDynamicItem( self.itemID )
			kitbagState = player.checkItemsPlaceIntoNK_( [item] )
			if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
				# 背包空间不够
				player.statusMessage( csstatus.CIB_MSG_CANT_OPERATER_FULL )
				player.endGossip( talkEntity.id )
				return
				
			player.addItemAndNotify_( item, csdefine.REWARD_TONG_WUDAO )
			player.addTitle( self.requireTitleID )
			player.selectTitle( player.id, self.requireTitleID )
		
		wuDaoChampion = ( player.query( "wuDaoChampion" )[ 0 ], True )
		player.set( "wuDaoChampion", wuDaoChampion )
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


class FuncWuDaoEnterSpace( Function ):
	"""
	武道大会进入
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self.pos = None
		position = section.readString( "param1" )
		pos = utils.vector3TypeConvert( position )
		if pos is None:
			ERROR_MSG( "Vector3 Type Error：%s Bad format '%s' in section param1 " % ( self.__class__.__name__, position ) )
		else:
			self.pos = pos

	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		BigWorld.globalData['WuDaoMgr'].selectEnterWuDao( player.databaseID )
		player.gotoSpace( "wu_dao", self.pos + ( random.randint(-2,2), 0, random.randint(-2,2) ), (0,0,0) )
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
