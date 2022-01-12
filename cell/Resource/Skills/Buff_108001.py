# -*- coding: gb18030 -*-
#
# $Id: Buff_108001.py,v 1.12 2008-07-04 03:50:57 kebiao Exp $

"""
������Ч��
"""
import random
import BigWorld

import csstatus
import csdefine
from bwdebug import *

import Const
from SpellBase import *
from Buff_Normal import Buff_Normal

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP

class Buff_108001( Buff_Normal ):
	"""
	example:ѣ��
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
		if receiver.attrIntonateTimer > 0 and receiver.attrIntonateSkill.getType() in Const.INTERRUPTED_BASE_TYPE or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		if receiver.isMoving():
			# �����ƶ����ƣ���ȷ��buff���ƶ�����Ч����Ч by����
			receiver.stopMoving()

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
		receiver.effectStateInc( csdefine.EFFECT_STATE_VERTIGO )
		if receiver.isMoving():
			# �����ƶ����ƣ���ȷ��buff���ƶ�����Ч����Ч by����
			receiver.stopMoving()
		
		
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
		receiver.effectStateDec( csdefine.EFFECT_STATE_VERTIGO )
		receiver.actCounterDec( STATES )
		
		
#
# $Log: not supported by cvs2svn $
# Revision 1.11  2008/07/04 01:03:58  kebiao
# �����˽�ֹ��Ծ״̬
#
# Revision 1.10  2008/07/03 02:49:39  kebiao
# �ı� ˯�� �����Ч����ʵ��
#
# Revision 1.9  2007/12/25 03:09:16  kebiao
# ����Ч����¼����ΪeffectLog
#
# Revision 1.8  2007/12/22 03:27:26  kebiao
# �������BUFF����
#
# Revision 1.7  2007/12/22 02:26:57  kebiao
# ����������ؽӿ�
#
# Revision 1.6  2007/12/13 00:48:08  kebiao
# ����������״̬�ı䲿�֣���Ϊ�ײ�����س�ͻ���� �������Ͳ��ٹ��ĳ�ͻ����
#
# Revision 1.5  2007/12/12 06:42:50  kebiao
# �����жϷ�ʽ
#
# Revision 1.4  2007/12/12 04:21:10  kebiao
# �޸�ѣ�ε�״̬�ж�
#
# Revision 1.3  2007/12/11 04:05:17  kebiao
# ����ֿ�BUFF֧��
#
# Revision 1.2  2007/12/05 05:48:59  kebiao
# ��������ʹ�ϵ�״̬
#
# Revision 1.1  2007/11/30 07:11:50  kebiao
# no message
#
# 
#