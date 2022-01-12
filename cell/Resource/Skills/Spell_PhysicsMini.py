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
import csconst
from CombatSystemExp import CombatExp

class Spell_PhysicsMini( MiniCombatSpell ):
	"""
	��ͨ������
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		MiniCombatSpell.__init__( self )
		self._baseType = csdefine.BASE_SKILL_TYPE_PHYSICS_NORMAL
		self._damageType = csdefine.DAMAGE_TYPE_PHYSICS_NORMAL				# �˺����
		
	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		MiniCombatSpell.init( self, dict )

	def calcSkillHitStrength( self, source, receiver,dynPercent, dynValue ):
		"""
		virtual method.
		���㼼�ܹ�����
		���ܹ��������ܹ�ʽ�еĻ���ֵ��= ��ɫ����������
		"""
		#��ͨ������ ֻ��Ҫ����source.damage
		return random.randint( int( source.damage_min ), int( source.damage_max ) )

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

	def receive( self, caster, receiver ):
		"""
		virtual method.
		����������Ҫ��������
		"""
		if not receiver or receiver.isDestroyed:
			return
		armor = self.calcVictimResist( caster, receiver )
		skillDamage = self.calcSkillHitStrength( caster,receiver, 0, 0 )
		finiDamage = skillDamage * ( 1 - armor )
		#�������С��Ƶд�����ʵ�ʼ��� 
		reRate = self.calReduceDamage( caster, receiver )
		rm =  1 - reRate
		finiDamage *= rm
		self.persentDamage( caster, receiver, self._damageType, finiDamage )