# -*- coding: gb18030 -*-

from bwdebug import *
from Function import Function

import csdefine

class FuncStartPickAnima( Function ):
	"""
	开始拾取灵光玩法
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		对话选项有效性检查
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		触发对话选项要做的事情
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		player.changeState( csdefine.ENTITY_STATE_PICK_ANIMA )
		player.endGossip( talkEntity )


class FuncStopPickAnima( Function ):
	"""
	结束拾取灵光玩法
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		
	def valid( self, player, talkEntity = None ):
		"""
		Virtual method.
		对话选项有效性检查
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		return True
		
	def do( self, player, talkEntity = None ):
		"""
		Virtual method.
		触发对话选项要做的事情
		
		@param player: 玩家entity
		@param talkEntity: npc entity
		"""
		spaceCell = player.getCurrentSpaceCell()
		if spaceCell:
			spaceCell.onGameOver()

		player.changeState( csdefine.ENTITY_STATE_FREE )
		player.endGossip( talkEntity )