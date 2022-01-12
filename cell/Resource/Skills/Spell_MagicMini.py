# -*- coding: gb18030 -*-

import random
import csdefine
import csstatus
from SpellBase import *
import BigWorld
import csconst
from bwdebug import *
from CombatSystemExp import CombatExp
import SkillTargetObjImpl

class Spell_MagicMini( MiniCombatSpell ):
	"""
	���������弼��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		MiniCombatSpell.__init__( self )
		self._damageType = csdefine.DAMAGE_TYPE_MAGIC				# �˺����

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		MiniCombatSpell.init( self, dict )

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

	def calcSkillHitStrength( self, source, receiver,dynPercent, dynValue ):
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
		return source.magic_damage

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		���㱻������������������
		��ɫ������������ֵ(�ܹ�ʽ�еĻ���ֵ)=0
		������������(�ܹ�ʽ�еĻ���ֵ)= ��������ֵ/(��������ֵ+40*�������ȼ�+350)-0.23
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
			
		# ��ֹ����ԭ���µĲ���ʩ��
		if caster.actionSign( csdefine.ACTION_FORBID_SPELL_MAGIC ):
			return csstatus.SKILL_CANT_CAST
		return CombatSpell.useableCheck( self, caster, target )
		
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

class Spell_MagicVolleyMini( Spell_MagicMini ):
	"""
	������Ⱥ�弼��
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		Spell_MagicMini.__init__( self )
		self._skill = ChildSpell( self )

	def init( self, dict ):
		"""
		��ȡ��������
		@param dict: ��������
		@type  dict: python dict
		"""
		Spell_MagicMini.init( self, dict )
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
			self._skill.cast( caster, SkillTargetObjImpl.createTargetObjEntity( receiver ) )
			self.receiveEnemy( caster, receiver )

#