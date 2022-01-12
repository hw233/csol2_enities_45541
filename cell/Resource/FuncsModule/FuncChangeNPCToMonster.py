# -*- coding: gb18030 -*-

"""
"""
from Function import Function
import csdefine
import csstatus
import Language
import time
import BigWorld


class FuncChangeNPCToMonster( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		#self.AIlevel = section.readInt( "param1" )										#AI 等级
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		talkEntity.changeToMonster( talkEntity.level, player.id )
		player.endGossip( talkEntity )
