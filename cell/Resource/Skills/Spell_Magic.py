# -*- coding: gb18030 -*-
#
# $Id: Spell_Magic.py,v 1.21 2008-09-04 07:46:27 kebiao Exp $

"""
"""

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
from Spell_PhysSkill import Spell_PhysSkill
import SkillTargetObjImpl
from CombatSystemExp import CombatExp
import CombatUnitConfig
import Const

class Spell_Magic( Spell_PhysSkill ):
	"""
	�������弼��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_PhysSkill.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_MAGIC				# �˺����
		self._effectConvert = 1.0	#���û��Ч�� ��ô����Ϊ1.0 ����Ϊ0.95
		self._volleyConvert = 1		#�����Ⱥ�巨����Ҫ��3

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_PhysSkill.init( self, dict )
		# ��ȥ�������ж��Ƿ�Ϊ-1.0 �������� �߻�����Ū���� �����޸�Ϊ�Ƿ�!=0.0
		if float( dict[ "EffectConvert" ] if dict[ "EffectConvert" ] > 0 else 0.0 )  != 0.0:	#Ч�����¸ü���2������е�һ������ ����100%�ͷ�Ч����ô����Ϊ1.0 ����Ϊ0.95
			self._effectConvert = int( dict[ "EffectConvert" ] if dict[ "EffectConvert" ] > 0 else 0 )  / 100.0
		if float( dict[ "VolleyConvert" ] if dict[ "VolleyConvert" ] > 0 else 0.0 )  != 0.0:	#Ч�����¸ü���2������е�һ������ ����100%�ͷ�Ч����ô����Ϊ1.0 ����Ϊ0.95
			self._volleyConvert = int( dict[ "VolleyConvert" ] if dict[ "VolleyConvert" ] > 0 else 0 )

	def getType( self ):
		"""
		ȡ�û�����������
		��Щֵ��BASE_SKILL_TYPE_*֮һ
		"""
		return csdefine.BASE_SKILL_TYPE_MAGIC

	def getRangeMax( self, caster ):
		"""
		virtual method.
		@param caster: ʩ���ߣ�ͨ��ĳЩ��Ҫ���������Ϊ����ķ����ͻ��õ���
		@return: ʩ������
		"""
		return ( self._rangeMax + caster.magicSkillRangeVal_value ) * ( 1 + caster.magicSkillRangeVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def getCastRange( self, caster ):
		"""
		�����ͷž���
		"""
		return ( self._skillCastRange + caster.magicSkillRangeVal_value ) * ( 1 + caster.magicSkillRangeVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def calcExtraRequire( self, caster ):
		"""
		virtual method.
		���㼼�����ĵĶ���ֵ�� ������װ�����߼���BUFFӰ�쵽���ܵ�����
		return : (�������ĸ���ֵ���������ļӳ�)
		"""
		return ( caster.magicManaVal_value, caster.magicManaVal_percent / csconst.FLOAT_ZIP_PERCENT )

	def calcTwoSecondRule( self, source, skillDamageExtra ):
		"""
		virtual method.
		������2��������
		���ڷ������ܹ�������˵�����ĸ���ֵЧ�������¼����������ƣ�
		1)ֻ�е�����������ʱ��t���ڻ����2���ʱ�򣬸÷����������ܵ���ֵ��ȫ��Ч�������ǵ�t����2���ʱ��ȡ2���㡣��tС��2��ʱ��ȡtֵ��
		��1��һ������������ʱ��Ϊ1.5�룬��÷������ܵĸ���ֵΪ������ֵ*1.5/2
		��2��һ������������ʱ��Ϊ6�룬��÷������ܵĸ���ֵΪ������ֵ*2/2��
		2)������÷�����˲����������t=0���ڼ�ֵ�ļ�����ȡ0.8����÷������ܵĸ���ֵΪ������ֵ*0.8/2��
		3)������÷�������һ���ܲ���ĳ�ֶ����Ч�����򸽼�ֵ����0.95�����㡣
		���磺һ����������ʱ��Ϊt(t�����������)���ڻ���Ŀ�������Ŀ����٣���÷������ܵĸ���ֵΪ������ֵ*t/2*0.95��
		4)�������ܹ������˺����ʵ�buffʱ���ַ�Ϊ���������
				A����buffΪ���ܱ���߱�buff
		���༼�ܵ��˺���Ϊ�����˺���buff�˺������ܼ�ֵ��Ч���ֱ�Ϊ70%��30%���缼��A�����жԷ������Է����a~b�Ļ𹥣�ͬʱ���һ���˺�buff����ʮ�ι�20�����c����ˣ���ʱ�������������100�ķ�������������ֵ����ô�����е�70�㹥�������״ι���ʱ�������ã�30��ƽ�ֵ�10��buff���˺��С�
				B����buffΪѧϰ�������ܺ󣬸���ӵ�е�Ч��
		���༼�ܵ��˺���ͬ����Ϊ�����˺���buff�˺��������˺��ֱ����ܹ�����ֵ��Ч����
		�缼��B�����жԷ������Է����a~b�Ļ𹥣���ʱ���ܱ����ǲ��ܲ���buff�ġ�ѧϰ�������ܺ��ܹ����һ���˺�buff����ʮ�ι�20�����c����ˣ���ʱ�������������100�ķ�����������ֵ����ô���״ι���ʱ������100�ķ�����������ͬʱ��100�㷨��������Ҳ��ƽ�ֵ�10��buff�˺��С�

		5)����ֵ��buff��15�����
		ֻ�е�buff�ĳ���ʱ��t���ڻ����15���ʱ�򣬸�buff�������ܵ�����ֵ��ȫ��Ч������t����15���ʱ��ȡ15���㡣��tС��15��ʱ��ȡtֵ��
		��1��һ��buff�ĳ���ʱ��Ϊ10�룬���buff���ܵĸ���ֵΪ������ֵ*10/15
		��2��һ��buff�ĳ���ʱ��Ϊ17�룬��÷������ܵĸ���ֵΪ������ֵ*15/15��

		6)������÷�����Ⱥ�幥����������ô�ڸ���ֵ�ļ����У���Ҫ��1/3�����㡣��
		�÷������ܵĸ���ֵΪ������ֵ*1/3��
		���磺һ��Ⱥ�幥������������˲�����Թ�����Χ�ڵ�Ŀ������˺�����������Ŀ���ƶ��ٶȽ���50%������6�롣��ô�÷������ܵļ�ֵΪ������ֵ*(0.8/2)*0.95/3
		��������ֻ�Ը���ֵ��Ч�����Լӳ���Ч��
		"""
		tVal = 2.0 #2������ȡֵ
		"""�߻��涨�� �̶�ȡ2���ֵ
		itime = self.getIntonateTime( source ) #��������ʱ����ܱ��������ܸı� ����޷��ڳ�ʼ��ʱ���Ż� ֻ�ܶ�̬����
		if itime <= 0:
			tVal = 0.8
		elif itime < 2.0:
			tVal = itime
		"""
		ret = skillDamageExtra * tVal / 2 * self._effectConvert#���һ�������Ч�����������_effectConvert
		return ret / self._volleyConvert

	def calcHitProbability( self, source, target ):
		"""
		virtual method.
		����������
		����������=1-��0.13-����������/10000-0.9��+���ط�����/10000-0.03��-ȡ�����������ȼ�-�ط��ȼ���/5��*0.01��
		���Ϲ�������Ϊ������������ֵ���ط�����Ϊ���ط�������ֵ��
		���ϼ���������1ʱ��ȡ1��С��0.7ʱ��ȡ0.7��

		@param source:	������
		@type  source:	entity
		@param target:	��������
		@type  target:	entity
		return type:	Float
		"""
		hitRate = CombatUnitConfig.calcMagicHitProbability( source, target )
		return max( 0.25, min( 1, hitRate ) )

	def calcSkillHitStrength( self, source,receiver, dynPercent, dynValue ):
		"""
		virtual method.
		���㼼�ܹ�����
		��������������(�ܹ�ʽ�еĻ���ֵ)=����*0.14
		�������ܹ�����(�ܹ�ʽ�еĻ���ֵ)=(�������ܱ���Ĺ�����+��ɫ������������2����������ֵ)*(1+�����������ӳ�)+������������ֵ
		ע�⣺�������ܹ���������������Щ��ͬ�������Ľ�ɫ�������������Է������ܹ�������Чʱ���Ǵ��ڸ���ֵ��λ�á�
		@param source:	������
		@type  source:	entity
		@param dynPercent:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ������ӳ�
		@param  dynValue:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ�������ֵ
		"""
		base = random.randint( self._effect_min, self._effect_max )
		extra = self.calcTwoSecondRule( source, source.magic_damage )
		return self.calcProperty( base, extra * self._shareValPercent, dynPercent + source.magic_skill_extra_percent / csconst.FLOAT_ZIP_PERCENT, dynValue + source.magic_skill_extra_value / csconst.FLOAT_ZIP_PERCENT )

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		���㱻������������������
		��ɫ������������ֵ(�ܹ�ʽ�еĻ���ֵ)=0
		������������(�ܹ�ʽ�еĻ���ֵ)= �������ֵ/(�������ֵ+40*�������ȼ�+350)-0.23
		@param source:	������
		@type  source:	entity
		@param target:	��������
		@type  target:	entity
		@return: FLOAT
		"""
		exp = CombatExp( source, target )
		val = max( 0.0, exp.getMagicDamageReductionRate() )
		if val > 0.95:
			val = 0.95
		return self.calcProperty( val, target.magic_armor_reduce_damage_extra / csconst.FLOAT_ZIP_PERCENT, target.magic_armor_reduce_damage_percent / csconst.FLOAT_ZIP_PERCENT, target.magic_armor_reduce_damage_value / csconst.FLOAT_ZIP_PERCENT )

	def calcDamageScissor( self, caster, receiver, damage ):
		"""
		virtual method.
		���㱻�����������˺�����
		��ʽ���˺�=ֱ�ӷ����˺�x (1 �C �������������˺�������)
		�C	�������������˺�����ֵ
		���������˺��������(�ܹ�ʽ�еĻ���ֵ)=0
		���������˺�����ֵ(�ܹ�ʽ�еĻ���ֵ)=0

		@param receiver: ��������
		@type  receiver: entity
		@param  damage: �����м��жϺ���˺�
		@type   damage: INT
		@return: INT32
		"""
		return caster.calcMagicDamageScissor( receiver, damage )

	def calcDoubleMultiple( self, caster ):
		"""
		virtual method.
		���㱩���˺��ӱ�
		@param caster: ��������
		@type  caster: entity
		@return type:�����õ��ı�������
		"""
		return caster.magic_double_hit_multiple

	def calcDamage( self, source, target, skillDamage ):
		"""
		virtual method.
		����ֱ���˺�
		��ͨ�����˺�(�ܹ�ʽ�еĻ���ֵ)=��������*(1-�������������������)
		���������˺�(�ܹ�ʽ�еĻ���ֵ)=���ܹ�����*(1-�������������������)

		@param source: ������
		@type  source: entity
		@param target: ��������
		@type  target: entity
		@param skillDamage: ���ܹ�����
		@return: INT32
		"""
		# ���㱻�����������������
		armor = self.calcVictimResist( source, target )
		return ( skillDamage * ( 1 - armor ) ) * ( 1 + target.receive_magic_damage_percent / csconst.FLOAT_ZIP_PERCENT ) + target.receive_magic_damage_value

	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		�жϹ������Ƿ񱬻�
		return type:bool
		"""
		return random.random() < ( caster.magic_double_hit_probability + ( receiver.be_magic_double_hit_probability - receiver.be_magic_double_hit_probability_reduce ) / csconst.FLOAT_ZIP_PERCENT )

	def isResistHit( self, caster, receiver ):
		"""
		virtual method.
		�жϱ��������Ƿ��м�
		return type:bool
		"""
		return False # �������ܲ��ɱ��м�

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
		if caster.effect_state & csdefine.EFFECT_STATE_VERTIGO > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_BLACKOUT
		if caster.effect_state & csdefine.EFFECT_STATE_SLEEP > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_SLEEP
		if caster.effect_state & csdefine.EFFECT_STATE_HUSH_MAGIC > 0:
			return csstatus.SKILL_IN_CAST_BAD_STATE_DUMB

		if caster.getState() == csdefine.ENTITY_STATE_RACER:
			return csstatus.SKILL_IN_CAST_RACER

		# ��ֹ����ԭ���µĲ���ʩ��
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
			return csstatus.SKILL_CANT_CAST
		return CombatSpell.useableCheck( self, caster, target )

class Spell_MagicVolley( Spell_Magic ):
	"""
	����Ⱥ�弼��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_Magic.__init__( self )
		self._skill = ChildSpell( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_Magic.init( self, dict )
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
			self.receiveEnemy( caster, receiver )
		# ���Լ���ʹ�ô���
		caster.doOnUseMaligSkill( self )
#
# $Log: not supported by cvs2svn $
# Revision 1.20  2008/08/22 07:07:57  kebiao
# �޸������ʹ�ʽ�̶�0.9
#
# Revision 1.19  2008/08/13 07:55:41  kebiao
# �����ü��ܵ�����
#
# Revision 1.18  2008/07/15 04:06:42  kebiao
# �����������޸ĵ�datatool��س�ʼ����Ҫ�޸�
#
# Revision 1.17  2008/07/04 03:50:57  kebiao
# ��Ч��״̬��ʵ���Ż�
#
# Revision 1.16  2008/07/03 02:49:39  kebiao
# �ı� ˯�� �����Ч����ʵ��
#
# Revision 1.15  2008/02/25 09:29:42  kebiao
# �޸� ���ܼ������
#
# Revision 1.14  2008/02/25 03:35:56  kebiao
# ���������ʼ��㹫ʽ
#
# Revision 1.13  2007/12/25 03:09:39  kebiao
# ����Ч����¼����ΪeffectLog
#
# Revision 1.12  2007/12/13 00:48:08  kebiao
# ����������״̬�ı䲿�֣���Ϊ�ײ�����س�ͻ���� �������Ͳ��ٹ��ĳ�ͻ����
#
# Revision 1.11  2007/12/12 06:01:38  kebiao
# ���ѣ�ε�״̬��ʾ
#
# Revision 1.10  2007/12/12 04:21:10  kebiao
# �޸�ѣ�ε�״̬�ж�
#
# Revision 1.9  2007/12/11 08:05:51  kebiao
# ����Ⱥ�弼��
#
# Revision 1.8  2007/11/29 03:46:52  kebiao
# ����BUG
#
# Revision 1.7  2007/11/28 01:46:31  kebiao
# �޸�calcDamage��ʽ
#
# Revision 1.6  2007/11/26 08:44:09  kebiao
# self._receiverObject.getReceivers( caster, target )
# �޸�Ϊ��������
# getReceivers( self, caster, target )
#
# Revision 1.5  2007/11/24 08:31:48  kebiao
# �޸��˽ṹ
#
# Revision 1.4  2007/11/23 02:55:08  kebiao
# ��Ⱥ�巨���������
#
# Revision 1.3  2007/11/22 07:23:40  kebiao
# �����������˼���
#
# Revision 1.2  2007/11/20 08:18:40  kebiao
# ս��ϵͳ��2�׶ε���
#
# Revision 1.1  2007/10/26 07:06:24  kebiao
# ����ȫ�µĲ߻�ս��ϵͳ������
#
#