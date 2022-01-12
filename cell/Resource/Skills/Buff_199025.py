# -*- coding: gb18030 -*-

import BigWorld
from Buff_Normal import Buff_Normal

class Buff_199025( Buff_Normal ):
	"""
	禁止添加不消耗魔法标志的效果buff，即xx秒内不允许再次触发不消耗魔法效果
	"""
	def __init__( self ):
		"""
		构造函数
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )

	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果开始的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		# 添加禁止不需要消耗魔法标志
		receiver.setTemp( "FORBID_NOT_NEED_MANA", True )

	def doReload( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果重新加载的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doReload( self, receiver, buffData )
		# 添加禁止不需要消耗魔法标志
		receiver.setTemp( "FORBID_NOT_NEED_MANA", True )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: None
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		# 去掉禁止不需要消耗魔法标志
		receiver.removeTemp( "FORBID_NOT_NEED_MANA" )
