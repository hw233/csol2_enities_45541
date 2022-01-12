# -*- coding: gb18030 -*-


"""
"""
from Function import Function
import csdefine
import BigWorld
import time
import csstatus
from interface.GameObject import GameObject

class FuncTriggerAIEventByDialog( Function ):
	"""
	对话改变AI等级(该对话选项隐藏)
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		Function.__init__( self, section )
		pass
		
	def do( self, player, talkEntity = None ):
		"""
		@param player: 玩家
		@type  player: Entity
		@param  talkEntity: 一个扩展的参数
		@type   talkEntity: entity
		@return: None
		"""
		pass
		
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
		talkEntity.remoteCall( "doAllEventAI", ( csdefine.AI_EVENT_TALK, ) )		#这里采用remoteCall方法主要是为了避免talkEntity为ghost的情况
		return False
