# -*- coding: gb18030 -*-
#
# $Id: Buff_108001.py,v 1.12 2008-07-04 03:50:57 kebiao Exp $

"""
������Ч��
"""

import BigWorld

import csstatus
import csdefine
from bwdebug import *

import Const
from SpellBase import *
from Buff_Normal import Buff_Normal

STATES = csdefine.ACTION_FORBID_MOVE | csdefine.ACTION_FORBID_ATTACK | csdefine.ACTION_FORBID_SPELL | csdefine.ACTION_FORBID_JUMP | csdefine.ACTION_FORBID_USE_ITEM

class Buff_12013( Buff_Normal ):
	"""
	example:"��������10���ڲ����κ��˺�����Ҳ�����ƶ�����ʹ�ü��ܣ�������ȡ����
	����״̬�£�ÿ2��ָ�һ�������ͷ������ܼƻָ������ͷ������޵�30%(31��)/45%(60��)������������ȡ������״ֹ̬ͣ�ָ���"

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
		self._p1 = float( dict[ "Param1" ] if len( dict[ "Param1" ] ) > 0 else 0 ) / 100.0
		
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
		if receiver.attrIntonateTimer > 0 or\
			( receiver.attrHomingSpell and receiver.attrHomingSpell.getType() in Const.INTERRUPTED_BASE_TYPE ) :
			receiver.interruptSpell( csstatus.SKILL_IN_BLACKOUT )

		dels = []
		
		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			buff = receiver.getBuff( idx )
			if buff.getEffectState() == csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT:
				# �߻��涨�� ������Լ��ͷŵĶ��Թ⻷Ч���� ���޵п�������
				if buffData[ "caster" ] == caster.id:
					dels.append( idx )
				else:				
					receiver.addBuffState( idx, csdefine.BUFF_STATE_DISABLED )
					
		for i in dels:
			receiver.removeBuff( i, [ 0 ] )
			
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )
		
		if receiver.isMoving():
			receiver.stopMoving()

		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		
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
		receiver.setHP( receiver.HP + int( receiver.HP_Max * self._p1 ) )
		receiver.setMP( receiver.MP + int( receiver.MP_Max * self._p1 ) )
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
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #������ӵֿ�
		# ִ�и���Ч��
		receiver.actCounterInc( STATES )
		receiver.effectStateInc( csdefine.EFFECT_STATE_FIX )
		
		if receiver.isMoving():
			receiver.stopMoving()
		
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
		
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
		receiver.effectStateDec( csdefine.EFFECT_STATE_FIX )
		receiver.actCounterDec( STATES )
		
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		
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
		
#
# 
#