# -*- coding: gb18030 -*-
#

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
import time
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_106010( Buff_Normal ):
	"""
	example:�ƶ��ٶȽ���%
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0 
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 )  * 100	
		
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
		receiver.move_speed_percent -= self._p1
		receiver.calcMoveSpeed()
		receiver.setTemp( "buff106010_down_speed", True )

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
		receiver.move_speed_percent -= self._p1
		receiver.setTemp( "buff106010_down_speed", True )
		
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
		receiver.move_speed_percent += self._p1
		receiver.calcMoveSpeed()
		receiver.removeTemp( "buff106010_down_speed" )

	def doLoop( self, receiver, buffData ):
		"""
		Virtual method; call only by real entity.
		����buff����ʾbuff��ÿһ������ʱӦ����ʲô��

		@param receiver: Ч��ҪӰ���ʵ��
		@type  receiver: BigWorld.Entity
		@param buffData: BUFF
		@type  buffData: BUFF
		@return: BOOL�������������򷵻�True�����򷵻�False
		@rtype:  BOOL
		"""
		if receiver.effect_state & csdefine.EFFECT_STATE_INVINCIBILITY > 0:
			if receiver.queryTemp( "buff106010_down_speed", False ):
				receiver.move_speed_percent += self._p1
				receiver.calcMoveSpeed()
				receiver.setTemp( "buff106010_down_speed", False )
		else:
			if not receiver.queryTemp( "buff106010_down_speed", True ):
				receiver.move_speed_percent -= self._p1
				receiver.calcMoveSpeed()
				receiver.setTemp( "buff106010_down_speed", True )
		return Buff_Normal.doLoop( self, receiver, buffData )