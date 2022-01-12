# -*- coding:gb18030 -*-
# 10 级副本“前世记忆” by mushuang


from Function import Function
import csstatus
import csdefine
from bwdebug import *
import Const
import BigWorld

REQUIRED_LEVEL = 10
SPACE_COPY_NAME = "fu_ben_qian_shi"
ENTER_POINT = ( 15.625, -5.093, 0.583 )	#modify by wuxo 2011-12-2
ENTER_DIRECTION = ( 11.76, 59.584, -1.014 ) #modify by wuxo 2011-12-13

class FuncBeforeNirvana( Function ):
	"""
	装备属性飞升
	"""
	def __init__( self, section ):
		"""
		@param param: 由实现类自己解释格式; param1 - param5
		@type  param: pyDataSection
		"""
		# param1: 为进入副本时需要展开的画卷ID
		self.scrollID = section[ "param1" ].asInt

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
		if talkEntity is None:
			ERROR_MSG( "player( %s ) talk entity is None." % player.getName() )
			return
		playerEntity.endGossip( talkEntity )
		
		# 检查相关进入条件
		
		# 等级
		if playerEntity.getLevel() < REQUIRED_LEVEL :
			playerEntity.statusMessage( csstatus.BEFORE_NIRVANA_LEVEL_TOO_LOW )
			return
		
		playerEntity.setTemp( "ScrollIDOnEnter", self.scrollID )
		
		# 所有条件通过，准许进入
		playerEntity.gotoSpace( SPACE_COPY_NAME, ENTER_POINT, ENTER_DIRECTION )
		