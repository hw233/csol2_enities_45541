# -*- coding: gb18030 -*-
#

"""
�Ṧϵͳ-Ѹ���ƶ�buff
"""

import BigWorld
import csdefine
import Const
import csconst
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal


class Buff_6008( Buff_Normal ):
	"""
	example:�ƶ��ٶ����%
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 0
		self._p2 = 0
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 =  int( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) * 100.0 
		self._p2 = int( dict[ "Param2" ] )
		self._loopSpeed = 1 # ǿ��1����һ��
		
	def springOnUseMaligSkill( self, caster, skill ):
		"""
		ʹ�ö��Լ��ܱ�����
		"""
		buffID = self.getBuffID()
		caster.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )

	def springOnDamage( self, caster, skill ):
		"""
		�����˺���
		"""
		buffID = self.getBuffID()
		caster.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )	
		
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
		speed = Const.ROLE_MOVE_SPEED_RADIX / csconst.FLOAT_ZIP_PERCENT
		speed1 = receiver.move_speed
		speed2  = speed1 * (  1 + self._p1 / csconst.FLOAT_ZIP_PERCENT )
		per = receiver.move_speed_percent
		percent = ( speed2 - speed ) / speed * csconst.FLOAT_ZIP_PERCENT - per
		receiver.setTemp("MOVE_SPEED_PERCENT",percent)
		receiver.move_speed_percent += percent
		receiver.calcMoveSpeed()
		
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
		speed = Const.ROLE_MOVE_SPEED_RADIX / csconst.FLOAT_ZIP_PERCENT
		speed1 = receiver.move_speed
		speed2  = speed1 * (  1 + self._p1 / csconst.FLOAT_ZIP_PERCENT )
		per = receiver.move_speed_percent
		percent = ( speed2 - speed ) / speed * csconst.FLOAT_ZIP_PERCENT - per
		receiver.setTemp("MOVE_SPEED_PERCENT",percent)
		receiver.move_speed_percent += percent
		
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
		if receiver.energy < self._p2: #��Ծ����ֵ����
			buffID = self.getBuffID()
			receiver.removeAllBuffByBuffID( buffID, [ csdefine.BUFF_INTERRUPT_NONE ] )
		else:
			receiver.calEnergy( - self._p2 )
		return Buff_Normal.doLoop( self, receiver, buffData )
		
		
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
		percent = receiver.popTemp("MOVE_SPEED_PERCENT",0.0)
		receiver.move_speed_percent -= percent
		receiver.calcMoveSpeed()
		
	