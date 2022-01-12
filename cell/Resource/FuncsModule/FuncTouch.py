# -*- coding: gb18030 -*-

"""
"""
from Function import Function
import csdefine
import csstatus
import Language
import time
import BigWorld
from bwdebug import *

class FuncTouch( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
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
		if talkEntity.isReal():
			talkEntity.getScript().touch( talkEntity )
		else:
			talkEntity.remoteScriptCall( "touch", () )
		return False


class FuncOpenDoor( Function ):
	"""
	对话开启门
	"""
	def __init__( self, section ):
		"""
		"""
		# param1: 门，具体填什么内容需要根据param2决定。
		# param2: 门的类型(字符串)，可选值在self.doorType中
		# 门的类型决定了如何调用openDoor方法 -_-!
		
		# 这么纠结的代码绝对不是我本意，可是像openDoor这种方法居然不是接口的一部分，
		# 因此不同的副本有不同的调用方式，有的传入参数是dict,有的是字符串，有的是className
		# 相比增加"openDoorDict","openDoorStr","openDoorClassName"这些神奇的关键字，还是决
		# 定在这里增加一个门的类型。
		
		self.acceptDoorType = [ "monsterType", "dict" ] # 如果需要更多类型请自行添加
		
		self.doorType = section.readString( "param2" ) # 门的类型
		
		# 为了和以前的配置保持兼容，如果doorType不填，那么默认为monsterType
		if self.doorType == "": self.doorType = "monsterType"
		
		DEBUG_MSG( "doorType = %s"%self.doorType )
		
		assert self.doorType in self.acceptDoorType,"Invalid door type!"
		
		# 根据doorType初始化door
		if self.doorType == "monsterType":
			self.door = section.readInt( "param1" )
		elif self.doorType == "dict":
			self.door = section.readString( "param1" )
		#elif more doorType:
		#	some init work
		else:
			assert False,"Code path should never reach here!"
		
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
		
		spaceBase = player.getCurrentSpaceBase()
		if not spaceBase:
			ERROR_MSG( "Can't find space base!" )
			return
		
		# 根据门的类型选择不同的调用方式
		if self.doorType == "monsterType":
			player.getCurrentSpaceBase().openDoor( self.door )
		elif self.doorType == "dict":
			player.getCurrentSpaceBase().openDoor( { "entityName": self.door } )
		else:
			ERROR_MSG( "Code path should never reach here!" )

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
