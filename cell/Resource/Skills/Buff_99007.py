# -*- coding: gb18030 -*-

"""
������Ч��
"""

from Buff_Normal import Buff_Normal
import csstatus
import csdefine

class Buff_99007( Buff_Normal ):
	"""
	����ר��buff
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
		m = buff.isMalignant()
		if not buff.isRayRingEffect() and m: #�Ƕ��Ե����ǹ⻷Ч�� ��ô����
			return csstatus.SKILL_BUFF_IS_RESIST
		elif buff.isRayRingEffect() and m:   #�Ƕ������ǹ⻷Ч�� ��ô ʹ��ʧЧ
			buffData[ "state" ] |= csdefine.BUFF_STATE_DISABLED

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
		#receiver.clearBuff( csdefine.BUFF_INTERRUPT_INVINCIBLE_EFFECT ) #ɾ�������������п���ɾ����BUFF
		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			receiver.addBuffState( idx, csdefine.BUFF_STATE_DISABLED )
		receiver.effectStateInc( csdefine.EFFECT_STATE_INVINCIBILITY )
	
	def doReload( self, receiver, buffData ):
		receiver.appendImmunityBuff( buffData[ "skill" ] ) #������ӵֿ�
		#receiver.clearBuff( csdefine.BUFF_INTERRUPT_INVINCIBLE_EFFECT ) #ɾ�������������п���ɾ����BUFF
		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			receiver.addBuffState( idx, csdefine.BUFF_STATE_DISABLED )
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
		for idx in receiver.getBuffIndexsByEffectType( csdefine.SKILL_RAYRING_EFFECT_STATE_MALIGNANT ):
			receiver.removeBuffState( idx, csdefine.BUFF_STATE_DISABLED )
		receiver.effectStateDec( csdefine.EFFECT_STATE_INVINCIBILITY )
		receiver.retractVehicle( receiver.id )

# $Log: not supported by cvs2svn $