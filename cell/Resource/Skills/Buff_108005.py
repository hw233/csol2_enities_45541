# -*- coding: gb18030 -*-
#
# $Id: Buff_108003.py,v 1.12 2008-07-04 03:50:57 kebiao Exp $

"""
������Ч��
"""

import BigWorld
import csstatus
import csdefine
from bwdebug import *
from SpellBase import *
from Buff_Normal import Buff_Normal
import random
import time
import csconst

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_JUMP

class Buff_108005( Buff_Normal ):
	"""
	example:����ʼ�ȴ�
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
		self._loopSpeed = 1 # ǿ��3����һ��

	def receive( self, caster, receiver ):
		"""
		���ڸ�Ŀ��ʩ��һ��buff�����е�buff�Ľ��ն�����ͨ���˽ӿڣ�
		�˽ӿڱ����жϽ������Ƿ�ΪrealEntity��
		����������Ҫͨ��receiver.receiveOnReal()�ӿڴ���

		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		Buff_Normal.receive( self, caster, receiver )

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
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )

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
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )

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
		receiver.client.onStatusMessage( csstatus.RACEHORSE_IS_BEGIN, "" )
		receiver.effectStateDec( csdefine.EFFECT_STATE_FIX )
		receiver.actCounterDec( STATES )
		receiver.client.showRaceTime()

	def calculateTime( self, caster ):
		"""
		virtual method.
		ȡ�ó���ʱ��
		"""

		leaveTime = caster.queryTemp( 'horseRaceStartTime',0 ) - time.time() + 0.5

		if leaveTime <= 0: return 1
		return int( time.time() + leaveTime )

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
		spaceType = receiver.getCurrentSpaceData( csconst.SPACE_SPACEDATA_SPACE_TYPE_KEY )
		if not spaceType == str( csdefine.SPACE_TYPE_RACE_HORSE ):
			return False
		return Buff_Normal.doLoop( self, receiver, buffData )