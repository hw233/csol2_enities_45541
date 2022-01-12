# -*- coding: gb18030 -*-

"""
��ս����λ

$Id: CombatUnit.py,v 1.76 2008-09-04 07:44:14 kebiao Exp $
"""

import sys
import BigWorld
from bwdebug import *
import csdefine
import csstatus
import Const
import ECBExtend
from State import State
from SpellUnit import SpellUnit
from EntityRelationTable import EntityRelationTable
import csconst
import math
import random
import Language
import CombatUnitConfig
import ShareTexts as ST
from RelationStaticModeMgr import RelationStaticModeMgr
import RelationDynamicObjImpl

g_relationStaticMgr = RelationStaticModeMgr.instance()


# ע�����ڲ߻�����δָ������������ͣ�սʿ�����͵ȣ���������Щ�㷨����ʹ�ã�
#     ��˴˴����㷨ΪĬ���㷨����������̳���ӿ���д�㷨

def calcProperty( baseVal, extraVal, percentVal, value ):
	"""
	�������������ܹ�ʽ
	����ֵ=������ֵ+����ֵ��*��1+�ӳɣ�+��ֵ
	result = ( corporeity_base + corporeity_extra ) * ( 1 + corporeity_percent ) + corporeity_value
	( 100 + 0 ) * (1 + 0.0 ) + 0 = 100
	( 100 + 0 ) * (1 + 0.1 ) + 0 = 110

	@param baseVal: ����ֵ
	@param extraVal: ����ֵ
	@param percentVal: �ӳ�
	@param value: ��ֵ
	"""
	return ( baseVal + extraVal ) * ( 1 + percentVal ) + value

