# -*- coding: gb18030 -*-

from SpellBase import *
from Buff_Normal import Buff_Normal
from bwdebug import *
import Const

class Buff_22138( Buff_Normal ):
	"""
	进入位面，通过buff来控制玩家进入位面时topSpeed的变化时间
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )

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
		receiver.setTopSpeed( Const.TELEPORT_PLANE_TOPSPEED_LIMIT )

	def doEnd( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		效果结束的处理。

		@param receiver: 效果要影响的实体
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		"""
		receiver.updateTopSpeed()
		Buff_Normal.doEnd( self, receiver, buffData )
		