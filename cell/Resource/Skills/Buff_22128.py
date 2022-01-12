# -*- coding: gb18030 -*-
import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22128( Buff_Normal ):
	"""
	此BUFF在给定时间到了之后完成一个“QTTaskEventTrigger”，用例：10级副本中看图的任务 by mushuang
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.questID = 0
		self.taskIndex = 0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		# Param1 任务ID
		# Param2 任务目标索引
		Buff_Normal.init( self, dict )
		self.questID = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
		self.taskIndex = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )

	def doLoop( self, receiver, buffData ):
		"""
		irtual method; call only by real entity.
		用于buff，表示buff在每一次心跳时应该做什么。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL；如果允许继续则返回True，否则返回False
		@rtype:  BOOL
		"""
		# 触发玩家身上的相应完成状态
		receiver.questTaskIncreaseState( self.questID, self.taskIndex )
		return True
