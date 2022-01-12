# -*- coding: gb18030 -*-
#
# $Id: Buff_99018.py,v 1.2 2009-09-19 08:01:12 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import Const
import csstatus
import csdefine
from Function import newUID
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import time

class Buff_99018( Buff_Normal ):
	"""
	example: ��������	�ڼ�����PKֵ���ٵĸ��졣
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._rate = float( dict[ "Param1" ] ) - 1.0

	def startNewPkValueTimer( self, receiver ):
		"""
		"""
		# ��ֹͣpkֵ����timer 
		receiver.endPkValueTimer()
		
		# ʹ���µ�timer�ٶ�
		val = Const.PK_VALUE_PRISON_LESS_TIME - ( Const.PK_VALUE_PRISON_LESS_TIME * self._rate )
		DEBUG_MSG( "NewPkValueTimer tick = %i" % val )
		receiver.startPkValueTimer( val, val )
	
	def restorePkValueTimer( self, receiver ):
		"""
		"""
		if receiver.pkValue <= 0:
			return
			
		# ��ֹͣpkֵ����timer 
		receiver.endPkValueTimer()
		receiver.startPkValueTimer()
		
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
		self.startNewPkValueTimer( receiver )
		receiver.statusMessage( csstatus.PRISON_BUFF_GOOD )
		
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
		# receiver.setPkValue( receiver.pkValue - 1 )
		spaceKey = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_KEY )
		if spaceKey != "fu_ben_jian_yu":
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )
		
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
		self.startNewPkValueTimer( receiver )
		
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
		self.restorePkValueTimer( receiver )
































