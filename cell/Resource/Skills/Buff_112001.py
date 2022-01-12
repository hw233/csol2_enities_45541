# -*- coding: gb18030 -*-
#
# $Id: Buff_22005.py,v 1.2 2008-08-05 08:44:27 kebiao Exp $

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
import csconst

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP
			 
class Buff_112001( Buff_Normal ):
	"""
	example:��ӡ�ں���֮�С������ƶ��͹�����Ҳ�����ܵ��κ��˺���
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
		
	def springOnImmunityBuff( self, caster, receiver, buffData ):
		"""
		@param   caster: ʩ����
		@type    caster: Entity
		@param receiver: �ܻ���
		@type  receiver: Entity
		"""
		buff = buffData[ "skill" ]
		isRayRingEffect = buff.isRayRingEffect()

		if not isRayRingEffect and buff.isMalignant(): #�Ƕ��Ե����ǹ⻷Ч�� ��ô����
			return csstatus.SKILL_BUFF_IS_RESIST
		elif isRayRingEffect:   # �ǹ⻷Ч��
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# �߻��涨�� ������Լ��ͷŵĶ��Թ⻷Ч���� ���޵п�������
				if buffData[ "caster" ] != caster.id:
					buffData[ "state" ] |= csdefine.BUFF_STATE_DISABLED
				else:
					return csstatus.SKILL_BUFF_IS_RESIST
		
		return csstatus.SKILL_GO_ON
		
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
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #������ӵֿ�
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		
		if receiver.isMoving():		# �����ƶ����ƣ���ȷ��buff���ƶ�����Ч����Ч by����
			receiver.stopMoving()

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
		receiver.appendImmunityBuff( buffData[ "skill" ] )
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		
		if receiver.isMoving():		# �����ƶ����ƣ���ȷ��buff���ƶ�����Ч����Ч by����
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
		receiver.removeImmunityBuff( buffData[ "skill" ].getUID() )
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.actCounterDec( STATES )
		
#
# $Log: not supported by cvs2svn $
# Revision 1.1  2008/08/05 06:36:02  kebiao
# no message
#
#
#