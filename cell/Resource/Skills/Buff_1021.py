# -*- coding:gb18030 -*-

from SpellBase import *
from bwdebug import *
import BigWorld
import csconst
import csstatus
from bwdebug import *
from Buff_Normal import Buff_Normal


class Buff_1021( Buff_Normal ):
	"""
	提高力量、敏捷、智慧、体质X%，增加生命值和法力值A点
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._param1 = 0			# 提高力量、敏捷、智慧、体质X%
		self._param2 = 0			# 增加的生命值
		self._param3 = 0			# 增加的法力值
		
	def init( self, dict ):
		"""
		"""
		Buff_Normal.init( self, dict )
		self._param1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) / 100.0 * csconst.FLOAT_ZIP_PERCENT
		self._param2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )
		self._param3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )
		
	def doBegin( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doBegin( self, receiver, buffData )
		receiver.corporeity_percent += self._param1
		receiver.dexterity_percent += self._param1
		receiver.intellect_percent += self._param1
		receiver.strength_percent += self._param1
		receiver.HP_Max_extra += self._param2
		receiver.MP_Max_extra += self._param3
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
		receiver.corporeity_percent += self._param1
		receiver.dexterity_percent += self._param1
		receiver.intellect_percent += self._param1
		receiver.strength_percent += self._param1
		receiver.HP_Max_extra += self._param2
		receiver.MP_Max_extra += self._param3
		
	def doEnd( self, receiver, buffData ):
		"""
		"""
		Buff_Normal.doEnd( self, receiver, buffData )
		receiver.corporeity_percent -= self._param1
		receiver.dexterity_percent -= self._param1
		receiver.intellect_percent -= self._param1
		receiver.strength_percent -= self._param1
		receiver.HP_Max_extra -= self._param2
		receiver.MP_Max_extra -= self._param3
		receiver.calcDynamicProperties()
		
		