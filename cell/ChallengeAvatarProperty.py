# -*- coding: gb18030 -*-

import csconst
import csdefine

"""
ְҵ	ְҵ����ϵ��	ְҵ���ϵ��	ְҵ����ϵ��
����	C				D				F
սʿ	1.25			0.67			1.4
����	1				1				1
����	1.18			1				1.4
��ʦ	0.9				1.9				0.5

Ӣ��ְҵ	����ϵ��	����ϵ��	���ϵ��	����ϵ��
����		A			B			E			G
�������	12			0.8			1.5			0.71
�Ƶ�����	10			1			1			1
��������	8.5			0.85		1			0.71
Ů洽���	8			1.1			0.53		1.96
"""
PLAYER_JOB_CONVER_DICT = {
	csdefine.CLASS_FIGHTER		:	( 1.25, 0.67, 1.40 ),
	csdefine.CLASS_SWORDMAN		:	( 1.00, 1.00, 1.00 ),
	csdefine.CLASS_ARCHER		:	( 1.18, 1.00, 1.40 ),
	csdefine.CLASS_MAGE			:	( 0.90, 1.90, 0.50 ),
}

class AvatarPropertyBase( object ):
	def __init__( self ):
		self.owner = None
		# ���ְҵϵ��
		self.c_damage = 0
		self.c_armor = 0
		self.c_magic_armor = 0
		
		self.HP_Max = 0
		self.save_HP_Max = 0
		
		self.MP_Max = 0
		self.save_MP_Max = 0
		
		self.damage_min = 0
		self.save_damage_min = 0
		
		self.damage_max = 0
		self.save_damage_max = 0
		
		self.magic_damage = 0
		self.save_magic_damage = 0
		
		self.armor = 0
		self.save_armor = 0
		
		self.magic_armor = 0
		self.save_magic_armor = 0
		
		self.save_hitProbability = 0
		
		self.save_double_hit_probability = 0
		
		self.save_magic_hitProbability = 0

		self.save_magic_double_hit_probability = 0
		
		self.save_dodge_probability = 0
		
		self.save_resist_hit_probability = 0
	
	def onInit( self, player ):
		self.setOwner( player )
		
	def setOwner( self, player):
		self.owner = player
		ownerClass = self.owner.getClass()
		self.c_damage = PLAYER_JOB_CONVER_DICT[ ownerClass ][ 0 ]
		self.c_armor = PLAYER_JOB_CONVER_DICT[ ownerClass ][ 1 ]
		self.c_magic_armor = PLAYER_JOB_CONVER_DICT[ ownerClass ][ 2 ]
	
	def initHPMax( self ):
		# ����ֵ
		self.save_HP_Max = self.HP_Max - self.owner.HP_Max
		self.owner.HP_Max_value = self.owner.HP_Max_value + self.save_HP_Max
		self.owner.calcHPMax()
	
	def resetHPMax( self ):
		self.owner.HP_Max_value = self.owner.HP_Max_value - self.save_HP_Max
		self.owner.calcHPMax()	
	
	def initMPMax( self ):
		# ħ��ֵ
		self.save_MP_Max = self.MP_Max - self.owner.MP_Max
		self.owner.MP_Max_value = self.owner.MP_Max_value + self.save_MP_Max
		self.owner.calcMPMax()
	
	def resetMPMax( self ):
		self.owner.MP_Max_value = self.owner.MP_Max_value - self.save_MP_Max
		self.owner.calcMPMax()		
	
	def initHitProbability( self ):
		"""
		���������� 
		�̶� 0.9
		"""
		self.save_hitProbability = 0.9 - self.owner.hitProbability
		self.owner.hitProbability_value = self.owner.hitProbability_value + self.save_hitProbability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcHitProbability()
	
	def resetHitProbability( self ):
		self.owner.hitProbability_value = self.owner.hitProbability_value - self.save_hitProbability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcHitProbability()
		
	def initDoubleHitProbability( self ):
		"""
		��������
		�̶� 0.2
		"""
		self.save_double_hit_probability = 0.2 - self.owner.double_hit_probability
		self.double_hit_probability_value = self.owner.double_hit_probability_value + self.save_double_hit_probability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcMagicDoubleHitProbability()
	
	def resetDoubleHitProbability( self ):
		self.owner.double_hit_probability_value = self.owner.double_hit_probability_value - self.save_double_hit_probability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcMagicDoubleHitProbability()
	
	def initMagicHitProbability( self ):
		"""
		����������
		�̶� 0.9
		"""
		self.save_magic_hitProbability = 0.9 - self.owner.magic_hitProbability
		self.owner.magic_hitProbability_value = self.owner.magic_hitProbability_value + self.save_magic_hitProbability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcMagicHitProbability()
	
	def resetMagicHitProbability( self ):
		self.owner.magic_hitProbability_value = self.owner.magic_hitProbability_value - self.save_magic_hitProbability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcMagicHitProbability()
		
	def initMagicDoubleHitProbability( self ):
		"""
		����������
		�̶� 0.2
		"""
		self.save_magic_double_hit_probability = 0.2 - self.owner.magic_double_hit_probability
		self.owner.magic_double_hit_probability_value = self.owner.magic_double_hit_probability_value + self.save_magic_double_hit_probability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcMagicDoubleHitProbability()
	
	def resetMagicDoubleHitProbability( self ):
		self.owner.magic_double_hit_probability_value = self.owner.magic_double_hit_probability_value - self.save_magic_double_hit_probability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcMagicDoubleHitProbability()
	
	def initDodgeProbability( self ):
		"""
		������
		�̶� 0.1
		"""
		self.save_dodge_probability = 0.1 - self.owner.dodge_probability
		self.owner.dodge_probability_value = self.owner.dodge_probability_value + self.save_dodge_probability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcDodgeProbability()
	
	def resetDodgeProbability( self ):
		self.owner.dodge_probability_value = self.owner.dodge_probability_value - self.save_dodge_probability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcDodgeProbability()
	
	def initResistHitProbability( self ):
		"""
		�м���
		�̶�0.1
		"""
		self.save_resist_hit_probability = 0.1 - self.owner.resist_hit_probability
		self.owner.resist_hit_probability_value = self.owner.resist_hit_probability_value + self.save_resist_hit_probability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcResistHitProbability()
	
	def resetResistHitProbability( self ):
		self.owner.resist_hit_probability_value = self.owner.resist_hit_probability_value - self.save_resist_hit_probability * csconst.FLOAT_ZIP_PERCENT
		self.owner.calcResistHitProbability()
	
	def initDamageMin( self ):
		"""
		������С��������
		"""
		self.save_damage_min = self.damage_min - self.owner.damage_min
		self.owner.damage_min_value = self.owner.damage_min_value + self.save_damage_min
		self.owner.calcDamageMin()
	
	def resetDamageMin( self ):
		self.owner.damage_min_value = self.owner.damage_min_value - self.save_damage_min
		self.owner.calcDamageMin()
	
	def initDamageMax( self ):
		"""
		���������������
		"""
		self.save_damage_max = self.damage_max - self.owner.damage_max
		self.owner.damage_max_value = self.owner.damage_max_value + self.save_damage_max
		self.owner.calcDamageMax()
	
	def resetDamageMax( self ):
		self.owner.damage_max_value = self.owner.damage_max_value - self.save_damage_max
		self.owner.calcDamageMax()
	
	def initMagicDamage( self ):
		"""
		����������
		"""
		self.save_magic_damage = self.magic_damage - self.owner.magic_damage
		self.owner.magic_damage_value = self.owner.magic_damage_value + self.save_magic_damage
		self.owner.calcMagicDamage()
	
	def resetMagicDamage( self ):
		self.owner.magic_damage_value = self.owner.magic_damage_value - self.save_magic_damage
		self.owner.calcMagicDamage()
	
	def initArmor( self ):
		"""
		�������ֵ	��ʾ����ɫ�ܵ�������ʱ���ܶԴ�������������������������
		"""
		self.save_armor = self.armor - self.owner.armor
		self.owner.armor_value = self.owner.armor_value + self.save_armor
		self.owner.calcArmor()
	
	def resetArmor( self ):
		self.owner.armor_value = self.owner.armor_value - self.save_armor
		self.owner.calcArmor()
	
	def initMagicArmor( self ):
		"""
		��������ֵ	��ʾ����ɫ�ܵ���������ʱ���ܶԴ˷�������������������������
		"""
		self.save_magic_armor = self.magic_armor - self.owner.magic_armor
		self.owner.magic_armor_value = self.owner.magic_armor_value + self.save_magic_armor
		self.owner.calcMagicArmor()
	
	def resetMagicArmor( self ):
		self.owner.magic_armor_value = self.owner.magic_armor_value - self.save_magic_armor
		self.owner.calcMagicArmor()
	
	def changeProperty( self ):
		self.owner.calcDynamicProperties()
		
		self.initHPMax()
		self.initMPMax()
		self.initHitProbability()
		self.initDoubleHitProbability()
		self.initMagicHitProbability()
		self.initMagicDoubleHitProbability()
		self.initDodgeProbability()
		self.initResistHitProbability()
		self.initDamageMin()
		self.initDamageMax()
		self.initMagicDamage()
		self.initArmor()
		self.initMagicArmor()
	
	def resetProperty( self ):
		self.resetHPMax()
		self.resetMPMax()
		self.resetHitProbability()
		self.resetDoubleHitProbability()
		self.resetMagicHitProbability()
		self.resetMagicDoubleHitProbability()
		self.resetDodgeProbability()
		self.resetResistHitProbability()
		self.resetDamageMin()
		self.resetDamageMax()
		self.resetMagicDamage()
		self.resetArmor()
		self.resetMagicArmor()
		
	def asDict( self ):
		# ���
		dict = {}
		dict[ "save_HP_Max" ] = self.save_HP_Max
		dict[ "save_MP_Max" ] = self.save_MP_Max
		dict[ "save_damage_min" ] = self.save_damage_min
		dict[ "save_damage_max" ] = self.save_damage_max 
		dict[ "save_magic_damage" ] = self.save_magic_damage
		dict[ "save_armor" ] = self.save_armor
		dict[ "save_magic_armor" ] = self.save_magic_armor
		dict[ "save_hitProbability" ] = self.save_hitProbability
		dict[ "save_double_hit_probability" ] = self.save_double_hit_probability
		dict[ "save_magic_hitProbability" ] = self.save_magic_hitProbability
		dict[ "save_magic_double_hit_probability" ] = self.save_magic_double_hit_probability
		dict[ "save_dodge_probability" ] = self.save_dodge_probability
		dict[ "save_resist_hit_probability" ] = self.save_resist_hit_probability
		return dict
	
	def resetObj( self, dict ):
		# �ָ�
		self.save_HP_Max = dict[ "save_HP_Max" ]
		self.save_MP_Max = dict[ "save_MP_Max" ]
		self.save_damage_min = dict[ "save_damage_min" ]
		self.save_damage_max = dict[ "save_damage_max" ]
		self.save_magic_damage = dict[ "save_magic_damage" ]
		self.save_armor = dict[ "save_armor" ]
		self.save_magic_armor = dict[ "save_magic_armor" ]
		self.save_hitProbability = dict[ "save_hitProbability" ]
		self.save_double_hit_probability = dict[ "save_double_hit_probability" ]
		self.save_magic_hitProbability = dict[ "save_magic_hitProbability" ]
		self.save_magic_double_hit_probability = dict[ "save_magic_double_hit_probability" ]
		self.save_dodge_probability = dict[ "save_dodge_probability" ]
		self.save_resist_hit_probability = dict[ "save_resist_hit_probability" ]
	
