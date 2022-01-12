# -*- coding: gb18030 -*-


import BigWorld
from bwdebug import *

from SpellBase import *
from Skill_Damage import Skill_Damage

import csconst
import csdefine
import csstatus
import random
import CombatUnitConfig
from CombatSystemExp import CombatExp


class Skill_PhyDamage( Skill_Damage ):
	"""
	���������˺���:�����˺�

	Ŀǰ��������,��������ĿǰΪֹȷ����һЩ��Ϊ����Ӧװ���������Լ��ܵ�����,
	�Ժ���Ҫ�Ա������ܽṹ��������滮.11:14 2008-10-24,wsf
	"""
	def __init__( self ):
		"""
		"""
		Skill_Damage.__init__( self )


	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Skill_Damage.init( self, dict )


	def isDoubleHit( self, caster, receiver ):
		"""
		virtual method.
		�жϹ������Ƿ񱬻�
		return type:bool
		"""
		return random.random() < ( caster.double_hit_probability + ( receiver.be_double_hit_probability - receiver.be_double_hit_probability_reduce ) / csconst.FLOAT_ZIP_PERCENT )


	def calcDoubleMultiple( self, caster ):
		"""
		virtual method.
		���㱩���˺��ӱ�
		@param caster: ��������
		@type  caster: entity
		@return type:�����õ��ı�������
		"""
		return caster.double_hit_multiple

	def calcHitProbability( self, source, target ):
		"""
		virtual method.
		����������
		��������
		����������=1-��0.13-����������/10000-0.9��+���ط�����/10000-0.03��-ȡ�����������ȼ�-�ط��ȼ���/5��*0.01��
		���Ϲ�������Ϊ������������ֵ���ط�����Ϊ���ط�������ֵ�����ϼ���������1ʱ��ȡ1��С��0.7ʱ��ȡ0.7

		@param source:	������
		@type  source:	entity
		@param target:	��������
		@type  target:	entity
		return type:	Float
		"""
		hitRate = CombatUnitConfig.calcHitProbability( source, target )
		return hitRate > 1 and 1 or max( 0.7, hitRate )

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		���㱻�����������������
		��ɫ�����������ֵ���ܹ�ʽ�еĻ���ֵ��=0
		����������ˣ��ܹ�ʽ�еĻ���ֵ��=�������ֵ/���������ֵ+40*�������ȼ�+350��-0.23
		�ڹ����ļ����У�����ֵ���Ȼ���ɷ������ˣ�Ȼ���ٺ͹��������л��㡣
		@param source:	������
		@type  source:	entity
		@param target:	��������
		@type  target:	entity
		@return: FLOAT
		"""
		exp = CombatExp( source, target )
		val = max( 0.0, exp.getPhysicsDamageReductionRate() )
		if val > 0.95:
			val = 0.95
		return self.calcProperty( val, target.armor_reduce_damage_extra / csconst.FLOAT_ZIP_PERCENT, target.armor_reduce_damage_percent / csconst.FLOAT_ZIP_PERCENT, target.armor_reduce_damage_value / csconst.FLOAT_ZIP_PERCENT )



