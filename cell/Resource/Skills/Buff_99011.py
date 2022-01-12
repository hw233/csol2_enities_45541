# -*- coding: gb18030 -*-
#
# $Id: Buff_1003.py,v 1.2 2007-12-13 04:59:55 huangyongwei Exp $

"""
������Ч��
"""

import BigWorld
import csdefine
import csconst
import csstatus
import time
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import Const

class Buff_99011( Buff_Normal ):
	"""
	�����赸buff���������Ӿ���
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
		self._p1 = float( dict[ "Param1" ] ) 						# ���Ӿ���Ĺ�ʽ

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
		increaseEXP = self.getIncreaseEXP( receiver.level )
		buffIncreaseEXP = 0

		if not receiver.actionSign( csdefine.ACTION_ALLOW_DANCE ):		# �жϽ�ɫ�Ƿ���������
			return Buff_Normal.doLoop( self, receiver, buffData )

		# �ж��Ƿ�����ʱ���С�����
		if len( receiver.findBuffsByBuffID( Const.JING_WU_SHI_KE_DANCE_BUFF ) ) == 0:		# �жϽ�ɫ�Ƿ�������ʱ����
			#receiver.statusMessage( csstatus.JING_WU_SHI_KE_NO_BUFF_NO_EXP )
			return Buff_Normal.doLoop( self, receiver, buffData )

		if len( receiver.findBuffsByBuffID( Const.JING_WU_SHI_KE_TIAO_WU_YAO_JUE_BUFF ) ) > 0:		# �жϽ�ɫ�Ƿ�������Ҫ��
			buffIncreaseEXP += increaseEXP * 5

		if len( receiver.findBuffsByBuffID( Const.JING_WU_SHI_KE_WU_WANG_MI_JUE_BUFF ) ) > 0:		# �жϽ�ɫ�Ƿ��������ؾ�
			buffIncreaseEXP += increaseEXP * 10

		if buffIncreaseEXP > 0:
			receiver.addExp ( int(buffIncreaseEXP), csdefine.CHANGE_EXP_DANCE )
		else:
			receiver.addExp ( int(increaseEXP), csdefine.CHANGE_EXP_DANCE )

		return Buff_Normal.doLoop( self, receiver, buffData )

	def getIncreaseEXP( self, level ):
		"""
		���ݹ�ʽ������ӵ�Exp
		"""
		return csconst.ACTIVITY_GET_EXP( csdefine.ACTIVITY_TIAO_WU, level )
