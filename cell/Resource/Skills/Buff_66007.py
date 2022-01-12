# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_66007( Buff_Normal ):
	"""
	狼化,生命值上限提高x点，物理攻击力提高x点，物理防护值提高x点。
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0	# 生命值提高
		self._p2 = 0	# 物理攻击力提高
		self._p3 = 0	# 物理防御值提高

	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )
		self._p2 = int( float( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  * 100 )
		self._p3 = int( float( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )  * 100 )

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
		receiver.HP_Max_value += self._p1
		receiver.damage_min_value += self._p2
		receiver.damage_max_value += self._p2
		receiver.armor_value += self._p3
		receiver.calcDynamicProperties()


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
		receiver.HP_Max_value += self._p1
		receiver.damage_min_value += self._p2
		receiver.damage_max_value += self._p2
		receiver.armor_value += self._p3


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
		receiver.HP_Max_value -= self._p1
		receiver.damage_min_value -= self._p2
		receiver.damage_max_value -= self._p2
		receiver.armor_value -= self._p3
		receiver.calcDynamicProperties()