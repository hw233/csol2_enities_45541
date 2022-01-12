# -*- coding: gb18030 -*-

from Buff_Normal import Buff_Normal

class Buff_99043( Buff_Normal ):
	"""
	增加物理攻击力x%(英雄王座副本使用)
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
		self._p1 = int( dict["Param1"] if len( dict["Param1"] ) > 0 else 0 ) * 100

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
		receiver.damage_min_percent += self._p1
		receiver.damage_max_percent += self._p1
		receiver.calcDamageMin()
		receiver.calcDamageMax()

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
		receiver.damage_min_percent += self._p1
		receiver.damage_max_percent += self._p1

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
		receiver.damage_min_percent -= self._p1
		receiver.damage_max_percent -= self._p1
		receiver.calcDamageMin()
		receiver.calcDamageMax()