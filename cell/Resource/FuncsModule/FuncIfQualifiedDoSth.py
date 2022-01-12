# -*- coding: gb18030 -*-


import csstatus
import cschannel_msgs
import BigWorld
import csdefine
import items
from Function import Function
from bwdebug import *
g_items = items.instance()



class FuncSpellTargetIfQualified( Function ):
	"""
	如果没有相应的物品，那么对玩家释放一个技能
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )		# 需要检测的物品 itemId1|itemId2|itemId3 。。。
		self._skillID = section.readInt( "param2" )		# 产生的技能ID(因为奖励的是一个buff)
		self._describe = section.readString( "param3" )	# 存在物品时的描述
		if len( self._p1 ):
			self._requireItems = self._p1.split( "|" )		# 需要检测的物品ID数组 type:str
		else:
			self._requireItems = []


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
		for itemID in self._requireItems:
			item = player.findItemFromNKCK_( int( itemID ) )
			if item:
				talkEntity.say( self._describe )
				return

		talkEntity.spellTarget( self._skillID, player.id )

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



class FuncGiveItemIfQualified( Function ):
	"""
	如果没有相应的物品，那么给予玩家相应的物品
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		self._p1 = section.readString( "param1" )					# 需要检测的物品 itemId1|itemId2|itemId3 。。。
		self._p2 = section.readString( "param2" )					# 奖励的物品 itemId1|itemId2|itemId3 。。。
		self._describe = section.readString( "param3" )				# 存在物品时的描述
		if len( self._p1 ):
			self._requireItems = self._p1.split( "|" )					# 需要检测的物品ID数组 type:str
		else:
			self._requireItems = []
		if len( self._p2 ):
			self._rewardItems = self._p2.split( "|" )					# 奖励的物品ID数组 type:str
		else:
			self._rewardItems = []
		

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
		for itemID in self._requireItems:
			item = player.findItemFromNKCK_( int( itemID ) )
			if item:
				talkEntity.say( self._describe )
				return

		self.rewardPlayer( player )


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

	def rewardPlayer( self, player ):
		"""
		奖励玩家
		"""
		items = []
		for itemID in self._rewardItems:
			item = g_items.createDynamicItem( int( itemID ) )
			items.append( item )
			if item is None:
				ERROR_MSG( "item %s not exist." % itemID )
				return
				
		kitbagState = player.checkItemsPlaceIntoNK_( items )
		if  kitbagState == csdefine.KITBAG_NO_MORE_SPACE:
			# 背包空间不够装
			player.statusMessage( csstatus.CIB_MSG_ITEMBAG_SPACE_NOT_ENOUGH )
		else:
			for item in items:
				player.addItem( item, csdefine.ADD_ITEM_BY_TALK )

