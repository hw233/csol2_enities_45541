# -*- coding: gb18030 -*-
#
# $Id: Spell_PhysSkill.py,v 1.18 2008-09-04 07:46:27 kebiao Exp $

"""
������Ч��
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
import SkillTargetObjImpl
import Const

class Spell_PhysSkill( CombatSpell ):
	"""
	������ ���ܱ���Ĺ�����+��ɫ����������  ����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		CombatSpell.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_PHYSICS				# �˺����

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
		return csdefine.BASE_SKILL_TYPE_PHYSICS

	def getRangeMax( self, caster ):
		"""
		virtual method.
		@param caster: ʩ���ߣ�ͨ��ĳЩ��Ҫ���������Ϊ����ķ����ͻ��õ���
		@return: ʩ������
		"""
		return ( self._rangeMax + caster.phySkillRangeVal_value ) * ( 1 + caster.phySkillRangeVal_percent / csconst.FLOAT_ZIP_PERCENT ) + getattr( caster, "modelScale", 1.0 ) * caster.getBoundingBox().z /4.0

	def getCastRange( self, caster ):
		"""
		�����ͷž���
		"""
		return (self._skillCastRange + caster.phySkillRangeVal_value ) * ( 1 + caster.phySkillRangeVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def calcExtraRequire( self, caster ):
		"""
		virtual method.
		���㼼�����ĵĶ���ֵ�� ������װ�����߼���BUFFӰ�쵽���ܵ�����
		return : (�������ĸ���ֵ���������ļӳ�)
		"""
		return ( caster.phyManaVal_value, caster.phyManaVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def calcSkillHitStrength( self, source,receiver, dynPercent, dynValue ):
		"""
		virtual method.
		���㼼�ܹ�����
		��ʽ1�����ܹ��������ܹ�ʽ�еĻ���ֵ��=���ܱ���Ĺ�����+��ɫ����������
		�����ܹ�ʽ�о��ǣ������ܱ���Ĺ�����+��ɫ����������*��1+���������ӳɣ�+����������ֵ
		@param source:	������
		@type  source:	entity
		@param dynPercent:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ������ӳ�
		@param  dynValue:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ�������ֵ
		"""
		#��ɫ��������
		extra = random.randint( int( source.damage_min ), int( source.damage_max ) )
		base = random.randint( self._effect_min, self._effect_max )
		return self.calcProperty( base, extra, dynPercent + source.skill_extra_percent / csconst.FLOAT_ZIP_PERCENT, dynValue + source.skill_extra_value )

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
		#�����Ĭ��һ�༼�ܵ�ʩ���ж�
		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_PHY > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB
		# ��ֹ����ԭ���µĲ���ʩ��
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL_PHY ):
			return csstatus.SKILL_CANT_CAST
		return CombatSpell.useableCheck( self, caster, target )

class Spell_PhysSkill2( Spell_PhysSkill ):
	"""
	������  ���ܱ���Ĺ����� ����
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill.__init__( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )

	def calcSkillHitStrength( self, source,receiver, dynPercent, dynValue ):
		"""
		virtual method.
		���㼼�ܹ�����
		��ʽ2�����ܹ��������ܹ�ʽ�еĻ���ֵ��=���ܱ���Ĺ�����
		�����ܹ�ʽ�о��ǣ����ܱ���Ĺ�����*��1+���������ӳɣ�+����������ֵ
		@param source:	������
		@type  source:	entity
		@param dynPercent:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ������ӳ�
		@param  dynValue:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ�������ֵ
		"""
		base = random.randint( self._effect_min, self._effect_max )
		return self.calcProperty( base, 0, dynPercent + source.skill_extra_percent / csconst.FLOAT_ZIP_PERCENT, dynValue + source.skill_extra_value )

class Spell_PhyVolley( Spell_PhysSkill ):
	"""
	������ ���ܱ���Ĺ�����+��ɫ����������  Ⱥ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill.__init__( self )
		self._skill = ChildSpell( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )
		self._skill.init( dict )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""

		# ��ȡ����������
		receivers = self.getReceivers( caster, target )
		for receiver in receivers:
			receiver.clearBuff( self._triggerBuffInterruptCode )
			self._skill.cast( caster, SkillTargetObjImpl.createTargetObjEntity( receiver ) )
		# ���Լ���ʹ�ô���
		caster.doOnUseMaligSkill( self )

class Spell_PhyVolley2( Spell_PhysSkill2 ):
	"""
	������ ���ܱ���Ĺ�����+��ɫ����������  Ⱥ��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill.__init__( self )
		self._skill = ChildSpell( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )
		self._skill.init( dict )

	def onArrive( self, caster, target ):
		"""
		virtual method = 0.
		�����ִ�Ŀ��ͨ�档��Ĭ������£��˴�ִ�п�������Ա�Ļ�ȡ��Ȼ�����receive()�������ж�ÿ���������߽��д���
		ע���˽ӿ�Ϊ�ɰ��е�receiveSpell()

		@param   caster: ʩ����
		@type    caster: Entity
		@param target: ʩչ����
		@type  target: һ����װ���Ķ���entity ����װ��������� (λ�ã�entity, item)��ϸ�뿴SkillTargetObjImpl.py
		"""

		# ��ȡ����������
		receivers = self.getReceivers( caster, target )
		for receiver in receivers:
			receiver.clearBuff( self._triggerBuffInterruptCode )
			self._skill.cast( caster, SkillTargetObjImpl.createTargetObjEntity( receiver ) )
		# ���Լ���ʹ�ô���
		caster.doOnUseMaligSkill( self )
#
# $Log: not supported by cvs2svn $
# Revision 1.17  2008/08/13 07:55:41  kebiao
# �����ü��ܵ�����
#
# Revision 1.16  2008/07/29 02:57:07  wangshufeng
# ����damage_min��damage_max��Ϊ�����ͣ���������������Ӧ����
#
# Revision 1.15  2008/07/04 03:50:57  kebiao
# ��Ч��״̬��ʵ���Ż�
#
# Revision 1.14  2008/07/03 02:49:39  kebiao
# �ı� ˯�� �����Ч����ʵ��
#
# Revision 1.13  2008/01/15 07:23:09  kebiao
# ȥ�����BUFF���� �ƶ���combatSpell
#
# Revision 1.12  2007/12/25 03:09:39  kebiao
# ����Ч����¼����ΪeffectLog
#
# Revision 1.11  2007/12/13 00:48:08  kebiao
# ����������״̬�ı䲿�֣���Ϊ�ײ�����س�ͻ���� �������Ͳ��ٹ��ĳ�ͻ����
#
# Revision 1.10  2007/12/12 06:01:38  kebiao
# ���ѣ�ε�״̬��ʾ
#
# Revision 1.9  2007/12/12 04:21:10  kebiao
# �޸�ѣ�ε�״̬�ж�
#
# Revision 1.8  2007/12/11 08:05:51  kebiao
# ����Ⱥ�弼��
#
# Revision 1.7  2007/11/27 03:20:02  kebiao
# ���ʩ���ж� �Գ�û��֧��
#
# Revision 1.6  2007/11/26 08:44:09  kebiao
# self._receiverObject.getReceivers( caster, target )
# �޸�Ϊ��������
# getReceivers( self, caster, target )
#
# Revision 1.5  2007/11/26 08:23:22  kebiao
# ���ֻ�㼼�ܹ�������Ⱥ��������
#
# Revision 1.4  2007/11/24 08:31:48  kebiao
# �޸��˽ṹ
#
# Revision 1.3  2007/11/23 02:55:29  kebiao
# ��Ⱥ�巨���������
#
# Revision 1.2  2007/11/20 08:18:40  kebiao
# ս��ϵͳ��2�׶ε���
#
# Revision 1.1  2007/10/26 07:06:24  kebiao
# ����ȫ�µĲ߻�ս��ϵͳ������
#
# Revision 1.15  2007/08/15 03:28:57  kebiao
# �¼���ϵͳ
#
#
#