class AvatarPropertyChiyou( AvatarPropertyBase ):
	"""
	�������
	"""
	def __init__( self ):
		super( AvatarPropertyChiyou, self ).__init__()
		
	def initHPMax( self ):
		"""
		real entity method.
		��������ֵ
		��ʽ��(315��1.5^(0.1��Lvl-1)+����������ʡ�3)��12
		"""
		self.HP_Max = ( 315 * 1.5 ** (0.1 * self.owner.level - 1) + self.owner.corporeity * 3) * 12
		super( AvatarPropertyChiyou, self ).initHPMax()

	def initMPMax( self ):
		"""
		real entity method.
		��������ֵ
		��ʽ����315��1.5^(0.1��Lvl-1)+�������������3����10
		"""
		self.MP_Max = (315 * 1.5 ** ( 0.1 * self.owner.level - 1 ) +  self.owner.intellect * 3 ) * 10
		super( AvatarPropertyChiyou, self ).initMPMax()

	def initDamageMin( self ):
		"""
		������С��������
		��ʽ��80��1.5^(0.1��Lvl-1)��7+����������﹥+������﷨���������ְҵ����ϵ����3
		"""
		damage_min = 80 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 + ( self.owner.damage_min + self.owner.magic_damage ) * self.c_damage * 3
		if damage_min < 0:damage_min = 0
		if self.damage_min != damage_min: self.damage_min = damage_min
		super( AvatarPropertyChiyou, self ).initDamageMin()
	
	def initDamageMax( self ):
		"""
		���������������
		��ʽ��(80��1.5^(0.1��Lvl-1)��7+(��������﹥+������﷨��)�����ְҵ����ϵ����3
		"""
		damage_max = 80 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 + ( self.owner.damage_max + self.owner.magic_damage ) * self.c_damage * 3
		if damage_max < 0:damage_max = 0
		if self.damage_max != damage_max: self.damage_max = damage_max
		super( AvatarPropertyChiyou, self ).initDamageMax()
	
	def initMagicDamage( self ):
		"""
		����������
		��ʽ��80��1.5^(0.1��Lvl-1)��7+����������﹥+������﷨���������ְҵ����ϵ����3
		"""
		magic_damage = 80 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 + ( self.owner.damage_max - self.save_damage_max + self.owner.magic_damage )* self.c_damage * 3
		if magic_damage < 0:magic_damage = 0.0
		if self.magic_damage != magic_damage: self.magic_damage = magic_damage
		super( AvatarPropertyChiyou, self ).initMagicDamage()
	
	def initArmor( self ):
		"""
		�������ֵ	��ʾ����ɫ�ܵ�������ʱ���ܶԴ�������������������������
		��ʽ����133��1.5^(0.1��Lvl-1)��0.7+������ֵ�����ְҵ���ϵ����0.3����1.5
		"""
		armor =( 133 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 0.7 + self.owner.armor * self.c_armor * 0.3 ) * 1.5
		if self.armor != armor: self.armor = armor
		super( AvatarPropertyChiyou, self ).initArmor()
	
	def initMagicArmor( self ):
		"""
		��������ֵ	��ʾ����ɫ�ܵ���������ʱ���ܶԴ˷�������������������������
		��ʽ����188��1.5^(0.1��Lvl-1)��0.7+��ҷ���ֵ�����ְҵ����ϵ����0.3����0.71
		"""
		magic_armor = ( 188 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 0.7 + self.owner.magic_armor * self.c_magic_armor * 0.3 ) * 0.71
		if self.magic_armor != magic_armor: self.magic_armor = magic_armor
		super( AvatarPropertyChiyou, self ).initMagicArmor()
		
