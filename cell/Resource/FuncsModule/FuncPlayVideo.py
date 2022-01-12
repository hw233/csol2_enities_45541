# -*- coding: gb18030 -*-

from bwdebug import *
from Function import Function
import csconst
import csstatus

class FuncPlayVideo( Function ):
	"""
	播放视频
	"""
	def __init__( self, section ):
		"""
		"""
		Function.__init__( self, section )
		self._param1 = section.readString( "param1" )			#视频文件名字
		
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
		#DEBUG_MSG( "-->>rlt_askForStartAlly" )
		player.endGossip( talkEntity )
		player.client.playVideo( self._param1 )
		
		