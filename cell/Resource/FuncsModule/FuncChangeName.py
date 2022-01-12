# -*- coding: gb18030 -*-

from bwdebug import *
import cschannel_msgs
import ShareTexts as ST
from Function import Function
import csdefine

class FuncChangeFamilyName( Function ):
	"""
	家族改名
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.client.askChangeFamilyName( talkEntity.id )
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
		return player.familyName.endswith( cschannel_msgs.ACCOUNT_NOTICE_7 ) and player.isFamilyShaikh()
		
		
class FuncChangeTongName( Function ):
	"""
	帮会改名
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能
		
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		player.client.askChangeTongName( talkEntity.id )
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
		return player.tongName.endswith( cschannel_msgs.ACCOUNT_NOTICE_7 ) and player.isTongChief()
		
		