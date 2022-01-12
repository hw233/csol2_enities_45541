# -*- coding: gb18030 -*-

"""
引力、斥力
"""

import BigWorld
import Math
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_208001( Buff_Normal ):
	"""
	example:
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._speed = 0.0

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._speed = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
		

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
		self.setDirection( receiver, buffData )
		receiver.topSpeed += self._speed


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
		self.setDirection( receiver, buffData )

	def doLoop( self, receiver, buffData ):
		self.setDirection( receiver, buffData )
		return Buff_Normal.doLoop( self, receiver, buffData )
	
	def setDirection( self, receiver, buffData ):
		id = buffData["caster"]
		if BigWorld.entities.has_key( id ):
			caster = BigWorld.entities[ id ]
			direction = caster.position - receiver.position
			receiver.moveDirection = [ direction[0], direction[2], self._speed ]
	
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
		if BigWorld.entities.has_key( id ):
			self.moveDirection = []
		receiver.updateTopSpeed()