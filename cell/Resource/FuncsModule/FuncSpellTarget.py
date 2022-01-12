# -*- coding:gb18030 -*-

from Function import Function
import csstatus
import csdefine
import csconst
from bwdebug import *
import Const
import BigWorld


class FuncSpellTarget( Function ):
	"""
	对玩家施放技能
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		# param1： 技能ID，整数，比如9770022001
		Function.__init__( self, section )
		self.skillID = section["param1"].asInt
		self.teleportInfos = section.readString("param2")
		assert self.skillID != 0, "Invalid skill ID!"
		
	def valid( self, playerEntity, talkEntity = None ):
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

	def do( self, playerEntity, talkEntity = None ):
		"""
		执行一个功能

		@param playerEntity: 玩家
		@type  playerEntity: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		playerEntity.endGossip( talkEntity )
		
		if talkEntity is None:
			ERROR_MSG( "player( %s ) talk entity is None." % playerEntity.getName() )
			return
		playerEntity.setTemp( "requestTeleport", self.teleportInfos )
		playerEntity.spellTarget( self.skillID, playerEntity.id )

		