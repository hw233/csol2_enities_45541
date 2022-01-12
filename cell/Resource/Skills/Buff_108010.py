# -*- coding: gb18030 -*-

import BigWorld
import csdefine
from Buff_Normal import Buff_Normal


class Buff_108010( Buff_Normal ):
	"""
	example:僵直
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self.targetMoveSpeed = 6.0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		if dict["Param1"]:
			self.targetMoveSpeed = float( dict["Param1"] )  # 位移速度

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
		# 执行附加效果
		receiver.move_speed = self.targetMoveSpeed
		receiver.updateTopSpeed()


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
		# 执行附加效果
		receiver.move_speed = self.targetMoveSpeed
		receiver.updateTopSpeed()

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.calcMoveSpeed()
		receiver.updateTopSpeed()

