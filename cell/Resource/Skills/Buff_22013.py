# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus# -*- coding: gb18030 -*-
#
# $Id: Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22013( Buff_Normal ):
	"""
	�����ߵĿ�ˡ
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 #���в���״̬������߰ٷֱ�
		self._p2 = 0 #�����ħ��������߰ٷֱ�
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100	
		self._p2 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100	
		
	def doBegin( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		Ч����ʼ�Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
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
		Ч�����¼��صĴ���

		@param receiver: Ч��ҪӰ���ʵ��
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
		Ч�������Ĵ���

		@param receiver: Ч��ҪӰ���ʵ��
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