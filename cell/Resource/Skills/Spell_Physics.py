# -*- coding: gb18030 -*-
#
# $Id: Spell_Physics.py,v 1.28 2008-08-13 07:55:41 kebiao Exp $

"""
������Ч��
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
from bwdebug import *
import Const

class Spell_Physics( CombatSpell ):
	"""
	��ͨ������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		CombatSpell.__init__( self )
		self._baseType = csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL
		self._damageType = csdefine.DAMAGE_TYPE_PHYSICS_NORMAL				# �˺����

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		CombatSpell.init( self, dict )

	def getType( self ):
		"""
		ȡ�û�����������
		��Щֵ��BASE_SKILL_TYPE_*֮һ
		"""
		return csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL

	def calcSkillHitStrength( self, source,receiver, dynPercent, dynValue ):
		"""
		virtual method.
		���㼼�ܹ�����
		���ܹ��������ܹ�ʽ�еĻ���ֵ��= ��ɫ����������
		"""
		#��ͨ������ ֻ��Ҫ����source.damage
		return random.randint( int( source.damage_min ), int( source.damage_max ) )

	def getRangeMax( self, caster ):
		"""
		virtual method.
		ȡ�ù�������
		"""
		return caster.range + getattr( caster, "modelScale", 1.0 ) * caster.getBoundingBox().z /4.0

	def getCastRange( self, caster ):
		"""
		�����ͷž���
		"""
		return self.getRangeMax( caster ) + 0.5

	def useableCheck( self, caster, target ):
		"""
		virtual method.
		У�鼼���Ƿ����ʹ�á�
		return: SkillDefine::SKILL_*;Ĭ�Ϸ���SKILL_UNKNOW
		ע���˽ӿ��Ǿɰ��е�validUse()

		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return:           INT��see also csdefine.SKILL_*
		@rtype:            INT
		"""
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER

		if caster.actionSign( csdefine.ACTION_FORBID_ATTACK ):
			return csstatus.SKILL_CANT_ATTACK

		state = CombatSpell.useableCheck( self, caster, target )
		if state != csstatus.SKILL_GO_ON:
			return state

		# ��鹥���ӳ�
		if not caster.hitDelayOver():
			return csstatus.SKILL_NOT_HIT_TIME
		return csstatus.SKILL_GO_ON

	def onSkillCastOver_( self, caster, target ):
		"""
		virtual method.
		����ʩ�����֪ͨ
		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""
		#���㹥���ӳ�ʱ�䣬 ��һ�ι���ʱ����ʱ�� ʱ�䵽�˲ſ��Լ�������
		#caster.hitDelay = BigWorld.time() + caster.hit_speed
		caster.setHitDelay()
		CombatSpell.onSkillCastOver_( self, caster, target )

	def getReceivers( self, caster, target ):
		"""
		ȡ�����еķ���������������Entity�б�
		���е�onArrive()������Ӧ�õ��ô˷�������ȡ��Ч��entity��

		@rtype: list of Entity
		"""
		entity = target.getObject()
		if entity is None:
			return []
		return [ entity ]

	def calcDelay( self, caster, target ):
		"""
		virtual method.
		ȡ���˺��ӳ�
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		@return: float(��)
		"""
		return CombatSpell.calcDelay( self, caster, target ) + 0.7

#
# $Log: not supported by cvs2svn $
# Revision 1.27  2008/07/29 02:56:38  wangshufeng
# ����damage_min��damage_max��Ϊ�����ͣ���������������Ӧ����
#
# Revision 1.26  2008/07/04 03:50:57  kebiao
# ��Ч��״̬��ʵ���Ż�
#
# Revision 1.25  2008/07/03 02:49:39  kebiao
# �ı� ˯�� �����Ч����ʵ��
#
# Revision 1.24  2008/03/03 06:34:23  kebiao
# SKILL getRange to getRangeMax
#
# Revision 1.23  2008/02/02 09:09:52  phw
# method modified: calcDelay(), change extra delay from 1.0 to 0.7
#
# Revision 1.22  2008/02/02 08:33:48  kebiao
# ����ӳ�ʱ��1��
#
# Revision 1.21  2007/12/25 03:09:39  kebiao
# ����Ч����¼����ΪeffectLog
#
# Revision 1.20  2007/12/13 06:52:32  kebiao
# ���������� ��� ���� ���� ʹ��һ����ͨ������
#
# Revision 1.19  2007/12/12 06:01:38  kebiao
# ���ѣ�ε�״̬��ʾ
#
# Revision 1.18  2007/12/12 04:21:10  kebiao
# �޸�ѣ�ε�״̬�ж�
#
# Revision 1.17  2007/12/05 07:43:58  kebiao
# ������ע��
#
# Revision 1.16  2007/11/20 08:18:40  kebiao
# ս��ϵͳ��2�׶ε���
#
# Revision 1.15  2007/10/26 07:06:24  kebiao
# ����ȫ�µĲ߻�ս��ϵͳ������
#
# Revision 1.15  2007/08/15 03:28:57  kebiao
# �¼���ϵͳ
#
#
#
