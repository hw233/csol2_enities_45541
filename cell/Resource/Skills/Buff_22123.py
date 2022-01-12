# -*- coding: gb18030 -*-
#
# $Id: Buff_1003.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
������Ч��
"""

import BigWorld
import csconst
import csstatus
import csdefine
import time
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import Const

class Buff_22123( Buff_Normal ):
	"""
	�����������buff
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
		if not receiver.wallow_getLucreRate(): # �������Ϊ0���򲻽���
			return Buff_Normal.doLoop( self, receiver, buffData )

		if not receiver.actionSign( csdefine.ACTION_ALLOW_DANCE ):		# �жϽ�ɫ�Ƿ���������
			return Buff_Normal.doLoop( self, receiver, buffData )

		if receiver.dancePointDailyRecord.getDegree() >= Const.JING_WU_SHI_KE_MAX_POINT_ONE_DAY:	# �����ɫ�ﵽһ������ۻ���
			return
		if receiver.dancePoint < Const.JING_WU_SHI_KE_MAX_POINT:		# �����ɫ�������û�дﵽ����ۻ���
			receiver.dancePoint += 1
			receiver.dancePointDailyRecord.incrDegree()
			receiver.statusMessage( csstatus.JING_WU_SHI_KE_GET_POINT )

		return Buff_Normal.doLoop( self, receiver, buffData )