class AvatarPropertyHuangdi( AvatarPropertyBase ):
	"""
	�ʵ�����
	"""
	def __init__( self ):
		super( AvatarPropertyHuangdi, self ).__init__()
		
	def initHPMax( self ):
		"""
		real entity method.
		��������ֵ
		��ʽ����315��1.5^(0.1��Lvl-1)+����������ʡ�3����10
		"""
		self.HP_Max =( 315 * 1.5 ** ( 0.1 * self.owner.level - 1 ) + self.owner.corporeity * 3 ) * 10
		super( AvatarPropertyHuangdi, self ).initHPMax()
	
	def initMPMax( self ):
		"""
		real entity method.
		��������ֵ
		��ʽ����315��1.5^(0.1��Lvl-1)+�������������3����10
		"""
		self.MP_Max =( 315 * 1.5 ** ( 0.1 * self.owner.level - 1 ) +  self.owner.intellect * 3 ) * 10
		super( AvatarPropertyHuangdi, self ).initMPMax()
	
	def initDamageMin( self ):
		"""
		������С��������
		��ʽ��100��1.5^(0.1��Lvl-1)��7+����������﹥+������﷨���������ְҵ����ϵ����3
		"""
		damage_min = 100 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 +( self.owner.damage_min + self.owner.magic_damage ) * self.c_damage * 3
		if damage_min < 0:damage_min = 0
		if self.damage_min != damage_min: self.damage_min = damage_min
		super( AvatarPropertyHuangdi, self ).initDamageMin()
	
	def initDamageMax( self ):
		"""
		���������������
		��ʽ��100��1.5^(0.1��Lvl-1)��7+����������﹥+������﷨���������ְҵ����ϵ����3
		"""
		damage_max = 100 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 + ( self.owner.damage_max + self.owner.magic_damage ) * self.c_damage * 3
		if damage_max < 0:damage_max = 0
		if self.damage_max != damage_max: self.damage_max = damage_max
		super( AvatarPropertyHuangdi, self ).initDamageMax()
	
	def initMagicDamage( self ):
		"""
		����������
		��ʽ��100��1.5^(0.1��Lvl-1)��7+����������﹥+������﷨���������ְҵ����ϵ����3
		"""
		magic_damage = 100 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 +( self.owner.damage_max - self.save_damage_max + self.owner.magic_damage )* self.c_damage * 3
		if magic_damage < 0:magic_damage = 0.0
		if self.magic_damage != magic_damage: self.magic_damage = magic_damage
		super( AvatarPropertyHuangdi, self ).initMagicDamage()
	
	def initArmor( self ):
		"""
		�������ֵ	��ʾ����ɫ�ܵ�������ʱ���ܶԴ�������������������������
		��ʽ����133��1.5^(0.1��Lvl-1)��0.7+������ֵ�����ְҵ���ϵ����0.3����1
		"""
		armor =( 133 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 0.7 + self.owner.armor * self.c_armor * 0.3 ) * 1.0
		if self.armor != armor: self.armor = armor
		super( AvatarPropertyHuangdi, self ).initArmor()
	
	def initMagicArmor( self ):
		"""
		��������ֵ	��ʾ����ɫ�ܵ���������ʱ���ܶԴ˷�������������������������
		��ʽ����188��1.5^(0.1��Lvl-1)��0.7+��ҷ���ֵ�����ְҵ����ϵ����0.3����1
		"""
		magic_armor = ( 188 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 0.7 + self.owner.magic_armor * self.c_magic_armor * 0.3 ) * 1.0
		if self.magic_armor != magic_armor: self.magic_armor = magic_armor
		super( AvatarPropertyHuangdi, self ).initMagicArmor()

