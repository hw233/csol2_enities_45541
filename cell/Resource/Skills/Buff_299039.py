# -*- coding: gb18030 -*-

import BigWorld
from Buff_Normal import Buff_Normal

ELEM_MAPS = {0:"huo", 1:"xuan", 2:"lei", 3:"bing"}

class Buff_299039( Buff_Normal ):
	"""
	元素攻击效果buff，火玄雷冰
	"""
	def __init__( self ):
		"""
		构造函数
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
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )

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
		# 添加元素攻击效果
		receiver.setTemp( "ELEM_ATTACK_EFFECT", ELEM_MAPS.get( self._p1, "" ) )

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
		# 添加元素攻击效果
		receiver.setTemp( "ELEM_ATTACK_EFFECT", ELEM_MAPS.get( self._p1, "" ) )

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
		# 去掉元素攻击效果
		receiver.removeTemp( "ELEM_ATTACK_EFFECT" )