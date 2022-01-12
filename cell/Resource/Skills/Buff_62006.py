# -*- coding: gb18030 -*-
#
# 物理暴击和法术暴击增加x%(x为参数由策划配置)	2009-07-17 SPF
#


import BigWorld
import csconst
import csstatus
import Const
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_62006( Buff_Normal ):
	"""
	物理暴击和法术暴击增加x%(x为参数由策划配置)
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100	
		
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
		receiver.double_hit_probability_value += self._p1
		receiver.calcDoubleHitProbability()
		receiver.magic_double_hit_probability_value += self._p1
		receiver.calcMagicDoubleHitProbability()
	
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
		receiver.double_hit_probability_value += self._p1
		receiver.magic_double_hit_probability_value += self._p1
	
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
		receiver.double_hit_probability_value -= self._p1
		receiver.calcDoubleHitProbability()
		receiver.magic_double_hit_probability_value -= self._p1
		receiver.calcMagicDoubleHitProbability()
		