class CombatUnit( State, SpellUnit, EntityRelationTable ):
	"""
	"""
	def __init__( self ):
		"""
		"""
		State.__init__( self )
		SpellUnit.__init__( self )
		EntityRelationTable.__init__( self )

		self.friendlyCamps = [ self.getCamp() ]	#Ĭ��Ϊ�Լ�����Ӫ
		if Language.LANG == Language.LANG_GBK:
			self.double_hit_multiple_base = 20000
			self.magic_double_hit_multiple_base = 20000

	def initAvatar( self ):
		"""
		virtual method = 0.
		��ʼ��avatar�����Ǻ͹���(��NPC)���ܻ��в�ͬ�ĳ�ʼ����ʽ
		"""
		pass

	def calcDynamicProperties( self ):
		"""
		���¼������е�����
		"""
		#�����ȳ�ʼ���Ĳ���
		self.calcStrength()							# ����
		self.calcDexterity()						# ����
		self.calcIntellect()						# ����
		self.calcCorporeity()						# ����
		self.calcPhysicsDPS()						# ���� DPS
		self.calcWaveDPS()							# dps ����

		self.calcHPMax()							# HP ���ֵ
		self.calcMPMax()							# MP ���ֵ
		self.calcHPCureSpeed()						# HP �����ٶ�
		self.calcMPCureSpeed()						# MP �����ٶ�
		self.calcDoubleHitProbability()				# ��������
		self.calcMagicDoubleHitProbability()		# ����������
		self.calcResistHitProbability()				# �����м���
		self.calcDodgeProbability()					# ����������
		self.calcReduceRoleDamage()                           #�����˺�����
		self.calcAddRoleDamage()                           #�Ƶ�
		self.calcArmor()							# �������
		self.calcMagicArmor()						# ��������
		self.calcMoveSpeed()						# �ƶ��ٶ�
		self.calcHitSpeed()							# �����ٶ�
		self.calcRange()							# ��������
		self.calcDamageDerate()						# �����˺�����
		self.calcMagicDamageDerate()				# �����˺�����
		self.calcDamageDerateRatio()				# �����˺�������
		self.calcMagicDamageDerateRatio()			# �����˺�������
		self.calcHitProbability()					# ����������
		self.calcMagicHitProbability()				# ����������
		self.calcResistYuanli()						# ����Ԫ��
		self.calcResistLingli()						# ��������
		self.calcResistTipo()						# ��������
		self.calcResistGiddyProbability()			# �ֿ�ѣ�μ���
		self.calcResistFixProbability()				# �ֿ�������
		self.calcResistChenmoProbability()			# �ֿ���Ĭ����
		self.calcResistSleepProbability()			# �ֿ�˯�߼���
		self.calcDoubleHitMultiple()				# ����������
		self.calcMagicDoubleHitMultiple()			# ������������
		self.calcResistHitDerate()					# �мܼ���

		#��Ҫ���ʼ��
		self.calcDamageMin()						# ��С��������
		self.calcDamageMax()						# �����������
		self.calcMagicDamage()						# ����������

		# ����Ԫ������
		# self.initElemProperty()						# ���ȳ�ʼ��Ԫ��
		self.calcElemHuoDamage()					# �����Ԫ���˺�
		self.calcElemXuanDamage()					# ������Ԫ���˺�
		self.calcElemLeiDamage()					# ������Ԫ���˺�
		self.calcElemBingDamage()					# �����Ԫ���˺�

		self.calcElemHuoDeepRatio()					# �����Ԫ���˺�������
		self.calcElemXuanDeepRatio()				# ������Ԫ���˺�������
		self.calcElemLeiDeepRatio()					# ������Ԫ���˺�������
		self.calcElemBingDeepRatio()				# �����Ԫ���˺�������

		self.calcElemHuoDerateRatio()				# �����Ԫ�ؿ���
		self.calcElemXuanDerateRatio()				# ������Ԫ�ؿ���
		self.calcElemLeiDerateRatio()				# ������Ԫ�ؿ���
		self.calcElemBingDerateRatio()				# �����Ԫ�ؿ���

	def getClass( self ):
		"""
		ȡ������ְҵ
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_CLASS

	def calcStrengthBase( self ):
		"""
		������������ֵ
		"""
		pass

	def calcStrength( self ):
		"""
		��������
		"""
		self.calcStrengthBase()
		strength = calcProperty( self.strength_base, \
								self.strength_extra, \
								self.strength_percent / csconst.FLOAT_ZIP_PERCENT, \
								self.strength_value )
		if strength < 0:strength = 0
		if self.strength != strength: self.strength = strength

	def calcDexterityBase( self ):
		"""
		�������ݻ���ֵ
		"""
		pass

	def calcDexterity( self ):
		"""
		��������
		"""
		self.calcDexterityBase()
		dexterity = calcProperty( self.dexterity_base, \
								self.dexterity_extra, \
								self.dexterity_percent / csconst.FLOAT_ZIP_PERCENT, \
								self.dexterity_value )
		if dexterity < 0:dexterity = 0
		if self.dexterity != dexterity: self.dexterity = dexterity

	def calcIntellectBase( self ):
		"""
		������������ֵ
		"""
		pass

	def calcIntellect( self ):
		"""
		��������
		"""
		self.calcIntellectBase()
		intellect = calcProperty( self.intellect_base,
									self.intellect_extra, \
									self.intellect_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.intellect_value )
		if intellect < 0:intellect = 0
		if self.intellect != intellect: self.intellect = intellect

	def calcCorporeityBase( self ):
		"""
		�������ʻ���ֵ
		"""
		pass

	def calcCorporeity( self ):
		"""
		��������
		"""
		self.calcCorporeityBase()
		corporeity = calcProperty( self.corporeity_base, \
									self.corporeity_extra, \
									self.corporeity_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.corporeity_value )
		if corporeity < 0:corporeity = 0
		if self.corporeity != corporeity: self.corporeity = corporeity

	def calcPhysicsDPSBase( self ):
		"""
		��������DPS_baseֵ
		"""
		self.physics_dps_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcPhysicsDPS( self ) * csconst.FLOAT_ZIP_PERCENT )

	def calcPhysicsDPS( self ):
		"""
		��������DPS
		"""
		self.calcPhysicsDPSBase()
		physics_dps = calcProperty( self.physics_dps_base / csconst.FLOAT_ZIP_PERCENT, \
									self.physics_dps_extra / csconst.FLOAT_ZIP_PERCENT, \
									self.physics_dps_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.physics_dps_value / csconst.FLOAT_ZIP_PERCENT )
		if physics_dps < 0:physics_dps = 0.0
		if self.physics_dps != physics_dps: self.physics_dps = physics_dps

	def calcWaveDPS( self ):
		"""
		����DPS����
		"""
		self.wave_dps = calcProperty( self.wave_dps_base / csconst.FLOAT_ZIP_PERCENT, \
									self.wave_dps_extra / csconst.FLOAT_ZIP_PERCENT, \
									self.wave_dps_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.wave_dps_value / csconst.FLOAT_ZIP_PERCENT )

	def calcHPMaxBase( self ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		self.HP_Max_base = self.corporeity * 10

	def calcHPMax( self ):
		"""
		real entity method.
		virtual method
		��������ֵ
		"""
		if self.queryTemp( "SAME_TYPE_BUFF_REPLACE", False ): return
		if self.queryTemp( "SAME_TYPE_SKILL_REPLACE", False ): return
		self.calcHPMaxBase()
		HP_Max = int( calcProperty( self.HP_Max_base, \
									self.HP_Max_extra, \
									self.HP_Max_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.HP_Max_value ) )

		if self.HP_Max != HP_Max:
			self.HP_Max = HP_Max
			if self.HP > HP_Max:
				self.HP = HP_Max

	def calcMPMaxBase( self ):
		"""
		real entity method.
		virtual method
		��������ֵ����ֵ
		"""
		self.MP_Max_base = self.intellect * 10

	def calcMPMax( self ):
		"""
		real entity method.
		virtual method
		��������ֵ
		"""
		if self.queryTemp( "SAME_TYPE_BUFF_REPLACE", False ): return
		if self.queryTemp( "SAME_TYPE_SKILL_REPLACE", False ): return
		self.calcMPMaxBase()
		MP_Max = int( calcProperty( self.MP_Max_base, \
									self.MP_Max_extra, \
									self.MP_Max_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.MP_Max_value ) )

		if self.MP_Max != MP_Max:
			self.MP_Max = MP_Max
			if self.MP > MP_Max:
				self.MP = MP_Max

	def calcHPCureSpeed( self ):
		"""
		���������ָ��ٶ�
		��ɫ���������ԣ�������ɫÿ3����Իָ���������ֵ��ս��ʱ��Ч����ֵ����
		"""
		self.HP_regen = int( calcProperty( self.HP_regen_base, \
										self.HP_regen_extra, \
										self.HP_regen_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.HP_regen_value ) )

	def calcMPCureSpeed( self ):
		"""
		��ɫ���������ԣ�������ɫÿ3����Իָ��ķ�����ֵ��ս��ʱ��Ч����ֵ����
		"""
		self.MP_regen = int( calcProperty( self.MP_regen_base, \
										self.MP_regen_extra, \
										self.MP_regen_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.MP_regen_value ) )

	def calcMagicDamageBase( self ):
		"""
		virtual method
		����������
		"""
		self.magic_damage_base = int( self.intellect * 0.14 ) #�����������������ܹ�ʽ�еĻ���ֵ��=����*0.14

	def calcMagicDamage( self ):
		"""
		virtual method
		����������
		"""
		self.calcMagicDamageBase()
		magic_damage = math.ceil( calcProperty( self.magic_damage_base, \
											self.magic_damage_extra, \
											self.magic_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
											self.magic_damage_value ) )
		if magic_damage < 0:magic_damage = 0.0
		if self.magic_damage != magic_damage: self.magic_damage = magic_damage

	def calcDamageMinBase( self ):
		"""
		������С�������� ����ֵ
		"""
		self.damage_min_base = int( self.physics_dps * self.hit_speed * ( 1.0 - self.wave_dps ) )

	def calcDamageMin( self ):
		"""
		������С��������
		"""
		self.calcDamageMinBase()
		damage_min = calcProperty( self.damage_min_base, \
									self.damage_min_extra, \
									self.damage_min_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.damage_min_value )
		if damage_min < 0:damage_min = 0
		if self.damage_min != damage_min: self.damage_min = damage_min

	def calcDamageMaxBase( self ):
		"""
		��������������� ����ֵ
		"""
		self.damage_max_base = int( self.physics_dps * self.hit_speed * ( 1.0 + self.wave_dps ) )

	def calcDamageMax( self ):
		"""
		���������������
		"""
		self.calcDamageMaxBase()
		damage_max = calcProperty( self.damage_max_base, \
									self.damage_max_extra, \
									self.damage_max_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.damage_max_value )
		if damage_max < 0:damage_max = 0
		if self.damage_max != damage_max: self.damage_max = damage_max

	def calcDoubleHitProbabilityBase( self ):
		"""
		��������
		"""
		self.double_hit_probability_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcBaseDoubleHitProbability( self ) * csconst.FLOAT_ZIP_PERCENT )

	def calcDoubleHitProbability( self ):
		"""
		��������
		"""
		self.calcDoubleHitProbabilityBase()
		double_hit_probability = max( calcProperty( self.double_hit_probability_base / csconst.FLOAT_ZIP_PERCENT, \
													self.double_hit_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
													self.double_hit_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.double_hit_probability_value / csconst.FLOAT_ZIP_PERCENT ), 0.0 )
		if self.double_hit_probability != double_hit_probability: self.double_hit_probability = double_hit_probability

	def calcMagicDoubleHitProbabilityBase( self ):
		"""
		����������
		"""
		self.magic_double_hit_probability_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcMagicBaseDoubleHitProbability( self ) * csconst.FLOAT_ZIP_PERCENT )

	def calcMagicDoubleHitProbability( self ):
		"""
		����������
		"""
		self.calcMagicDoubleHitProbabilityBase()
		magic_double_hit_probability = max( calcProperty( self.magic_double_hit_probability_base / csconst.FLOAT_ZIP_PERCENT, \
														self.magic_double_hit_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
														self.magic_double_hit_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
														self.magic_double_hit_probability_value / csconst.FLOAT_ZIP_PERCENT ), 0.0 )
		if self.magic_double_hit_probability != magic_double_hit_probability: self.magic_double_hit_probability = magic_double_hit_probability

	def calcResistHitProbabilityBase( self ):
		"""
		�м���
		�м�����ָ�мܷ����ļ��ʣ���ͨ�������������ܹ��������ܹ����мܡ����Ƿ������������ܱ��мܡ��мܳɹ��󣬽�ɫ�ܵ����˺�����50%
		"""
		self.resist_hit_probability_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcBaseResistHitProbability( self ) * csconst.FLOAT_ZIP_PERCENT )

	def calcResistHitProbability( self ):
		"""
		�м���
		�м�����ָ�мܷ����ļ��ʣ���ͨ�������������ܹ��������ܹ����мܡ����Ƿ������������ܱ��мܡ��мܳɹ��󣬽�ɫ�ܵ����˺�����50%
		"""
		self.calcResistHitProbabilityBase()
		resist_hit_probability = calcProperty( self.resist_hit_probability_base / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_hit_probability != resist_hit_probability: self.resist_hit_probability = resist_hit_probability

	def calcDodgeProbabilityBase( self ):
		"""
		������ ����ֵ
		��ɫ����Է������ļ��ʡ���ͨ���������Ա����ܡ������ܹ����ͷ������ܹ������ܱ����ܡ����ܳɹ��󣬱����������ι��������κ��˺���
		"""
		self.dodge_probability_base = int( CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].calcBaseDodgeProbability( self ) * csconst.FLOAT_ZIP_PERCENT )

	def calcDodgeProbability( self ):
		"""
		������
		��ɫ����Է������ļ��ʡ���ͨ���������Ա����ܡ������ܹ����ͷ������ܹ������ܱ����ܡ����ܳɹ��󣬱����������ι��������κ��˺���
		"""
		self.calcDodgeProbabilityBase()
		dodge_probability = calcProperty( self.dodge_probability_base / csconst.FLOAT_ZIP_PERCENT, \
										self.dodge_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
										self.dodge_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.dodge_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.dodge_probability != dodge_probability: self.dodge_probability = dodge_probability

	def calcReduceRoleDamageBase( self ):
		"""
		���� ����ֵ
		�ܵ�������ҵ��˺����٣�����ֵ����ʱ����
		"""
		self.reduce_role_damage_base = 0

	def calcReduceRoleDamage( self ):
		"""
		�����˺�������
		"""
		self.calcReduceRoleDamageBase()
		reduce_role_damage = calcProperty( self.reduce_role_damage_base / csconst.FLOAT_ZIP_PERCENT, \
										self.reduce_role_damage_extra / csconst.FLOAT_ZIP_PERCENT, \
										self.reduce_role_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.reduce_role_damage_value / csconst.FLOAT_ZIP_PERCENT )
		if self.reduce_role_damage != reduce_role_damage: self.reduce_role_damage = reduce_role_damage
		
	def calcAddRoleDamageBase( self ):
		"""
		�Ƶ� ����ֵ
		���Ӷ���ҵ��˺�������ֵ����ʱ����
		"""
		self.add_role_damage_base = 0

	def calcAddRoleDamage( self ):
		"""
		�Ƶ�--������˺�������
		"""
		self.calcAddRoleDamageBase()
		add_role_damage = calcProperty( self.add_role_damage_base / csconst.FLOAT_ZIP_PERCENT, \
										self.add_role_damage_extra / csconst.FLOAT_ZIP_PERCENT, \
										self.add_role_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.add_role_damage_value / csconst.FLOAT_ZIP_PERCENT )
		if self.add_role_damage != add_role_damage: self.add_role_damage = add_role_damage	

	def calcArmorBase( self ):
		"""
		virtual method
		�������ֵ	��ʾ����ɫ�ܵ�������ʱ���ܶԴ�������������������������
		"""
		pass

	def calcArmor( self ):
		"""
		virtual method
		�������ֵ	��ʾ����ɫ�ܵ�������ʱ���ܶԴ�������������������������
		"""
		self.calcArmorBase()
		armor = max( int( math.ceil( calcProperty( self.armor_base, \
													self.armor_extra, \
													self.armor_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.armor_value ) ) ), 0 )
		if self.armor != armor: self.armor = armor

	def calcMagicArmorBase( self ):
		"""
		virtual method
		��������ֵ	��ʾ����ɫ�ܵ���������ʱ���ܶԴ˷�������������������������
		"""
		pass

	def calcMagicArmor( self ):
		"""
		virtual method
		��������ֵ	��ʾ����ɫ�ܵ���������ʱ���ܶԴ˷�������������������������
		"""
		self.calcMagicArmorBase()
		magic_armor = max( int( math.ceil( calcProperty( self.magic_armor_base, \
															self.magic_armor_extra, \
															self.magic_armor_percent / csconst.FLOAT_ZIP_PERCENT, \
															self.magic_armor_value ) ) ), 0)
		if self.magic_armor != magic_armor: self.magic_armor = magic_armor

	def calcMoveSpeed( self ):
		"""
		virtual method.
		�ƶ��ٶ� = �ƶ��ٶȻ���ֵ + �ƶ��ٶȼ�ֵ
		npc�ƶ��ٶȣ��ܹ�ʽ�еĻ���ֵ��=4.5m/s
		"""
		if self.hasFlag( csdefine.ROLE_FLAG_FLY_TELEPORT ) and self.isEntityType( csdefine.ENTITY_TYPE_ROLE ):return #���ڷ��д���״̬����Ӧ�ٶ�ֵ�޸�
		move_speed = calcProperty( self.move_speed_base / csconst.FLOAT_ZIP_PERCENT, \
									self.move_speed_extra / csconst.FLOAT_ZIP_PERCENT, \
									self.move_speed_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.move_speed_value / csconst.FLOAT_ZIP_PERCENT )
		if self.move_speed != move_speed:
			if move_speed < 0:
				move_speed = 0.01
			self.setMoveSpeed( move_speed )

	def calcHitSpeedBase( self ):
		"""
		�����ٶ�
		"""
		pass

	def calcHitSpeed( self ):
		"""
		�����ٶ�
		"""
		# hit_speed���Ϊ�����ӳ�, ��λ: ��
		self.calcHitSpeedBase()
		hit_speed = calcProperty( self.hit_speed_base / csconst.FLOAT_ZIP_PERCENT, \
									self.hit_speed_extra / csconst.FLOAT_ZIP_PERCENT, \
									self.hit_speed_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.hit_speed_value / csconst.FLOAT_ZIP_PERCENT )
		if self.hit_speed != hit_speed: self.hit_speed = hit_speed

	def calcRange( self ):
		"""
		virtual method.
		���㹥������
		"""
		range = calcProperty( self.range_base / csconst.FLOAT_ZIP_PERCENT, \
								self.range_extra / csconst.FLOAT_ZIP_PERCENT, \
								self.range_percent / csconst.FLOAT_ZIP_PERCENT, \
								self.range_value / csconst.FLOAT_ZIP_PERCENT )
		if self.range != range: self.range = range

	def calcDamageDerate( self ):
		"""
		���������˺�����ֵ
		"""
		self.damage_derate = calcProperty( self.damage_derate_base, \
								self.damage_derate_extra, \
								self.damage_derate_percent / csconst.FLOAT_ZIP_PERCENT, \
								self.damage_derate_value )

	def calcMagicDamageDerate( self ):
		"""
		���㷨���˺�����ֵ
		"""
		self.magic_damage_derate = calcProperty( self.magic_damage_derate_base, \
													self.magic_damage_derate_extra, \
													self.magic_damage_derate_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_damage_derate_value )

	def calcDamageDerateRatio( self ):
		"""
		���������˺�������
		"""
		self.damage_derate_ratio = calcProperty( self.damage_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.damage_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.damage_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.damage_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcMagicDamageDerateRatio( self ):
		"""
		���㷨���˺�������
		"""
		self.magic_damage_derate_ratio = calcProperty( self.magic_damage_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_damage_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_damage_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_damage_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcHitProbability( self ):
		"""
		��������������
		���ղ߻�Ҫ�� ��ʾ���ͻ���Ĭ������ʾ���Լ�ͬһ�����Ŀ������ĸ���
		�ο���ʽ�ĵ������������ʼ��㣬���£�
		�������������ʣ��ܹ�ʽ�еĻ���ֵ��=95% -�����������ȼ�-�������ȼ���^1.61*3%
		��������������ȼ�-�������ȼ���<0���򣨱��������ȼ�-�������ȼ���=0���Ϊ0��
		���95% -�����������ȼ�-�������ȼ���^1.61*3%<1%�������ȡ1%��
		������ͨ�����������ܹ���������������������
		�����������÷���������
		"""
		hitProbability = calcProperty( self.hitProbability_base / csconst.FLOAT_ZIP_PERCENT, \
										self.hitProbability_extra / csconst.FLOAT_ZIP_PERCENT, \
										self.hitProbability_percent / csconst.FLOAT_ZIP_PERCENT, \
										self.hitProbability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.hitProbability != hitProbability: self.hitProbability = hitProbability

	def calcMagicHitProbability( self ):
		"""
		���㷨��������
		���ղ߻�Ҫ�� ��ʾ���ͻ���Ĭ������ʾ���Լ�ͬһ�����Ŀ������ĸ���
		�ο���ʽ�ĵ��з��������ʼ��㣬��ʽ���£�
		�������������ʣ��ܹ�ʽ�еĻ���ֵ��=95% -�����������ȼ�-�������ȼ���^1.61*3%
		��������������ȼ�-�������ȼ���<0���򣨱��������ȼ�-�������ȼ���=0���Ϊ0��
		���95% -�����������ȼ�-�������ȼ���^1.61*3%<1%�������ȡ1%��
		"""
		magic_hitProbability = calcProperty( self.magic_hitProbability_base / csconst.FLOAT_ZIP_PERCENT, \
											self.magic_hitProbability_extra / csconst.FLOAT_ZIP_PERCENT, \
											self.magic_hitProbability_percent / csconst.FLOAT_ZIP_PERCENT, \
											self.magic_hitProbability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.magic_hitProbability != magic_hitProbability: self.magic_hitProbability = magic_hitProbability
	
	def calcResistYuanli( self ):
		"""
		����Ԫ��
		"""
		resist_yuanli = calcProperty( self.resist_yuanli_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_yuanli_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_yuanli_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_yuanli_value / csconst.FLOAT_ZIP_PERCENT )
		if resist_yuanli > 100.0:
			resist_yuanli = 100.0
			
		if self.resist_yuanli != resist_yuanli: self.resist_yuanli = resist_yuanli
		
	def calcResistLingli( self ):
		"""
		��������
		"""
		resist_lingli = calcProperty( self.resist_lingli_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_lingli_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_lingli_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_lingli_value / csconst.FLOAT_ZIP_PERCENT )
		if resist_lingli > 100.0:
			resist_lingli = 100.0
			
		if self.resist_lingli != resist_lingli: self.resist_lingli = resist_lingli
		
	def calcResistTipo( self ):
		"""
		��������
		"""
		resist_tipo = calcProperty( self.resist_tipo_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_tipo_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_tipo_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_tipo_value / csconst.FLOAT_ZIP_PERCENT )
		if resist_tipo > 100.0:
			resist_tipo = 100.0
			
		if self.resist_tipo != resist_tipo: self.resist_tipo = resist_tipo

	def calcResistGiddyProbability( self ):
		"""
		����ֿ�ѣ�μ���
		"""
		resist_giddy_probability = calcProperty( self.resist_giddy_probability_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_giddy_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_giddy_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_giddy_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_giddy_probability != resist_giddy_probability: self.resist_giddy_probability = resist_giddy_probability

	def calcResistFixProbability( self ):
		"""
		����ֿ�������
		"""
		resist_fix_probability = calcProperty( self.resist_fix_probability_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_fix_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_fix_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_fix_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_fix_probability != resist_fix_probability: self.resist_fix_probability = resist_fix_probability

	def calcResistChenmoProbability( self ):
		"""
		����ֿ���Ĭ����
		"""
		resist_chenmo_probability = calcProperty( self.resist_chenmo_probability_base / csconst.FLOAT_ZIP_PERCENT, \
													self.resist_chenmo_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
													self.resist_chenmo_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.resist_chenmo_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_chenmo_probability != resist_chenmo_probability: self.resist_chenmo_probability = resist_chenmo_probability

	def calcResistSleepProbability( self ):
		"""
		����ֿ�˯�߼���
		"""
		resist_sleep_probability = calcProperty( self.resist_sleep_probability_base / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_sleep_probability_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_sleep_probability_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.resist_sleep_probability_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_sleep_probability != resist_sleep_probability: self.resist_sleep_probability = resist_sleep_probability

	def calcDoubleHitMultiple( self ):
		"""
		��������������
		"""
		self.double_hit_multiple = calcProperty( self.double_hit_multiple_base / csconst.FLOAT_ZIP_PERCENT, \
												self.double_hit_multiple_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.double_hit_multiple_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.double_hit_multiple_value / csconst.FLOAT_ZIP_PERCENT )

	def calcMagicDoubleHitMultiple( self ):
		"""
		���㷨����������
		"""
		self.magic_double_hit_multiple = calcProperty( self.magic_double_hit_multiple_base / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_double_hit_multiple_extra / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_double_hit_multiple_percent / csconst.FLOAT_ZIP_PERCENT, \
													self.magic_double_hit_multiple_value / csconst.FLOAT_ZIP_PERCENT )

	def calcResistHitDerate( self ):
		"""
		�����мܼ���
		"""
		self.resist_hit_derate = calcProperty( self.resist_hit_derate_base / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_derate_extra / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_derate_percent / csconst.FLOAT_ZIP_PERCENT, \
											self.resist_hit_derate_value / csconst.FLOAT_ZIP_PERCENT )
		if self.resist_hit_derate > 10000:
			self.resist_hit_derate = 10000

	# ----------------------------------------------------------------------------------------------------
	# Ԫ�����
	# ----------------------------------------------------------------------------------------------------
	def initElemProperty( self ):
		"""
		virtual method.
		��ʼ������Ԫ�����Եĳ�ʼֵ
		"""
		CombatUnitConfig.ENTITY_COMBAT_BASE_EXPRESSION[self.getClass()].initElemProperty( self )

	def calcElemHuoDamage( self ):
		"""
		�����Ԫ���˺�
		"""
		elem_huo_damage = calcProperty( self.elem_huo_damage_base, \
									self.elem_huo_damage_extra, \
									self.elem_huo_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.elem_huo_damage_value )
		if elem_huo_damage < 0:elem_huo_damage = 0
		if self.elem_huo_damage != elem_huo_damage: self.elem_huo_damage = elem_huo_damage

	def calcElemXuanDamage( self ):
		"""
		������Ԫ���˺�
		"""
		elem_xuan_damage = calcProperty( self.elem_xuan_damage_base, \
									self.elem_xuan_damage_extra, \
									self.elem_xuan_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.elem_xuan_damage_value )
		if elem_xuan_damage < 0:elem_xuan_damage = 0
		if self.elem_xuan_damage != elem_xuan_damage: self.elem_xuan_damage = elem_xuan_damage

	def calcElemLeiDamage( self ):
		"""
		������Ԫ���˺�
		"""
		elem_lei_damage = calcProperty( self.elem_lei_damage_base, \
									self.elem_lei_damage_extra, \
									self.elem_lei_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.elem_lei_damage_value )
		if elem_lei_damage < 0:elem_lei_damage = 0
		if self.elem_lei_damage != elem_lei_damage: self.elem_lei_damage = elem_lei_damage

	def calcElemBingDamage( self ):
		"""
		�����Ԫ���˺�
		"""
		elem_bing_damage = calcProperty( self.elem_bing_damage_base, \
									self.elem_bing_damage_extra, \
									self.elem_bing_damage_percent / csconst.FLOAT_ZIP_PERCENT, \
									self.elem_bing_damage_value )
		if elem_bing_damage < 0:elem_bing_damage = 0
		if self.elem_bing_damage != elem_bing_damage: self.elem_bing_damage = elem_bing_damage

	def calcElemHuoDeepRatio( self ):
		"""
		��Ԫ���˺�������
		"""
		self.elem_huo_deep_ratio = calcProperty( self.elem_huo_deep_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_deep_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_deep_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_deep_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcElemXuanDeepRatio( self ):
		"""
		��Ԫ���˺�������
		"""
		self.elem_xuan_deep_ratio = calcProperty( self.elem_xuan_deep_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_deep_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_deep_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_deep_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcElemLeiDeepRatio( self ):
		"""
		��Ԫ���˺�������
		"""
		self.elem_lei_deep_ratio = calcProperty( self.elem_lei_deep_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_deep_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_deep_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_deep_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcElemBingDeepRatio( self ):
		"""
		��Ԫ���˺�������
		"""
		self.elem_bing_deep_ratio = calcProperty( self.elem_bing_deep_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_deep_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_deep_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_deep_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT

	def calcElemHuoDerateRatio( self ):
		"""
		�����Ԫ�ؿ���
		"""
		self.elem_huo_derate_ratio = max(0, min( 10000, calcProperty( self.elem_huo_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_huo_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemXuanDerateRatio( self ):
		"""
		������Ԫ�ؿ���
		"""
		self.elem_xuan_derate_ratio = max(0, min( 10000, calcProperty( self.elem_xuan_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_xuan_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemLeiDerateRatio( self ):
		"""
		������Ԫ�ؿ���
		"""
		self.elem_lei_derate_ratio = max(0, min( 10000, calcProperty( self.elem_lei_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_lei_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	def calcElemBingDerateRatio( self ):
		"""
		�����Ԫ�ؿ���
		"""
		self.elem_bing_derate_ratio = max(0, min( 10000, calcProperty( self.elem_bing_derate_ratio_base / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_extra / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_percent / csconst.FLOAT_ZIP_PERCENT, \
												self.elem_bing_derate_ratio_value / csconst.FLOAT_ZIP_PERCENT ) * csconst.FLOAT_ZIP_PERCENT ) )

	# ---------------------------------------
	def affectPropValue( self, propName, delta, calcMethodName ) :
		"""
		defined method
		Ӱ���������ֵ�����ڸ����� Entity ��ҪӰ����������ֵʱ���ã�Ʃ����輼��Ӱ���ɫ���ԣ��������Եȣ�
		hyw--2009.08.07
		@type			propName		: str
		@param			propName		: ҪӲ�Ե�������
		@type			delta			: INT32
		@param			delta			: Ӱ�������ֵ(���ﶨΪ 32 λ��������⣬ǰ���ǣ�Ӱ�������ֵ���ᳬ�� 2^32 - 1)
		@type			calcMethodName  : str
		@param			calcMethodName  : �������㣨����Ϊ���ַ�����Ϊ�մ�ʱ���������¼������ԣ�
		"""
		if not hasattr( self, propName ): return
		value = getattr( self, propName )
		setattr( self, propName, value + delta )
		if calcMethodName != "" :
			getattr( self, calcMethodName )()

	# ----------------------------------------------------------------
	def setHitDelay( self ):
		"""
		�������ù����ӳ�
		"""
		hitDelay = BigWorld.time() + self.hit_speed
		if self.hitDelay != hitDelay: self.hitDelay = hitDelay

	def hitDelayOver( self ):
		"""
		�жϹ����ӳ��Ƿ����

		@return: BOOL
		"""
		return BigWorld.time() >= self.hitDelay

	def updateTopSpeed( self ):
		"""
		virtual method = 0.

		�����ƶ��ٶ�����(topSpeed)
		"""
		pass

	def setMoveSpeed( self, speed ):
		"""
		virtual method.
		�����ƶ��ٶ�
		"""
		self.move_speed = speed
		self.updateTopSpeed()

	def receiveDamage( self, casterID, skillID, damageType, damage ):
		"""
		Define and virtual method.
		�����˺���

		@param   casterID: ʩ����ID
		@type    casterID: OBJECT_ID
		@param    skillID: ����ID
		@type     skillID: INT
		@param damageType: �˺����ͣ�see also csdefine.py/DAMAGE_TYPE_*
		@type  damageType: UINT8
		@param     damage: �˺���ֵ
		@type      damage: INT
		"""
		if self.state == csdefine.ENTITY_STATE_DEAD:
			return

		self.setHP( self.HP - damage )
		# �ܵ��˺�ʱ �׳�buff�ж��룬 �����������ܵ��˺���������buff����ȥ��
		self.clearBuff( [csdefine.BUFF_INTERRUPT_GET_HIT] )
		
		if self.HP == 0:
			self.setMP( 0 )
			self.die( casterID )
			if self.spawnMB:
				# ��spawnMB�Ĺ�����Ҫ֪ͨ���ĳ����㣬(����)���¸���
				if BigWorld.entities.has_key( self.spawnMB.id ):
					BigWorld.entities[self.spawnMB.id].entityDead()
				else:
					self.spawnMB.cell.entityDead()			

	def setHP( self, value ):
		"""
		real entity method.
		virtual method
		����HP
		"""
		if value < 0:
			value = 0
		elif value > self.HP_Max:
			value = self.HP_Max

		self.HP = value
		self.onHPChanged()

	def onHPChanged( self ):
		"""
		HP���ı�ص�
		"""
		pass

	def addHP( self, value ):
		"""
		real entity method.
		virtual method
		����HP
		"""
		m_preHp = self.HP
		self.setHP( self.HP + value )
		m_addHp = self.HP - m_preHp

		return m_addHp

	def setMP( self, value ):
		"""
		real entity method.
		virtual method
		����MP
		"""
		if value < 0:
			value = 0
		elif value > self.MP_Max:
			value = self.MP_Max

		self.MP = value
		self.onMPChanged()

	def onMPChanged( self ):
		"""
		MP���ı�ص�
		"""
		pass

	def addMP( self, value ):
		"""
		real entity method.
		virtual method
		����MP
		"""
		m_preMp = self.MP
		self.setMP( self.MP + value )
		m_addMp = self.MP - m_preMp

		return m_addMp

	def full( self ):
		"""
		����HP��MP��
		"""
		self.setHP( self.HP_Max )
		self.setMP( self.MP_Max )

	def beforeDie( self, killerID ):
		"""
		virtual method.

		����ͨ���� killer����Ϊ��
		"""
		return True

	def onDie( self, killerID ):
		"""
		virtual method.

		����ʱ�ص���ִ��һЩ����������һ�̱����������顣
		"""
		pass

	def afterDie( self, killerID ):
		"""
		virtual method.

		������ص���ִ��һЩ�����ڹ�����������������顣
		"""
		return

	def die( self, killerID ):
		"""
		virtual method.

		����������
		"""
		# ����ǰ���ж�
		
		if self.queryTemp( "inDie", False ):
			return
		self.setTemp("inDie", True )
		
		try:
			if not self.beforeDie( killerID ):
				return
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			self.onDie( killerID )
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			self.clearBuff( [csdefine.BUFF_INTERRUPT_ON_DIE] )					# �������buff
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			self.changeState( csdefine.ENTITY_STATE_DEAD )
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			killer = BigWorld.entities[ killerID ]
		except KeyError:
			if killerID != 0:
				WARNING_MSG( "killer %i not found." % killerID )
			self.afterDie( killerID )
			self.removeTemp( "inDie" )
			return

		try:
			self.resetEnemyList()
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			if killer.isEntityType( csdefine.ENTITY_TYPE_PET ):
				if self.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# ��������������
					killer.remoteCall( "statusMessage", ( csstatus.ROLE_STATE_KILL_DEAD_BY_YOU, self.getName() ) )
				else:
					killer.remoteCall( "statusMessage", ( csstatus.ACCOUNT_STATE_KILL_DEAD_TO, self.getName() ) )

			if killer.isEntityType( csdefine.ENTITY_TYPE_ROLE ):
				roleName = self.getName()
				if killer.onFengQi:
					roleName = ST.CHAT_CHANNEL_MASED
				if killer.isReal():
					if self.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# ��������������
						killer.statusMessage( csstatus.ROLE_STATE_KILL_DEAD_BY_YOU, roleName )
					else:
						killer.statusMessage( csstatus.ACCOUNT_STATE_KILL_DEAD_TO, roleName )
				else:
					if self.isEntityType( csdefine.ENTITY_TYPE_ROLE ):	# ��������������
						killer.remoteCall( "statusMessage", ( csstatus.ROLE_STATE_KILL_DEAD_BY_YOU, roleName ) )
					else:
						killer.remoteCall( "statusMessage", ( csstatus.ACCOUNT_STATE_KILL_DEAD_TO, roleName ) )

				if killer.teamMailbox is not None:
					killer.team_notifyKillMessage( self )
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		try:
			# ��������Щ����
			self.afterDie( killerID )
		except:
			EXCEHOOK_MSG("CombatUnit die wrong")

		self.removeTemp( "inDie" )

	def isDead( self ):
		"""
		virtual method.

		@return: BOOL�������Լ��Ƿ��Ѿ��������ж�
		@rtype:  BOOL
		"""
		# ��Ȼ��һ�������������ӿ�����Ҫ��
		return self.state == csdefine.ENTITY_STATE_DEAD

	def canFight( self ):
		"""
		virtual method.

		@return: BOOL�������Լ��Ƿ���ս�����ж�
		@rtype:  BOOL
		"""
		return not self.actionSign( csdefine.ACTION_FORBID_FIGHT )

	def equipDamage( self, demageValue ):
		"""
		virtual define method.
		�ܻ���װ��ĥ��
		"""
		pass

	def equipAbrasion( self, demageValue ):
		"""
		virtual define method.
		������װ��ĥ��
		"""
		pass

	def onStateChanged( self, old, new ):
		"""
		virtual method
		״̬�ı�
		"""
		State.onStateChanged( self, old, new )

	def checkViewRange( self, entity ):
		"""
		virtual method
		���entity�Ƿ�����Ұ��Χ
		�ж�entity�Ƿ����Լ�����Ұ��Χ֮��
		return 	:	True	��
		return	:	False	����
		"""
		if entity.spaceID != self.spaceID or entity.position.distTo( self.position ) > self.viewRange:
			return False
		return True

	def queryRelation( self, entity ):
		"""
		virtual method.
		ȡ���Լ���Ŀ��Ĺ�ϵ

		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		if not self.isNeedQueryRelation( entity ):
			return csdefine.RELATION_FRIEND
		else:
			return csdefine.RELATION_NONE

	def queryCampRelation( self, entity ):
		"""
		ȡ���Լ���Ŀ�����Ӫ��ϵ
		@param entity: ����Ŀ��entity
		@return : RELATION_*
		"""
		# �Ѻ���Ӫ�б��ж�
		# ��Ӫ��ͬ������Ӫ��Ŀ����Ѻ���Ӫ�б�,��ʾ�Ѻù�ϵ�������ǵжԹ�ϵ
		sCamp = self.getCamp()
		tCamp = entity.getCamp()
		if ( sCamp == tCamp ) or ( sCamp in entity.friendlyCamps ) or ( tCamp in self.friendlyCamps ):
			return csdefine.RELATION_FRIEND
		else:
			return csdefine.RELATION_ANTAGONIZE

	# ----------------------------------------------------------------
	def appendReceiverMonsterExp( self, skill ):
		"""
		call on real.
		����һ���ڡ����ﱻɱ����þ���ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springReceiveMonsterExpList.append( skill )

	def removeReceiverMonsterExp( self, skillUID ):
		"""
		call on real.
		�Ƴ�һ���ڡ����ﱻɱ����þ���ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springReceiveMonsterExpList ):
			if skill.getUID() == skillUID:
				self.springReceiveMonsterExpList.pop( index )
				return

	def doAddKillMonsterExp( self, exp ):
		"""
		call on real
		����һ��ɱ�־���ʱ����
		"""
		for skill in self.springReceiveMonsterExpList:
			skill.addExpTrigger( self, exp )

	def appendReceiverCure( self, skill ):
		"""
		call on real.
		����һ���ڡ�������ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springReceiverCureList.append( skill )

	def removeReceiverCure( self, skillUID ):
		"""
		call on real.
		����һ���ڡ�������ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springReceiverCureList ):
			if skill.getUID() == skillUID:
				self.springReceiverCureList.pop( index )
				return

	def doReceiverOnCure( self, caster, cureHP ):
		"""
		�ڱ�����ʱ��������˺�����ʱ�˿����Ѿ����ˣ�����������Ҫ����һЩ��Ҫ�ڱ����к��ٴ�����Ч����

		�����ڣ�
		    ������Ŀ��ʱ$1%���ʸ���Ŀ������˺�$2
		    etc.
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			for spell in self.springReceiverCureList:
				spell.springOnCure( caster, self, cureHP )

	def appendCasterCure( self, skill ):
		"""
		call on real.
		����һ���ڡ�����Ŀ��ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springCasterCureList.append( skill )

	def removeCasterCure( self, skillUID ):
		"""
		call on real.
		����һ���ڡ�����Ŀ��ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springCasterCureList ):
			if skill.getUID() == skillUID:
				self.springCasterCureList.pop( index )
				return

	def doCasterOnCure( self, receiver, cureHP ):
		"""
		������Ŀ��ʱ��������˺�����ʱ�˿����Ѿ����ˣ�����������Ҫ����һЩ��Ҫ�����к��ٴ�����Ч����

		�����ڣ�
		    ����Ŀ��ʱ$1%���ʸ���Ŀ������˺�$2
		    ����Ŀ��ʱ$1%����ʹĿ�깥��������$2������$3��
		    ������ʱ$1���ʻָ�$2����
		    ������ʱ$1%�����������$2������$3��
		    etc.
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		for spell in self.springCasterCureList:
			spell.springOnCure( self, receiver, cureHP )

	def appendVictimHit( self, skill ):
		"""
		call on real.
		����һ���ڡ������к󡭡�����������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimHitList.append( skill )

	def removeVictimHit( self, skillUID ):
		"""
		call on real.
		����һ���ڡ������к󡭡�����������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimHitList ):
			if skill.getUID() == skillUID:
				self.springVictimHitList.pop( index )
				return

	def doVictimOnHit( self, caster, damageType ):
		"""
		�ڱ����к󣨼�����˺�����ʱ�˿����Ѿ����ˣ�����������Ҫ����һЩ��Ҫ�ڱ����к��ٴ�����Ч����

		�����ڣ�
		    ������Ŀ��ʱ$1%���ʸ���Ŀ������˺�$2
		    etc.
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			for spell in self.springVictimHitList:
				spell.springOnHit( caster, self, damageType )

	def appendAttackerHit( self, skill ):
		"""
		call on real.
		����һ���ڡ����к󡭡�����������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springAttackerHitList.append( skill )

	def removeAttackerHit( self, skillUID ):
		"""
		call on real.
		����һ���ڡ����к󡭡�����������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerHitList ):
			if skill.getUID() == skillUID:
				self.springAttackerHitList.pop( index )
				return

	def removeAttackerHitByID( self, skillID ):
		"""
		call on real.
		����һ���ڡ����к󡭡�����������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerHitList ):
			if skill.getID() == skillID:
				self.springAttackerHitList.pop( index )
				return

	def doAttackerOnHit( self, receiver, damageType ):
		"""
		�����к󣨼�����˺�����ʱ�˿����Ѿ����ˣ�����������Ҫ����һЩ��Ҫ�����к��ٴ�����Ч����

		�����ڣ�
		    ����Ŀ��ʱ$1%���ʸ���Ŀ������˺�$2
		    ����Ŀ��ʱ$1%����ʹĿ�깥��������$2������$3��
		    ������ʱ$1���ʻָ�$2����
		    ������ʱ$1%�����������$2������$3��
		    etc.
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		for spell in self.springAttackerHitList:
			spell.springOnHit( self, receiver, damageType )

	def onAttackerMiss( self, receiver, damageType ):
		"""
		������δ����
		"""
		pass

	def appendVictimDodge( self, skill ):
		"""
		call on real.
		����һ���ڡ����ܳɹ�ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimDodgeList.append( skill )

	def removeVictimDodge( self, skillUID ):
		"""
		call on real.
		����һ���ڡ����ܳɹ�ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimDodgeList ):
			if skill.getUID() == skillUID:
				self.springVictimDodgeList.pop( index )
				return

	def doVictimOnDodge( self, caster, damageType ):
		"""
		�����ܳɹ�ʱ��������˺�����ʱ�˿����Ѿ����ˣ�������
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			for spell in self.springVictimDodgeList:
				spell.springOnDodge( caster, self, damageType )

	def appendAttackerDodge( self, skill ):
		"""
		call on real.
		����һ���ڡ�Ŀ�����ܳɹ�ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springAttackerDodgeList.append( skill )

	def removeAttackerDodge( self, skillUID ):
		"""
		call on real.
		����һ���ڡ�Ŀ�����ܳɹ�ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerDodgeList ):
			if skill.getUID() == skillUID:
				self.springAttackerDodgeList.pop( index )
				return

	def doAttackerOnDodge( self, receiver, damageType ):
		"""
		��Ŀ�����ܳɹ�ʱ��������˺�����ʱ�˿����Ѿ����ˣ�������
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		for spell in self.springAttackerDodgeList:
			spell.springOnDodge( self, receiver, damageType )

	def appendVictimDoubleHit( self, skill ):
		"""
		call on real.
		����һ���ڡ���������ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimDoubleHitList.append( skill )

	def removeVictimDoubleHit( self, skillUID ):
		"""
		call on real.
		����һ���ڡ���������ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimDoubleHitList ):
			if skill.getUID() == skillUID:
				self.springVictimDoubleHitList.pop( index )
				return

	def doVictimOnDoubleHit( self, caster, damageType ):
		"""
		�ڱ�������ʱ��������˺�����ʱ�˿����Ѿ����ˣ�������
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			for spell in self.springVictimDoubleHitList:
				spell.springOnDoubleHit( caster, self, damageType )

	def appendAttackerDoubleHit( self, skill ):
		"""
		call on real.
		����һ���ڡ�����������ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springAttackerDoubleHitList.append( skill )

	def removeAttackerDoubleHit( self, skillUID ):
		"""
		call on real.
		����һ���ڡ�����������ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerDoubleHitList ):
			if skill.getUID() == skillUID:
				self.springAttackerDoubleHitList.pop( index )
				return

	def doAttackerOnDoubleHit( self, receiver, damageType ):
		"""
		�ڲ���������ʱ��������˺�����ʱ�˿����Ѿ����ˣ�������
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		for spell in self.springAttackerDoubleHitList:
			spell.springOnDoubleHit( self, receiver, damageType )

	def appendVictimResistHit( self, skill ):
		"""
		call on real.
		����һ���ڡ��мܳɹ�ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimResistHitList.append( skill )

	def removeVictimResistHit( self, skillUID ):
		"""
		call on real.
		����һ���ڡ��мܳɹ�ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimResistHitList ):
			if skill.getUID() == skillUID:
				self.springVictimResistHitList.pop( index )
				return

	def doVictimOnResistHit( self, caster, damageType ):
		"""
		���мܳɹ�ʱ��������˺�����ʱ�˿����Ѿ����ˣ�������
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			for spell in self.springVictimResistHitList:
				spell.springOnResistHit( caster, self, damageType )

	def appendAttackerResistHit( self, skill ):
		"""
		call on real.
		����һ���ڡ�Ŀ���мܳɹ�ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springAttackerResistHitList.append( skill )

	def removeAttackerResistHit( self, skillUID ):
		"""
		call on real.
		����һ���ڡ�Ŀ���мܳɹ�ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerResistHitList ):
			if skill.getUID() == skillUID:
				self.springAttackerResistHitList.pop( index )
				return

	def doAttackerOnResistHit( self, receiver, damageType ):
		"""
		��Ŀ���мܳɹ�ʱ��������˺�����ʱ�˿����Ѿ����ˣ�������
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		for spell in self.springAttackerResistHitList:
			spell.springOnResistHit( self, receiver, damageType )

	def appendVictimBeforeDamage( self, skill ):
		"""
		call on real.
		����һ���ڡ����˺�����ǰ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimBeforeDamageList.append( skill )

	def removeVictimBeforeDamage( self, skillUID ):
		"""
		call on real.
		����һ���ڡ����˺�����ǰ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimBeforeDamageList ):
			if skill.getUID() == skillUID:
				self.springVictimBeforeDamageList.pop( index )
				return

	def appendAttackerAfterDamage( self, skill ):
		"""
		call on real.
		����һ���ڡ����˺�����󡭡�����������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springAttackerAfterDamageList.append( skill )

	def removeAttackerAfterDamage( self, skillUID ):
		"""
		call on real.
		����һ���ڡ����˺�����󡭡�����������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springAttackerAfterDamageList ):
			if skill.getUID() == skillUID:
				self.springAttackerAfterDamageList.pop( index )
				return

	def doAttackerAfterDamage( self, skill, receiver, damage ):
		"""
		���˺�����󣨼�����˺�����ʱ�˿����Ѿ����ˣ�����������Ҫ����һЩ��Ҫ���ܵ��˺��Ժ��ٴ�����Ч����

		�����ڣ�
		    ����Ŀ��ʱ$1%���ʸ���Ŀ������˺�$2
		    ����Ŀ��ʱ$1%����ʹĿ�깥��������$2������$3��
		    ������ʱ$1���ʻָ�$2����
		    ������ʱ$1%�����������$2������$3��
		    etc.
		@param skill:����ʵ��
		@type skill: SKILL
		@param receiver:������( ��һ����һ��real entity )
		@type receiver: ENTITY
		"""
		for spell in self.springAttackerAfterDamageList:
			spell.springOnDamage( self, receiver, skill, damage )

	def appendVictimAfterDamage( self, skill ):
		"""
		call on real.
		����һ���ڡ����˺�����󡭡�����������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springVictimAfterDamageList.append( skill )

	def removeVictimAfterDamage( self, skillUID ):
		"""
		call on real.
		����һ���ڡ����˺�����󡭡�����������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springVictimAfterDamageList ):
			if skill.getUID() == skillUID:
				self.springVictimAfterDamageList.pop( index )
				return

	def doVictimOnDamage( self, skill, caster, damage ):
		"""
		���˺�����󣨼�����˺�����ʱ�˿����Ѿ����ˣ�����������Ҫ����һЩ��Ҫ���ܵ��˺��Ժ��ٴ�����Ч����

		�����ڣ�
		    ����Ŀ��ʱ$1%���ʸ���Ŀ������˺�$2
		    ����Ŀ��ʱ$1%����ʹĿ�깥��������$2������$3��
		    ������ʱ$1���ʻָ�$2����
		    ������ʱ$1%�����������$2������$3��
		    etc.
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		# ��������mailbox�Զ�ת��Ϊentity���ñ��ı�Ϊ��ת������������Ҫ�ֶ�ת��Ϊentity, kebiao
		caster = BigWorld.entities.get( caster.id, None )
		if caster:
			caster.setTemp( "lastDPS", damage )
			for spell in self.springVictimAfterDamageList:
				spell.springOnDamage( caster, self, skill, damage )

	def appendImmunityBuff( self, skill ):
		"""
		call on real.
		����һ��������BUFF
		������Ҫ���ߵ����ͷǳ��Ķ�ǳ��Ĳ�ȷ�����ʹ�øô���ʽ
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springImmunityBuffList.append( skill )

	def removeImmunityBuff( self, skillUID ):
		"""
		call on real.
		ɾ��������BUFF
		������Ҫ���ߵ����ͷǳ��Ķ�ǳ��Ĳ�ȷ�����ʹ�øô���ʽ
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springImmunityBuffList ):
			if skill.getUID() == skillUID:
				self.springImmunityBuffList.pop( index )
				return

	def doImmunityBuff( self, caster, buffData ):
		"""
		ִ������������BUFF
		������Ҫ���ߵ����ͷǳ��Ķ�ǳ��Ĳ�ȷ�����ʹ�øô���ʽ
		�˽ӿ���Ҫ��֤receiver��real
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		for spell in self.springImmunityBuffList:
			state = spell.springOnImmunityBuff( caster, self, buffData )
			if state != csstatus.SKILL_GO_ON:
				return state
		return csstatus.SKILL_GO_ON

	def appendOnUseSkill( self, skill ):
		"""
		call on real.
		����һ���ڡ�ʹ�ü���ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springOnUseSkillList.append( skill )

	def removeOnUseSkill( self, skillUID ):
		"""
		call on real.
		����һ���ڡ�ʹ�ü���ʱ��������������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springOnUseSkillList ):
			if skill.getUID() == skillUID:
				self.springOnUseSkillList.pop( index )
				return

	def doOnUseSkill( self, skill ):
		"""
		��ʹ�ü���ʱ������ ���Խ��һЩ �罵����������ʱ�� ���ٻ�����ʩ�����ĵ�
		@param skill:����ʵ��
		@type skill: SKILL
		@param caster:ʩ����
		@type caster: ENTITY
		"""
		for spell in self.springOnUseSkillList:
			spell.springOnUseSkill( self, skill )

	def appendOnUseMaligSkill( self, skill ):
		"""
		call on real.
		����һ���ڡ�����ս��״̬�󡭡�����������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.springOnUseMaligSkill.append( skill )

	def removeOnUseMaligSkill( self, skillUID ):
		"""
		call on real.
		����һ���ڡ�����ս��״̬�󡭡�����������ͨ���ܻ�BUFF
		@param skill:����ʵ��
		@type skill: SKILL
		"""
		for index, skill in enumerate( self.springOnUseMaligSkill ):
			if skill.getUID() == skillUID:
				self.springOnUseMaligSkill.pop( index )
				return

	def doOnUseMaligSkill( self, skill ):
		"""
		��ʹ�ö��Լ��ܺ󴥷�
		"""
		for spell in self.springOnUseMaligSkill:
			spell.springOnUseMaligSkill( self, skill )

	def appendShield( self, skill ):
		"""
		call on real.
		����һ������

		@param shieldDict: ������������ʵ��, definition in alias.xml
		@type  shieldDict: SHIELD
		"""
		assert skill.getUID() !=0, "skill uid = 0!!"
		self.shields.append( skill )

	def removeShield( self, skillUID ):
		"""
		ɾ��һ������

		@param skillID: ��֮�����ļ���ID
		@type  skillID: SKILLID
		"""
		for index, skill in enumerate( self.shields ):
			if skill.getUID() == skillUID:
				self.shields.pop( index )
				return

	def getShieldsByType( self, dmgType ):
		"""
		��ȡ�����������ĳ���˺����͵Ļ���

		@param dmgType: �˺�����; SkillDefine::DAMAGE_TYPE_*
		@type  dmgType: INT
		@return: ���ҵ���ƥ��Ļ����б�format: [ (index,SHIELD type data), ... ]
		"""
		a = []
		for i, buff in enumerate( self.shields ):
			if buff["skill"].getShieldType() == dmgType:
				a.append( i )
		return a

	def shieldConsume( self, index, dmgType, damage ):
		"""
		���ܵ����Ĵ���  ע��: ����һ�����ؽӿ� �ڱ��ػ�����ִ�ж�����ȷ�ķ���һ��ֵ���ת��real cell��ִ��������ʵ��
		���������ﵽ2��cell�ϵĸû���һ�¡�
		@param index:�������ڵ�����
		@param damageType: �˺�����
		@param damage : �����˺�ֵ
		@return: ���ش������˺�ֵ
		"""
		try:
			shield = self.shields[index]
		except IndexError:
			# ����ĳ��������Ϊ����ʱ�䵽�˶�ɾ���� �ƻ��˴˴�ѭ��, ���ֱ�ӷ���
			WARNING_MSG( "can not find the shield (%i)" % index )
			return damage
		# ���ﴦ��������������
		nDamage = shield.doShield( self, dmgType, damage )
		if not self.isReal():
			self.remoteCall( "shieldConsume", ( index, dmgType, damage ) )
		else:
			self.shields[index] = self.shields[index]	# �������ܹ���������������ghostcell�Ϲ㲥����ʵ������ͬ��
			#���ﲻ�������ܵ�����ɾ������ ��ϸ�μ�filtrateMarShields�ӿ�˵��
		return nDamage

	def filtrateMarShields( self ):
		"""
		define method.
		�����𻵵Ļ���
		֮���Է��������� ����Ϊ��shieldConsume�ӿ���ɾ�����ƻ�����ѭ�����²���Ԥ�ϵĴ���
		������ΪBUFF�г���ʱ�������ɾ���Լ�Ҳ�ᵼ������ѭ����������λ�����������жϵĻ���,�������������¹���һ�β��ܱ�֤��ȫ
		"""
		m = []
		for shield in self.shields:
			if shield.isDisabled( self ):
				m.append( shield )

		m.reverse()
		for shield in m:
			rmb = []
			for idx in self.findBuffsByBuffID( shield.getBuffID() ):
				if self.getBuff( idx )["skill"].isDisabled( self ):
					rmb.append( idx )
			rmb.reverse()	# �Ӻ�����ǰɾ��
			for r in rmb:
				self.removeBuff( r, [csdefine.BUFF_INTERRUPT_NONE] )

	def calcShieldSuck( self, receiver, damage, damageType ):
		"""
		virtual method.
		���㱻���������ܶ��˺������� ��Ϊ�������֮���������ܻ�ο��˴ε�������������˺����Դ˽ӿڲ��ܷŵ�receiveDamage��
		��ʽ�������˺�=�˺� �C ��ǰʣ�໤��ֵ
		�����˺�����Ϊ0��
		Ȼ���ٶԻ��ܽ���������ʣ�໤��ֵ=��ǰʣ�໤��ֵ �C �����˺�
		ʣ�໤��ֵ����Ϊ0��
		ע���������������ͣ������ͻ��ܽ������������˺��������ͻ��ܽ������շ����˺��������ͻ��ܿ������κ��˺���
		��һ�ι��������а������������˺�ʱ�����ֱ�������ͽ������ա�
		�������������ڶ������Ч��ʱ���ȸ����������գ����ͬ���ͻ�����ʣ�����ʱ��̵������գ��������ͻ������������ֲ���ʱ���������ͻ���������/�����ͻ���֮�����á�

		@param target: ��������
		@type  target: entity
		@param  damage: �����м��жϺ���˺�
		@type   damage: INT
		@return: INT32
		"""
		#֮���Ի��ܼ������caster������Ϊ ����������caster��real��receiver.shields�Ǳ��������
		#�����caster����Ҳ�ǿ�����ô����ģ������ʱȽ�С��
		if len( receiver.shields ) > 0:
			for index, shield in enumerate( receiver.shields ):
				damage = receiver.shieldConsume( index, damageType, damage )
				if damage <= 0:
					break
			receiver.filtrateMarShields()
		return damage

	def calcDamageScissor( self, receiver, damage ):
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
		damage = damage * ( 1 - receiver.damage_derate_ratio / csconst.FLOAT_ZIP_PERCENT ) - receiver.damage_derate
		if damage < 0:
			damage = 0
		return damage

	def calcMagicDamageScissor( self, receiver, damage ):
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
		damage = damage * ( 1 - receiver.magic_damage_derate_ratio / csconst.FLOAT_ZIP_PERCENT ) - receiver.magic_damage_derate
		if damage < 0:
			damage = 0
		return damage

	def reboundDamage_Phy( self, caster, skillID, damage, rebound_damage_extra, rebound_damage_percent ):
		"""
		�����˺�������������
		@param casterID: ������ID
		@param damage: ��������ɵ��˺���ֵ
		"""
		# ��ʼ�˺���������
		rebound_damage = rebound_damage_extra
		rebound_damage += int( damage * rebound_damage_percent )
		rebound_damage = int( self.calcDamageScissor( caster, rebound_damage ) )
		rebound_damage = int( self.calcShieldSuck( caster, rebound_damage, csdefine.DAMAGE_TYPE_PHYSICS ) )
		if rebound_damage <= 0:
			return

		caster.receiveSpell( self.id, skillID, csdefine.DAMAGE_TYPE_PHYSICS|csdefine.DAMAGE_TYPE_REBOUND, rebound_damage, 0 )
		caster.receiveDamage( self.id, skillID, csdefine.DAMAGE_TYPE_PHYSICS|csdefine.DAMAGE_TYPE_REBOUND, rebound_damage )

	def reboundDamage_Magic( self, caster, skillID, damage, rebound_magic_damage_extra, rebound_magic_damage_percent ):
		"""
		�����˺�������������
		@param casterID: ������ID
		@param damage: ��������ɵ��˺���ֵ
		"""
		# ��ʼ�˺���������
		rebound_damage = rebound_magic_damage_extra
		rebound_damage += int( damage * rebound_magic_damage_percent )
		rebound_damage = int( self.calcMagicDamageScissor( caster, rebound_damage ) )
		rebound_damage = int( self.calcShieldSuck( caster, rebound_damage, csdefine.DAMAGE_TYPE_MAGIC ) )
		if rebound_damage <= 0:
			return

		caster.receiveSpell( self.id, skillID, csdefine.DAMAGE_TYPE_MAGIC|csdefine.DAMAGE_TYPE_REBOUND, rebound_damage, 0 )
		caster.receiveDamage( self.id, skillID, csdefine.DAMAGE_TYPE_MAGIC|csdefine.DAMAGE_TYPE_REBOUND, rebound_damage )


	def reboundDamage( self, casterID, skillID, damage, damageType ):
		"""
		�˺�������������
		@param damage: ��������ɵ��˺���ֵ
		"""
		if damageType & csdefine.DAMAGE_TYPE_REBOUND == csdefine.DAMAGE_TYPE_REBOUND:
			return

		try:
			caster = BigWorld.entities[ casterID ]
		except:
			WARNING_MSG( "not find the entityID %d" % casterID )
			return

		if damageType & ( csdefine.DAMAGE_TYPE_PHYSICS_NORMAL | csdefine.DAMAGE_TYPE_PHYSICS ):
			reboud_probability = self.queryTemp( "rebound_damage_probability", 0.0 )
			if reboud_probability > 0 and reboud_probability > random.random():
				rebound_damage_extra = self.queryTemp( "rebound_damage_extra", 0 )
				rebound_damage_percent = self.queryTemp( "rebound_damage_percent", 0.0 )
				if rebound_damage_extra > 0 or rebound_damage_percent > 0.0:
					self.reboundDamage_Phy( caster, skillID, damage, rebound_damage_extra, rebound_damage_percent )
		if damageType & csdefine.DAMAGE_TYPE_MAGIC:
			reboud_probability = self.queryTemp( "rebound_magic_damage_probability", 0.0 )
			if reboud_probability > 0 and reboud_probability > random.random():
				rebound_damage_extra = self.queryTemp( "rebound_magic_damage_extra", 0 )
				rebound_damage_percent = self.queryTemp( "rebound_magic_damage_percent", 0.0 )
				if rebound_damage_extra > 0 or rebound_damage_percent > 0.0:
					self.reboundDamage_Magic( caster, skillID, damage, rebound_damage_extra, rebound_damage_percent )

	# ----------------------------------------------------------------------------------------------------
	# race, class, gender, faction
	# ----------------------------------------------------------------------------------------------------
	def isRaceclass( self, rc, mask = csdefine.RCMASK_ALL):
		"""
		�Ƿ�Ϊָ������ְҵ��
		@return: bool
		"""
		return self.raceclass & mask == rc

	def getGender( self ):
		"""
		ȡ�������Ա�
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_GENDER

	def getRace( self ):
		"""
		ȡ����������
		@return: INT
		"""
		return self.raceclass & csdefine.RCMASK_RACE

	def getFaction( self ):
		"""
		ȡ����������������
		@return: INT
		"""
		return ( self.raceclass & csdefine.RCMASK_FACTION ) >> 12

	def getCamp( self ):
		"""
		ȡ��������Ӫ
		@return: INT
		"""
		return ( self.raceclass & csdefine.RCMASK_CAMP ) >> 20
		
	def getLevel( self ):
		"""
		���������
		"""
		return self.level
	
	def getDaoheng( self ):
		# ��ȡ�������ֵ
		return self.daoheng
	
	def addDaoheng( self, addValue, reason = 0 ):
		# ����������ֵ
		self.daoheng += addValue
	
	def setDaoheng( self, dxValue, reason = 0 ):
		# �����������ֵ
		self.daoheng = dxValue

	def isRealLook( self, entityID ):
		"""
		Define Method
		�Ƿ���⵽Ŀ��
		"""
		target = BigWorld.entities.get( entityID )
		if target is None: return True
		
		if target.isEntityType( csdefine.ENTITY_TYPE_PET ): #����ǳ���ж������˵������� add by wxuo 2012-6-8
			owner = target.getOwner()
			target = owner.entity
		# û����Ǳ�У�Ŀ��϶�����⵽
		if target.effect_state & csdefine.EFFECT_STATE_PROWL == 0: return True
		difLevel = ( target.level - self.level )*5 + target.sneakLevelAmend - self.realLookLevelAmend
		if difLevel > 25:
			odds = 0.0
		elif difLevel < -25:
			odds = 1.0
		else:
			odds = ( 1 - ( difLevel + 25 )/50.0 ) ** 2 + ( self.realLookAmend - target.lessRealLookAmend )/csconst.FLOAT_ZIP_PERCENT
		if random.random() <= odds:
			return True
		return False


	def addEnemyCheck( self, entityID ):
		"""
		"""
		if not EntityRelationTable.addEnemyCheck( self, entityID ):
			return False

		if self.getState() == csdefine.ENTITY_STATE_DEAD:
			return False
		
		entity = BigWorld.entities.get( entityID, None )
		if not entity:
			return False
			
		if self.queryRelation( entity ) != csdefine.RELATION_ANTAGONIZE:
			return False

		return True

	def moveToPosFC( self, endDstPos, targetMoveSpeed, targetMoveFace ):
		"""
		�����ƶ�
		"""
		pass
		
	def getCombatCamp( self ):
		"""
		��ȡս����Ӫ
		"""
		return self.combatCamp
		
	def getIsUseCombatCamp( self ):
		"""
		��ȡ�Ƿ�ʹ��ս����Ӫ
		"""
		return self.isUseCombatCamp
	
	def addCombatRelationIns( self, type, id ):
		inst = RelationDynamicObjImpl.createRelationObjSpecial( type, id )
		self.relationInsList.append( inst )
		pass
		
	def queryCombatRelationIns( self, type, id ):
		relationIns = None
		for inst in self.relationInsList:
			if inst.getID() == id and inst.getType() == type:
				relationIns = inst
				return relationIns
		return relationIns
		
	def removeCombatRelationIns( self, type, id ):
		removeInst = self.queryCombatRelationIns( type, id )
		if removeInst:
			self.relationInsList.remove( removeInst )
				
	def changeRelationMode( self, type ):
		if type in csconst.RELATION_TYPE_STATIC_SPACE or type == csdefine.RELATION_STATIC_CAMP:
			self.relationMode = type
		
	def queryCombatRelation( self, entity ):
		"""
		��ѯս����ϵ�ӿ�
		"""
		relation = 0
		ownRelationInsList = self.getRelationInsList()
		if ownRelationInsList:
			for inst in ownRelationInsList:
				relation = inst.queryCombatRelation( entity )
				if relation != csdefine.RELATION_NONE:
					return relation
					
		entityRelationInsList = entity.getRelationInsList()
		if entityRelationInsList:
			for inst in entityRelationInsList:
				relation = inst.queryCombatRelation( self )
				if relation != csdefine.RELATION_NONE:
					return relation
					
		type = self.getRelationMode()
		relationIns = g_relationStaticMgr.getRelationInsFromType( type )
		relation = relationIns.queryCombatRelation( self, entity )
		if relation != csdefine.RELATION_NONE:
			return relation
		
		return csdefine.RELATION_NEUTRALLY
	
	def getRelationMode( self ):
		"""
		��ȡս����ϵģʽ
		"""
		return self.relationMode
	
	def getRelationEntity( self ):
		"""
		��ȡ��ʵ�Ƚϵ�entityʵ��
		"""
		return self
		
	def getRelationInsList( self ):
		"""
		��ȡ�����relationInsList��Ҳ���ǹ�ϵʵ���б�
		"""
		return self.relationInsList
	
	def isNeedQueryRelation( self, entity ):
		"""
		�Ƿ���Ҫ��ѯ����֮��Ĺ�ϵ������Ѿ����ٻ��߲���CombatUnit����
		�Ͳ���Ҫ���²�ѯ��
		"""
		if self.isDestroyed and entity.isDestroyed:
			return False
		elif not isinstance( entity, CombatUnit ):
			return False
		else:
			return True
	
# CombatUnit.py
