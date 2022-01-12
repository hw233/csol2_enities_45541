# -*- coding: gb18030 -*-

"""
"""
from Function import Function
import csdefine
import csstatus
import Language
import time
import BigWorld
from CrondScheme import *


class FuncInScheme( Function ):
	"""
	"""
	def __init__( self, section ):
		"""
		"""
		if section:
			self._onSchemeTalkInfo   = section.readString( "param1" ).split("|")			#处于指定时间段中出现的对话 ( key | 标题 | 类型 ）
			self._outSchemeTalkInfo  = section.readString( "param2" ).split("|")			#不处于指定时间段中出现的对话 ( key | 标题 | 类型 ）
			self._cmd			 = section.readString( "param3" )							#计划字符串 如：" * * 3 * *" (参见 CrondScheme.py)
			self._presistMinute	 = section.readInt( "param4" )								#持续时间
			
			self.scheme = Scheme()
			self.scheme.init( self._cmd )
		
		
	def do( self, player, talkEntity = None ):
		"""
		执行一个功能

		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		pass
		#player.endGossip( talkEntity )


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
		year, month, day, hour, minute = time.localtime( time.time() - self._presistMinute * 60 )[:5]
		nextTime = self.scheme.calculateNext( year, month, day, hour, minute )
		if nextTime < time.time():
			player.addGossipOption( self._onSchemeTalkInfo[0], self._onSchemeTalkInfo[1], int( self._onSchemeTalkInfo[2] ) )
		else:
			player.addGossipOption( self._outSchemeTalkInfo[0], self._outSchemeTalkInfo[1], int( self._outSchemeTalkInfo[2] ) )
		return True