class AvatarPropertyHouyi( AvatarPropertyBase ):
	"""
	��������
	"""
	def __init__( self ):
		super( AvatarPropertyHouyi, self ).__init__()
		
	def initHPMax( self ):
		"""
		real entity method.
		��������ֵ
		��ʽ����315��1.5^(0.1��Lvl-1)+����������ʡ�3����8.5
		"""
		self.HP_Max =( 315 * 1.5 ** ( 0.1 * self.owner.level - 1 ) + self.owner.corporeity * 3 ) * 8.5
		super( AvatarPropertyHouyi, self ).initHPMax()

	def initMPMax( self ):
		"""
		real entity method.
		��������ֵ
		��ʽ����315��1.5^(0.1��Lvl-1)+�������������3����10
		"""
		self.MP_Max =( 315 * 1.5 ** ( 0.1 * self.owner.level - 1 ) +  self.owner.intellect * 3 ) * 10
		super( AvatarPropertyHouyi, self ).initMPMax()
	
	def initDamageMin( self ):
		"""
		������С��������
		��ʽ��85��1.5^(0.1��Lvl-1)��7+����������﹥+������﷨���������ְҵ����ϵ����3
		"""
		damage_min = 85 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 +( self.owner.damage_min + self.owner.magic_damage ) * self.c_damage * 3
		if damage_min < 0:damage_min = 0
		if self.damage_min != damage_min: self.damage_min = damage_min
		super( AvatarPropertyHouyi, self ).initDamageMin()
	
	def initDamageMax( self ):
		"""
		���������������
		��ʽ��85��1.5^(0.1��Lvl-1)��7+����������﹥+������﷨���������ְҵ����ϵ����3
		"""
		damage_max = 85 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 +( self.owner.damage_max + self.owner.magic_damage ) * self.c_damage * 3
		if damage_max < 0:damage_max = 0
		if self.damage_max != damage_max: self.damage_max = damage_max
		super( AvatarPropertyHouyi, self ).initDamageMax()
	
	def initMagicDamage( self ):
		"""
		����������
		��ʽ��85��1.5^(0.1��Lvl-1)��7+����������﹥+������﷨���������ְҵ����ϵ����3
		"""
		magic_damage = 85 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 +( self.owner.damage_max - self.save_damage_max + self.owner.magic_damage )* self.c_damage * 3
		if magic_damage < 0:magic_damage = 0.0
		if self.magic_damage != magic_damage: self.magic_damage = magic_damage
		super( AvatarPropertyHouyi, self ).initMagicDamage()
	
	def initArmor( self ):
		"""
		�������ֵ	��ʾ����ɫ�ܵ�������ʱ���ܶԴ�������������������������
		��ʽ����133��1.5^(0.1��Lvl-1)��0.7+������ֵ�����ְҵ���ϵ����0.3����1
		"""
		armor =( 133 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 0.7 + self.owner.armor * self.c_armor * 0.3 ) * 1.0
		if self.armor != armor: self.armor = armor
		super( AvatarPropertyHouyi, self ).initArmor()
	
	def initMagicArmor( self ):
		"""
		��������ֵ	��ʾ����ɫ�ܵ���������ʱ���ܶԴ˷�������������������������
		��ʽ����188��1.5^(0.1��Lvl-1)��0.7+��ҷ���ֵ�����ְҵ����ϵ����0.3����0.71
		"""
		magic_armor = ( 188 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 0.7 + self.owner.magic_armor * self.c_magic_armor * 0.3 ) * 0.71
		if self.magic_armor != magic_armor: self.magic_armor = magic_armor
		super( AvatarPropertyHouyi, self ).initMagicArmor()
		
