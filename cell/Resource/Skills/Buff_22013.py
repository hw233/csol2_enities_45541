# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
持续性效果
"""

import BigWorld
import csconst
import csstatus# -*- coding: gb18030 -*-
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

class Buff_22013( Buff_Normal ):
	"""
	遇难者的宽恕
	"""
	def __init__( self ):
		"""
		构造函数。
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 #所有不利状态抗性提高百分比
		self._p2 = 0 #物理和魔法防御提高百分比
		
	def init( self, dict ):
		"""
		读取技能配置
		@param dict: 配置数据
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100	
		self._p2 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100	
		
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
		receiver.resist_fix_probability_percent += self._p1
		receiver.calcResistFixProbability()
		receiver.resist_giddy_probability_percent += self._p1
		receiver.calcResistGiddyProbability()
		receiver.resist_sleep_probability_percent += self._p1
		receiver.calcResistSleepProbability()
		receiver.resist_chenmo_probability_percent += self._p1
		receiver.calcResistChenmoProbability()
		receiver.armor_percent += self._p2
		receiver.calcArmor()				
		receiver.magic_armor_percent += self._p2
		receiver.calcMagicArmor()

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
		receiver.resist_fix_probability_percent += self._p1
		receiver.resist_giddy_probability_percent += self._p1
		receiver.resist_sleep_probability_percent += self._p1
		receiver.resist_chenmo_probability_percent += self._p1
		receiver.armor_percent += self._p2
		receiver.magic_armor_percent += self._p2

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
		receiver.resist_fix_probability_percent -= self._p1
		receiver.calcResistFixProbability()
		receiver.resist_giddy_probability_percent -= self._p1
		receiver.calcResistGiddyProbability()
		receiver.resist_sleep_probability_percent -= self._p1
		receiver.calcResistSleepProbability()
		receiver.resist_chenmo_probability_percent -= self._p1
		receiver.calcResistChenmoProbability()
		receiver.armor_percent -= self._p2
		receiver.calcArmor()		
		receiver.magic_armor_percent -= self._p2
		receiver.calcMagicArmor()		