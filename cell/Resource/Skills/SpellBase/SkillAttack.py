# -*- coding: gb18030 -*-
#
# $Id: SkillAttack.py,v 1.17 2008-09-04 07:46:42 kebiao Exp $

"""
����ս��������� (spell,buff)
"""

from bwdebug import *
import BigWorld
import random
import csdefine
import csstatus
import SkillMessage
import csconst
from CombatSystemExp import CombatExp
import CombatUnitConfig

class SkillAttack:
	"""
	����ս��������� (spell,buff)
	"""
	def __init__( self ):
		"""
		���캯����
		"""
		self._damageType = csdefine.DAMAGE_TYPE_VOID				# �˺����
		self._shareValPercent = 1.0 #������ֵ�ļ������
		self._huo_damage = 0
		self._xuan_damage = 0
		self._lei_damage = 0
		self._bing_damage = 0

	def init( self, dictDat ):
		"""
		��ʼ������ʵ����
		@param dicDat:	������������
		@type  dictDat:	python �ֵ�����
		"""
		if dictDat[ "ShareValPercent" ] != -1.0:
			self._shareValPercent = dictDat[ "ShareValPercent" ] / 100.0

		if dictDat.has_key( "huo_damage" ):
			self._huo_damage = int( dictDat[ "huo_damage" ] )
		if dictDat.has_key( "xuan_damage" ):
			self._xuan_damage = int( dictDat[ "xuan_damage" ]  )
		if dictDat.has_key( "lei_damage" ):
			self._lei_damage = int( dictDat[ "lei_damage" ]  )
		if dictDat.has_key( "bing_damage" ):
			self._bing_damage = int( dictDat[ "bing_damage" ] )

	def calcProperty( self, baseVal, extraVal, percentVal, value ):
		"""
		�������������ܹ�ʽ
		����ֵ=������ֵ+����ֵ��*��1+�ӳɣ�+��ֵ
		@param baseVal: ����ֵ
		@param extraVal: ����ֵ
		@param percentVal: �ӳ�
		@param value: ��ֵ
		"""
		return ( baseVal + extraVal ) * ( 1 + percentVal ) + value

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
		return max( 0.25, min( 1, hitRate ) )

	def calcSkillHitStrength( self, source, receiver, dynPercent, dynValue ):
		"""
		virtual method.
		���㼼�ܹ�����
		���ܹ��������ܹ�ʽ�еĻ���ֵ��= ���ܱ���Ĺ�����+��ɫ����������
		@param source:	������
		@type  source:	entity
		@param dynPercent:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ������ӳ�
		@param  dynValue:	�ڱ��ι��������п��ܻ����ⲿ�������ܵ��¶���� ���ܹ�������ֵ
		"""
		ERROR_MSG( "missing the function is need of implement!" )

	def calcVictimResist( self, source, target ):
		"""
		virtual method.
		���㱻�����������������
		��ɫ�����������ֵ���ܹ�ʽ�еĻ���ֵ��=0
		����������ˣ��ܹ�ʽ�еĻ���ֵ��= ����ֵ/(0.1*����ֵ+150*�������ȼ�+1000)
		�ڹ����ļ����У�����ֵ���Ȼ���ɷ������ˣ�Ȼ���ٺ͹��������л��㡣
		@param source:	������
		@type  source:	entity
		@param target:	��������
		@type  target:	entity
		@return: FLOAT
		"""
		exp = CombatExp( source, target )

		val = max( 0.0,  exp.getPhysicsDamageReductionRate() )
		if val > 0.95:
			val = 0.95
		return self.calcProperty( val, target.armor_reduce_damage_extra / csconst.FLOAT_ZIP_PERCENT, target.armor_reduce_damage_percent / csconst.FLOAT_ZIP_PERCENT, target.armor_reduce_damage_value / csconst.FLOAT_ZIP_PERCENT )

	def calcDamage( self, source, target, skillDamage ):
		"""
		virtual method.
		����ֱ���˺�
		��ͨ�����˺����ܹ�ʽ�еĻ���ֵ��=��������*��1-������������������ˣ�
		���������˺����ܹ�ʽ�еĻ���ֵ��=���ܹ�����*��1-������������������ˣ�

		@param source: ������
		@type  source: entity
		@param target: ��������
		@type  target: entity
		@param skillDamage: ���ܹ�����
		@return: INT32
		"""
		# ���㱻�����������������
		armor = self.calcVictimResist( source, target )
		return ( skillDamage * ( 1 - armor ) ) * ( 1 + target.receive_damage_percent / csconst.FLOAT_ZIP_PERCENT ) + target.receive_damage_value

	def calcDamageScissor( self, caster, receiver, damage ):
		"""
		virtual method.
		���㱻�����������˺�����
		�˺�=�����˺�x (1 �C �������������˺�������)
		�C �������������˺�����ֵ
		�˺�����Ϊ0��
		ע���˺�ΪDOT�ͳ����˺�������˺���ֵ�������ٷִ����á�
		���У������˺������ʼ������˺�����ֵ�ο���ʽ�ĵ�����ʽ���£�
		��ɫ���������˺�����������ܹ�ʽ�еĻ���ֵ��=0
		��ɫ���������˺�����ֵ���ܹ�ʽ�еĻ���ֵ��=0
		@param target: ��������
		@type  target: entity
		@param  damage: �����м��жϺ���˺�
		@type   damage: INT
		@return: INT32
		"""
		return caster.calcDamageScissor( receiver, damage )

	def calcDoubleMultiple( self, caster ):
		"""
		virtual method.
		���㱩���˺��ӱ�
		@param caster: ��������
		@type  caster: entity
		@return type:�����õ��ı�������
		"""
		return caster.double_hit_multiple

	def calcElemDamage( self, caster, receiver, attackdamage = 0 ):
		"""
		virtual method.
		����Ԫ���˺�
		"""
		elemEffect = caster.queryTemp( "ELEM_ATTACK_EFFECT", "" )
		if elemEffect == "huo":		# ��Ԫ�ع���Ч��
			return [ caster.elem_huo_damage + self._huo_damage + attackdamage, \
					caster.elem_xuan_damage + self._xuan_damage, \
					caster.elem_lei_damage + self._lei_damage, \
					caster.elem_bing_damage + self._bing_damage ]
		elif elemEffect == "xuan":	# ��Ԫ�ع���Ч��
			return [ caster.elem_huo_damage + self._huo_damage, \
					caster.elem_xuan_damage + self._xuan_damage + attackdamage, \
					caster.elem_lei_damage + self._lei_damage, \
					caster.elem_bing_damage + self._bing_damage ]
		elif elemEffect == "lei":	# ��Ԫ�ع���Ч��
			return [ caster.elem_huo_damage + self._huo_damage, \
					caster.elem_xuan_damage + self._xuan_damage, \
					caster.elem_lei_damage + self._lei_damage + attackdamage, \
					caster.elem_bing_damage + self._bing_damage ]
		elif elemEffect == "bing":	# ��Ԫ�ع���Ч��
			return [ caster.elem_huo_damage + self._huo_damage, \
					caster.elem_xuan_damage + self._xuan_damage, \
					caster.elem_lei_damage + self._lei_damage, \
					caster.elem_bing_damage + self._bing_damage + attackdamage ]
		else:
			return [ caster.elem_huo_damage + self._huo_damage, \
					caster.elem_xuan_damage + self._xuan_damage, \
					caster.elem_lei_damage + self._lei_damage, \
					caster.elem_bing_damage + self._bing_damage ]

	def calcElemDamageDeep( self, receiver, elemDamageList ):
		"""
		virtual method.
		Ԫ���˺�������������ܵ���Ԫ���˺����x%
		"""
		if elemDamageList[ 0 ] > 0:
			elemDamageList[ 0 ] = self.calcElemDamageDeepByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_HUO, elemDamageList[ 0 ] )
		if elemDamageList[ 1 ] > 0:
			elemDamageList[ 1 ] = self.calcElemDamageDeepByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_XUAN, elemDamageList[ 1 ] )
		if elemDamageList[ 2 ] > 0:
			elemDamageList[ 2 ] = self.calcElemDamageDeepByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_LEI, elemDamageList[ 2 ] )
		if elemDamageList[ 3 ] > 0:
			elemDamageList[ 3 ] = self.calcElemDamageDeepByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_BING, elemDamageList[ 3 ] )

	def calcElemDamageDeepByElemType( self, receiver, elemType, elemDamage ):
		"""
		virtual method.
		����Ԫ���˺����ͼ���Ԫ���˺�����ֵ
		"""
		if elemDamage <= 0:
			return elemDamage

		deep_ratio = 0.0
		if elemType == csdefine.DAMAGE_TYPE_ELEM_HUO:
			deep_ratio = receiver.elem_huo_deep_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_XUAN:
			deep_ratio = receiver.elem_xuan_deep_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_LEI:
			deep_ratio = receiver.elem_lei_deep_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_BING:
			deep_ratio = receiver.elem_bing_deep_ratio
		return elemDamage * ( 1 + deep_ratio / csconst.FLOAT_ZIP_PERCENT )

	def calcElemDamageScissor( self, receiver, elemDamageList ):
		"""
		virtual method.
		���㱻������Ԫ���˺�����
		��ɫ�ܵ����ԶԷ����˺�Ϊ100�����˺�+30��Ԫ���˺�����������Ԫ�ؿ���Ϊ0ʱ��
		���ղ������˺�����130�㡣������������Ϊ20%�����ܵ��������˺���100�����˺�+30*(1-20%)��Ԫ���˺�=124�㡣
		"""
		if elemDamageList[ 0 ] > 0:
			elemDamageList[ 0 ] = self.calcElemDamageScissorByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_HUO, elemDamageList[ 0 ] )
		if elemDamageList[ 1 ] > 0:
			elemDamageList[ 1 ] = self.calcElemDamageScissorByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_XUAN, elemDamageList[ 1 ] )
		if elemDamageList[ 2 ] > 0:
			elemDamageList[ 2 ] = self.calcElemDamageScissorByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_LEI, elemDamageList[ 2 ] )
		if elemDamageList[ 3 ] > 0:
			elemDamageList[ 3 ] = self.calcElemDamageScissorByElemType( receiver, csdefine.DAMAGE_TYPE_ELEM_BING, elemDamageList[ 3 ] )

	def calcElemDamageScissorByElemType( self, receiver, elemType, elemDamage ):
		"""
		virtual method.
		���㱻������Ԫ���˺�����
		��ɫ�ܵ����ԶԷ����˺�Ϊ100�����˺�+30��Ԫ���˺�����������Ԫ�ؿ���Ϊ0ʱ��
		���ղ������˺�����130�㡣������������Ϊ20%�����ܵ��������˺���100�����˺�+30*(1-20%)��Ԫ���˺�=124�㡣
		"""
		if elemDamage <= 0:
			return elemDamage

		derate_ratio = 0.0
		if elemType == csdefine.DAMAGE_TYPE_ELEM_HUO:
			derate_ratio = receiver.elem_huo_derate_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_XUAN:
			derate_ratio = receiver.elem_xuan_derate_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_LEI:
			derate_ratio = receiver.elem_lei_derate_ratio
		elif elemType == csdefine.DAMAGE_TYPE_ELEM_BING:
			derate_ratio = receiver.elem_bing_derate_ratio
		return elemDamage * ( 1 - derate_ratio / csconst.FLOAT_ZIP_PERCENT )

	def calcShieldSuck( self, caster, receiver, attackDamage, attackDamageType, elemDamageList ):
		"""
		virtual method.
		���㻤������
		"""
		if len( receiver.shields ) > 0:
			if attackDamage > 0:
				newdamage = caster.calcShieldSuck( receiver, attackDamage, attackDamageType )
			else:
				newdamage = attackDamage

			if elemDamageList[ 0 ] > 0:
				elemDamageList[ 0 ] = caster.calcShieldSuck( receiver, elemDamageList[ 0 ], csdefine.DAMAGE_TYPE_ELEM_HUO )
			if elemDamageList[ 1 ] > 0:
				elemDamageList[ 1 ] = caster.calcShieldSuck( receiver, elemDamageList[ 1 ], csdefine.DAMAGE_TYPE_ELEM_XUAN )
			if elemDamageList[ 2 ] > 0:
				elemDamageList[ 2 ] = caster.calcShieldSuck( receiver, elemDamageList[ 2 ], csdefine.DAMAGE_TYPE_ELEM_LEI )
			if elemDamageList[ 3 ] > 0:
				elemDamageList[ 3 ] = caster.calcShieldSuck( receiver, elemDamageList[ 3 ], csdefine.DAMAGE_TYPE_ELEM_BING )
		else:
			newdamage = attackDamage

		return newdamage

	def calcTwoSecondRule( self, source, skillDamageExtra ):
		"""
		virtual method.
		������2�������� (������ buff or spell)
		"""
		pass # ���������Ļ���ģ��ȥʵ��

	def calcBuff15SecondRule( self, damage ):
		"""
		virtual method.
		buff��15�������� (������ buff)
		@param damage: ��ɫ�Ĺ����� �����������
		"""
		pass # ���������Ļ���ģ��ȥʵ��

	def initMagicDotDamage( self, caster, receiver, damage ):
		"""
		virtual method.
		��ʼ��dotЧ������������(�˺�)����ֵ  ��ͨ������BUFF������ֵ�ļ��㣩
		һ��Ӧ����BUFF����˺���  ��doLoop��ʱ����Ҫ��������ֵ�� ��Ҫ�ǹ����п��ܻᱻ��������
		@param receiver	:	��������
		@type  receiver	:	entity
		@param damage	: 	BUFF��������ֵ
		@return type	:	��������˺�
		"""
		extra = self.calcTwoSecondRule( caster, caster.magic_damage ) #����2�����Ĺ�����ֵ�ֳ�
		damage = self.calcProperty( damage, self.calcBuff15SecondRule( extra ),( caster.magic_skill_extra_percent + receiver.receive_magic_damage_percent )/ csconst.FLOAT_ZIP_PERCENT, caster.magic_skill_extra_value + receiver.receive_magic_damage_value)
		if self._loopSpeed > 0:
			damage /= int( self._persistent / self._loopSpeed )

		# ��Ϊ�������֮���������ܻ�ο��˴ε�������������˺����Դ˽ӿڲ��ܷŵ�receiveDamage��
		damage = caster.calcMagicDamageScissor( receiver, damage )
		if damage < 0:
			damage = 0 # ��ֹ�������ؼ����˺���ɸ���
		return damage

	def initPhysicsDotDamage( self, caster, receiver, damage ):
		"""
		virtual method.
		��ʼ��dotЧ����������(�˺�)����ֵ  ��ͨ������BUFF������ֵ�ļ��㣩
		һ��Ӧ����BUFF����˺���  ��doLoop��ʱ����Ҫ��������ֵ�� ��Ҫ�ǹ����п��ܻᱻ��������
		@param receiver: ��������
		@type  receiver: entity
		@param damage: BUFF��������ֵ
		@return type:��������˺�
		"""
		extra = ( caster.damage_min + caster.damage_max ) / 2
		damage = self.calcProperty( damage, self.calcBuff15SecondRule( extra ), ( caster.skill_extra_percent + receiver.receive_damage_percent )/ csconst.FLOAT_ZIP_PERCENT, caster.skill_extra_value + receiver.receive_damage_value )
		if self._loopSpeed > 0:
			damage /= int( self._persistent / self._loopSpeed )

		# ��Ϊ�������֮���������ܻ�ο��˴ε�������������˺����Դ˽ӿڲ��ܷŵ�receiveDamage��
		damage = caster.calcDamageScissor( receiver, damage )
		if damage < 0:
			damage = 0 # ��ֹ�������ؼ����˺���ɸ���
		return damage

	def calcDotDamage( self, caster, receiver, damageType, damage ):
		"""
		virtual method.
		����dotЧ����������(�˺�)����ֵ  ��ͨ������BUFF������ֵ�ļ��㣩
		@param receiver: ��������
		@type  receiver: entity
		@param damage: BUFF��������ֵ
		@return type:��������˺�
		"""
		new_damage = caster.calcShieldSuck( receiver, damage, damageType )
		damageSuck = damage - new_damage

		if damageSuck > 0:
			SkillMessage.spell_DamageSuck( caster, receiver, damageSuck )
		else:
			if new_damage < 0:
				new_damage = 0
		return int( new_damage )

