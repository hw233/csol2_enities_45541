# -*- coding: gb18030 -*-
#
# $Id: Buff_6001.py,v 1.3 2008-09-04 07:46:27 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_22124( Buff_Normal ):
	"""
	example:�ƶ��ٶ����%�������½�%�������½�%

	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0
		self._p2 = 0.0
		self._p3 = 0.0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = ( int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  / 100.0 ) * csconst.FLOAT_ZIP_PERCENT
		self._p2 = int( dict[ "Param2" ] if len( dict[ "Param2" ] ) > 0 else 0 )  * 100		# ������������������������x%��
		self._p3 = int( dict[ "Param3" ] if len( dict[ "Param3" ] ) > 0 else 0 )  * 100		# ���������������������x%��
		
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
		receiver.move_speed_percent += self._p1
		receiver.calcMoveSpeed()
		
		receiver.magic_damage_percent -= self._p2
		receiver.damage_min_percent -= self._p2
		receiver.damage_max_percent -= self._p2
		receiver.armor_percent -= self._p3
		receiver.magic_armor_percent -= self._p3
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
		receiver.move_speed_percent += self._p1

		receiver.magic_damage_percent -= self._p2
		receiver.damage_min_percent -= self._p2
		receiver.damage_max_percent -= self._p2
		receiver.armor_percent -= self._p3
		receiver.magic_armor_percent -= self._p3
		
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
		receiver.move_speed_percent -= self._p1
		receiver.calcMoveSpeed()

		receiver.magic_damage_percent += self._p2
		receiver.damage_min_percent += self._p2
		receiver.damage_max_percent += self._p2
		receiver.armor_percent += self._p3
		receiver.magic_armor_percent += self._p3
		receiver.calcDynamicProperties()
#