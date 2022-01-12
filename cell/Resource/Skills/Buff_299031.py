# -*- coding: gb18030 -*-
#
# $Id: Buffer_299031.py,edit by wuxo 2011-11-26

"""
��Ƶ����BUFFER
"""

import BigWorld
import csconst
import csstatus
import ECBExtend
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal

class Buff_299031( Buff_Normal ):
	"""
	��Ƶ����BUFFER��������Ƶ������ɺ��һЩ�ͻ��˲���
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = None
		self._p2 = []
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		self._p1 = eval(str( dict[ "Param1" ] ))
		p2 = str( dict[ "Param2" ] )
		monsters = p2.split(";")
		for i in monsters:
			self._p2.append(eval(i))
		
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
		receiver.setTemp( "playCamera_eventID", self._p1[1] )
		receiver.addTimer(self._p1[0],0,ECBExtend.DELAY_PLAYCAMERA_TIMER_CBID)
		#��������
		for i in self._p2 :
			for j in xrange(i[2] ):# �ٹֵĸ���
				receiver.createObjectNearPlanes( i[0], i[1], receiver.direction, {} )
		
