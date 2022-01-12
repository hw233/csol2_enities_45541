# -*- coding: gb18030 -*-
#

"""
������Ч��edit by wuxo
"""

import csdefine
from bwdebug import *
from Buff_Normal import Buff_Normal
from VehicleHelper import getCurrVehicleID

class Buff_8008( Buff_Normal ):
	"""
	������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Buff_Normal.__init__( self )
		self._p1 = 1
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Buff_Normal.init( self, dict )
		if dict[ "Param1" ] != "":
			self._p1 = int( dict[ "Param1" ])
		
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
		if self._p1 == 1:
			if getCurrVehicleID( receiver ): # �����������ϣ�ǿ�������
				receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )

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
		if self._p1 == 1:
			if getCurrVehicleID( receiver ): # �����������ϣ�ǿ�������
				receiver.clearBuff( [csdefine.BUFF_INTERRUPT_RETRACT_VEHICLE] )
		
