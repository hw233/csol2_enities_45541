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
	������������ݡ��ǻۡ�����X%����������ֵ�ͷ���ֵA��
	"""
	def __init__( self ):
		"""
		"""
		Buff_Normal.__init__( self )
		self._param1 = 0			# ������������ݡ��ǻۡ�����X%
		self._param2 = 0			# ���ӵ�����ֵ
		self._param3 = 0			# ���ӵķ���ֵ
		
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
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
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
		
		