class AvatarPropertyNuwo( AvatarPropertyBase ):
	"""
	Ů洽���
	"""
	def __init__( self ):
		super( AvatarPropertyNuwo, self ).__init__()
		
	def initHPMax( self ):
		"""
		real entity method.
		��������ֵ
		��ʽ����315��1.5^(0.1��Lvl-1)+����������ʡ�3����8
		"""
		self.HP_Max =( 315 * 1.5 ** ( 0.1 * self.owner.level - 1 ) + self.owner.corporeity * 3 ) * 8.0
		super( AvatarPropertyNuwo, self ).initHPMax()
	
	def initMPMax( self ):
		"""
		real entity method.
		��������ֵ
		��ʽ����315��1.5^(0.1��Lvl-1)+�������������3����10
		"""
		self.MP_Max =( 315 * 1.5 ** ( 0.1 * self.owner.level - 1 ) +  self.owner.intellect * 3 ) * 10
		super( AvatarPropertyNuwo, self ).initMPMax()
	
	def initDamageMin( self ):
		"""
		������С��������
		��ʽ��110��1.5^(0.1��Lvl-1)��7+����������﹥+������﷨���������ְҵ����ϵ����3
		"""
		damage_min = 110 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 +( self.owner.damage_min + self.owner.magic_damage ) * self.c_damage * 3
		if damage_min < 0:damage_min = 0
		if self.damage_min != damage_min: self.damage_min = damage_min
		super( AvatarPropertyNuwo, self ).initDamageMin()
	
	def initDamageMax( self ):
		"""
		���������������
		��ʽ��110��1.5^(0.1��Lvl-1)��7+����������﹥+������﷨���������ְҵ����ϵ����3
		"""
		damage_max = 110 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 +( self.owner.damage_max + self.owner.magic_damage ) * self.c_damage * 3
		if damage_max < 0:damage_max = 0
		if self.damage_max != damage_max: self.damage_max = damage_max
		super( AvatarPropertyNuwo, self ).initDamageMax()
	
	def initMagicDamage( self ):
		"""
		����������
		��ʽ��110��1.5^(0.1��Lvl-1)��7+����������﹥+������﷨���������ְҵ����ϵ����3
		"""
		magic_damage = 110 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 7 +( self.owner.damage_max - self.save_damage_max + self.owner.magic_damage )* self.c_damage * 3
		if magic_damage < 0:magic_damage = 0.0
		if self.magic_damage != magic_damage: self.magic_damage = magic_damage
		super( AvatarPropertyNuwo, self ).initMagicDamage()
	
	def initArmor( self ):
		"""
		�������ֵ	��ʾ����ɫ�ܵ�������ʱ���ܶԴ�������������������������
		��ʽ����133��1.5^(0.1��Lvl-1)��0.7+������ֵ�����ְҵ���ϵ����0.3����0.53
		"""
		armor =( 133 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 0.7 + self.owner.armor * self.c_armor * 0.3 ) * 0.53
		if self.armor != armor: self.armor = armor
		super( AvatarPropertyNuwo, self ).initArmor()
	
	def initMagicArmor( self ):
		"""
		��������ֵ	��ʾ����ɫ�ܵ���������ʱ���ܶԴ˷�������������������������
		��ʽ����188��1.5^(0.1��Lvl-1)��0.7+��ҷ���ֵ�����ְҵ����ϵ����0.3����1.96
		"""
		magic_armor = ( 188 * 1.5 ** ( 0.1 * self.owner.level - 1 ) * 0.7 + self.owner.magic_armor * self.c_magic_armor * 0.3 ) * 1.96
		if self.magic_armor != magic_armor: self.magic_armor = magic_armor
		super( AvatarPropertyNuwo, self ).initMagicArmor()
