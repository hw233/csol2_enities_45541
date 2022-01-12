# -*- coding:gb18030 -*-

from Function import Function
import csstatus
import csdefine
from bwdebug import *
import Const
import BigWorld
import SkillTargetObjImpl

class FuncUnfoldScroll( Function ):
	"""
	10级副本中展开墙上的画卷并向玩家施法
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		# param1 UINT32用来指定是哪一幅画
		# param2 STRING用来指定展开画卷时施法用的技能
		
		self.scrollID = section[ "param1" ].asInt
		self.spellID = section[ "param2" ].asInt
		
		assert self.spellID != 0
		

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
		
		# 向玩家施法，以便在随后的情节中检测特定任务是否完成
		playerEntity.spellTarget( self.spellID, playerEntity.id )
		
		playerEntity.client.unfoldScroll( talkEntity.id, self.scrollID )