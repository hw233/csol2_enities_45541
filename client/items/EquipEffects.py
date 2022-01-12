# -*- coding: gb18030 -*-

# $Id: EquipEffects.py,v 1.9 2008-05-13 00:57:19 zhangyuxing Exp $

import math
import skills
from bwdebug import *
from config.client.labels.items import lbs_EquipEffects


# ��ʽ����
_iFormatter = lambda name, value : "%s + %i" % ( name, math.ceil( value ) )
_iListFormatter = lambda name, value : [name, "+%i" % math.ceil( value )]
_iFormatter2 = lambda name, value : "%s + %i%%" % ( name, math.ceil( value ) )
_iListFormatter2 = lambda name, value : [name, "+%i%%" % math.ceil( value )]
_fFormatter = lambda name, value : "%s + %0.1f%%" % ( name, value * 100 )
_fListFormatter = lambda name, value : [name, "+%0.1f%%" % ( value * 100 ) ]
_fFormatter2 = lambda name, value : "%s + %0.2f" % ( name, value / 100.0 )	# Ԫ�ؿ�����
_fListFormatter2 = lambda name, value : [name, "+%0.2f" % ( value / 100.0 ) ]	# Ԫ�ؿ�����
_fFormatter3 = lambda name, value : "%s + %0.2f%%" % ( name, value / 100.0 )	# Ԫ����
_fListFormatter3 = lambda name, value : [name, "+%0.2f%%" % ( value / 100.0 ) ]	# Ԫ����

# -----------------------------------------------
# ���ʼ�ֵ
# -----------------------------------------------
class AddValueCorporeity:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[1], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[1], param )

class AddPercentCorporeity:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[1], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[1], param )

# -----------------------------------------------
# ������ֵ
# -----------------------------------------------
class AddValueIntellect:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[2], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[2], param )

class AddPercentIntellect:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[2], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[2], param )

# -----------------------------------------------
# ������ֵ
# -----------------------------------------------
class AddValueStrength:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[3], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[3], param )

class AddPercentStrength:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[3], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[3], param )

# -----------------------------------------------
# ���ݼ�ֵ
# -----------------------------------------------
class AddValueDexterity:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[4], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[4], param )

class AddPercentDexterity:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[4], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[4], param )

# -----------------------------------------------
# ������ֵ
# -----------------------------------------------
class AddValueHP:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[5], param)

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[5], param )

class AddPercentHP:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[5], param)

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[5], param )

# -----------------------------------------------
# ������ֵ
# -----------------------------------------------
class AddValueMP:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[6], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[6], param )

class AddPercentMP:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[6], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[6], param )

# -----------------------------------------------
# ���������ֵ
# -----------------------------------------------
class AddValueArmor:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[7], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[7], param )

class AddPercentArmor:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[7], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[7], param )

# -----------------------------------------------
# ����������ֵ
# -----------------------------------------------
class AddValueMagicArmor:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[8], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[8], param )

class AddPercentMagicArmor:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[8], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[8], param )

# -----------------------------------------------
# ��ɫ��������
# -----------------------------------------------
class AddValueDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[9], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[9], param )

class AddPercentDamage:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[9], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[9], param )

# -----------------------------------------------
# ��ɫ����������
# -----------------------------------------------
class AddValueMagicDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[10], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[10], param )

class AddPercentMagicDamage:
	@staticmethod
	def description( param ):
		return _iFormatter2( lbs_EquipEffects[10], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter2( lbs_EquipEffects[10], param )

# -----------------------------------------------
# ��������
# -----------------------------------------------
class AddValueSkillExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[9], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[9], param )

# -----------------------------------------------
# ����������
# -----------------------------------------------
class AddValueMagicSkillExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[10], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[10], param )

# -----------------------------------------------
# �����ָ��ٶ�
# -----------------------------------------------
class AddValueHPRegen:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[11], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[11], param )

# -----------------------------------------------
# �����ָ��ٶ�
# -----------------------------------------------
class AddValueMPRegen:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[12], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[12], param )

# -----------------------------------------------
# ��С������
# -----------------------------------------------
class AddValueDamageMin:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[13], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[13], param )

# -----------------------------------------------
# ��󹥻���
# -----------------------------------------------
class AddValueDamageMax:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[14], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[14], param )

# -----------------------------------------------
# �������е���
# -----------------------------------------------
class AddValueHit:

	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[15], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[15], param )


# -----------------------------------------------
# �������е���
# -----------------------------------------------
class AddValueMagicHit:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[16], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[16], param )

# -----------------------------------------------
# ���ܵ���
# -----------------------------------------------
class AddValueDodge:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[17], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[17], param )

# -----------------------------------------------
# ����������
# -----------------------------------------------
class AddValueDoubleHit:

	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[18], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[18], param )

# -----------------------------------------------
# ������������
# -----------------------------------------------
class AddValueMagicDoubleHit:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[19], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[19], param )

# -----------------------------------------------
# �мܵ���
# -----------------------------------------------
class AddValueResistHit:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[20], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[20], param )

# -----------------------------------------------
# �мܼ��˵���
# -----------------------------------------------
class AddValueResistHitDerate:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[21], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[21], param )

# -----------------------------------------------
# �����˺�����
# -----------------------------------------------
class AddValueDamageDerate:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[22], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[22], param )

# -----------------------------------------------
# �����˺�����
# -----------------------------------------------
class AddValueMagicDamageDerate:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[23], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[23], param )


# -----------------------------------------------
# �˺�����
# -----------------------------------------------
class AddValueAllDerate:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[24], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[24], param )

# -----------------------------------------------
# ��Ч��������
# -----------------------------------------------
class AddValueSpeciallySpring:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[25], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[25], param )

# -----------------------------------------------
# �������˺�����
# -----------------------------------------------
class AddValueDoubleHitMultiple:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[26], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[26], param )

# -----------------------------------------------
# ���������˺�����
# -----------------------------------------------
class AddValueMagicDoubleHitMultiple:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[27], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[27], param )

# -----------------------------------------------
# ���ͶԷ��������е���
# -----------------------------------------------
class AddValueReduceTargetHit:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[28], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[28], param )

# -----------------------------------------------
#���ͶԷ��������е���
# -----------------------------------------------
class AddValueReduceTargetMagicHit:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[29], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[29], param )

# -----------------------------------------------
# �ֿ���Ĭ����
# -----------------------------------------------
class AddValueResistChenmo:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[30], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[30], param )

# -----------------------------------------------
# �ֿ�ѣ��
# -----------------------------------------------
class AddValueResistGiddy:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[31], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[31], param )

# -----------------------------------------------
# �ֿ�����
# -----------------------------------------------
class AddValueResistFix:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[32], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[32], param )

# -----------------------------------------------
# �ֿ�˯��
# -----------------------------------------------
class AddValueResistSleep:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[33], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[33], param )

# -----------------------------------------------
# �ֿ���Ĭ����
# -----------------------------------------------
class AddValueResistChenmoOdds:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[34], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[34], param )

# -----------------------------------------------
# �ֿ�ѣ�μ���
# -----------------------------------------------
class AddValueResistGiddyOdds:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[35], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[35], param )

# -----------------------------------------------
# �ֿ�������
# -----------------------------------------------
class AddValueResistFixOdds:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[36], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[36], param )

# -----------------------------------------------
# �ֿ�˯�߼���
# -----------------------------------------------
class AddValueResistSleepOdds:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[37], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[37], param )

# -----------------------------------------------
# �����ٶ�
# -----------------------------------------------
class AddValueHitSpeed:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[38], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[39], param )

# -----------------------------------------------
# �ƶ��ٶ�
# -----------------------------------------------
class AddValueMoveSpeed:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[39], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[39], param )

# -----------------------------------------------
# ��������
# -----------------------------------------------
class AddValueRange:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[40], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[40], param )

# -----------------------------------------------
# ��Ч������
# -----------------------------------------------
class AddValueSpeciallySpringPro:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[41], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[41], param )

# -----------------------------------------------
# ��������
# -----------------------------------------------
class AddValueDoubleHitPro:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[42], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[42], param )

# -----------------------------------------------
# ����������
# -----------------------------------------------
class AddValueMagicDoubleHitPro:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[43], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[43], param )

# -----------------------------------------------
# ���������ʼ���
# -----------------------------------------------
class AddValueBeDoubleHitProReduce:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[115], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[115], param )

# -----------------------------------------------
# �����������ʼ���
# -----------------------------------------------
class AddValueMagicBeDoubleHitProReduce:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[116], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[116], param )

# -----------------------------------------------
# ����������
# -----------------------------------------------
class AddValueHitPro:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[44], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[44], param )

# -----------------------------------------------
# ����������
# -----------------------------------------------
class AddValueMagicHitPro:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[45], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[45], param )

# -----------------------------------------------
# ����������
# -----------------------------------------------
class AddValueWeaponDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[46], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[46], param )

# -----------------------------------------------
# ���ʼӳ�
# -----------------------------------------------
class AddPercentCorporeity:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[47], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[47], param )

# -----------------------------------------------
# �����ӳ�
# -----------------------------------------------
class AddPercentIntellect:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[48], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[48], param )

# -----------------------------------------------
# �����ӳ�
# -----------------------------------------------
class AddPercentStrength:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[49], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[49], param )

# -----------------------------------------------
# ���ݼӳ�
# -----------------------------------------------
class AddPercentDexterity:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[50], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[50], param )

# -----------------------------------------------
# �����ӳ�
# -----------------------------------------------
class AddPercentHP:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[51], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[51], param )

# -----------------------------------------------
# �����ӳ�
# -----------------------------------------------
class AddPercentMP:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[52], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[52], param )

# -----------------------------------------------
# ��������ӳ�
# -----------------------------------------------
class AddPercentArmor:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[53], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[53], param )

# -----------------------------------------------
# ���������ӳ�
# -----------------------------------------------
class AddPercentMagicArmor:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[54], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[54], param )

# -----------------------------------------------
# �����������ӳ�
# -----------------------------------------------
class AddPercentWeaponDamage:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[55], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[55], param )

# -----------------------------------------------
# ��ɫ���������ӳ�
# -----------------------------------------------
class AddPercentDamage:

	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[56], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[56], param )

# -----------------------------------------------
# ��ɫ�����������ӳ�
# -----------------------------------------------
class AddPercentMagicDamage:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[57], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[57], param )

# -----------------------------------------------
# ���������ӳɣ���ָ������Ӱ��������ļӳɣ�
# -----------------------------------------------
class AddPercentSkillExtra:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[58], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[58], param )

# -----------------------------------------------
# ��������������ָ��������Ӱ��������ļӳɣ�
# -----------------------------------------------
class AddPercentMagicSkillExtra:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[59], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[59], param )

# -----------------------------------------------
# �����ָ��ٶȼӳ�
# -----------------------------------------------
class AddPercentHPRegen:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[60], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[60], param )

# -----------------------------------------------
# �����ָ��ٶȼӳ�
# -----------------------------------------------
class AddPercentMPRegen:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[61], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[61], param )

# -----------------------------------------------
# �����˺�����ӳ�
# -----------------------------------------------
class AddPercentDamageDerate:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[62], param )


	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[62], param )

# -----------------------------------------------
# �����˺�����
# -----------------------------------------------
class AddPercentMagicDamageDerate:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[63], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[63], param )

# -----------------------------------------------
# �˺�����ӳ�
# -----------------------------------------------
class AddPercentAllDerate:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[64], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[64], param )

# -----------------------------------------------
# ����ӳ�
# -----------------------------------------------
class AddPercentMultExp:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[65], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[65], param )

# -----------------------------------------------
# Ǳ�ܵ�ӳ�
# -----------------------------------------------
class AddPercentMultPotential:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[66], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[66], param )


# -----------------------------------------------
# �ƶ��ٶȼӳ�
# -----------------------------------------------
class AddPercentMoveSpeed:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[67], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[67], param )

# -----------------------------------------------
# �����ٶ�
# -----------------------------------------------
class AddPercentHitSpeed:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[68], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[68], param )

# -----------------------------------------------
# Ԫ�����
# -----------------------------------------------
#-------------��------------------------
class AddHuoDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[107], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[107], param )

class AddHuoDamageBase:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[107], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[107], param )

class AddHuoDamagePercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[107], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[107], param )

class AddHuoDamageExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[107], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[107], param )

class AddHuoDamageValue:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[107], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[107], param )

class AddHuoDR:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[111], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[111], param )

class AddHuoDRBase:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[111], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[111], param )

class AddHuoDRPercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[111], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[111], param )

class AddHuoDRExtra:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[111], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[111], param )

class AddHuoDRValue:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[111], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[111], param )
#-------------��------------------------
class AddXuanDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[108], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[108], param )

class AddXuanDamageBase:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[108], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[108], param )

class AddXuanDamagePercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[108], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[108], param )

class AddXuanDamageExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[108], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[108], param )

class AddXuanDamageValue:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[108], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[108], param )

class AddXuanDR:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[112], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[112], param )

class AddXuanDRBase:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[112], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[112], param )

class AddXuanDRPercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[112], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[112], param )

class AddXuanDRExtra:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[112], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[112], param )

class AddXuanDRValue:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[112], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[112], param )
#-------------��------------------------
class AddLeiDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[109], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[109], param )

class AddLeiDamageBase:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[109], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[109], param )

class AddLeiDamagePercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[109], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[109], param )

class AddLeiDamageExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[109], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[109], param )

class AddLeiDamageValue:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[109], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[109], param )

class AddLeiDR:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[113], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[113], param )

class AddLeiDRBase:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[113], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[113], param )

class AddLeiDRPercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[113], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[113], param )

class AddLeiDRExtra:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[113], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[113], param )

class AddLeiDRValue:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[113], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[113], param )
#-------------��------------------------
class AddBingDamage:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[110], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[110], param )

class AddBingDamageBase:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[110], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[110], param )

class AddBingDamagePercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[110], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[110], param )

class AddBingDamageExtra:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[110], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[110], param )

class AddBingDamageValue:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[110], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[110], param )

class AddBingDR:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[114], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[114], param )

class AddBingDRBase:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[114], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[114], param )

class AddBingDRPercent:
	@staticmethod
	def description( param ):
		return _fFormatter3( lbs_EquipEffects[114], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter3( lbs_EquipEffects[114], param )

class AddBingDRExtra:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[114], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[114], param )

class AddBingDRValue:
	@staticmethod
	def description( param ):
		return _fFormatter2( lbs_EquipEffects[114], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter2( lbs_EquipEffects[114], param )
# -----------------------------------------------
#
# -----------------------------------------------
class SPEAddBuff:
	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return _fFormatter

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[69], sk.getDescription()]

# -----------------------------------------------
#
# -----------------------------------------------
class SPEHitSpring:
	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[100] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[100], sk.getDescription()]


# -----------------------------------------------
#
# -----------------------------------------------
class SPEMagicHitSpring:

	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[101] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[101], sk.getDescription() ]


# -----------------------------------------------
#
# -----------------------------------------------
class SPEBeHitSpring:
	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[102] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[102], sk.getDescription() ]

# -----------------------------------------------
#
# -----------------------------------------------
class SPEBeDoubleHitSpring:
	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[103] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[103], sk.getDescription()]

# -----------------------------------------------
#
# -----------------------------------------------
class SPEDoubleHitSpring:
	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[104] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[104], sk.getDescription() ]

# -----------------------------------------------
#
# -----------------------------------------------
class SPEMagicDoubleHitSpring:

	@staticmethod
	def description( param ):
		sk = skills.getSkill( param )
		return lbs_EquipEffects[105] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSkill( param )
		return [lbs_EquipEffects[105], sk.getDescription() ]

# -----------------------------------------------
#
# -----------------------------------------------
class SPEAddSkill:
	@staticmethod
	def description( param ):
		sk = skills.getSKill( param )
		return lbs_EquipEffects[106] + sk.getDescription()

	@staticmethod
	def descriptionList( param ):
		sk = skills.getSKill( param )
		return [lbs_EquipEffects[106], sk.getDescription()]

# -----------------------------------------------
#
# -----------------------------------------------
class SPENone:
	@staticmethod
	def description( param ):
		return ""

# -----------------------------------------------
# ���ӳ������
# -----------------------------------------------
class AddBuffOdds1:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[117], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[117], param )

# -----------------------------------------------
# �����ͻ�����
# -----------------------------------------------
class AddBuffOdds2:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[118], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[118], param )

# -----------------------------------------------
# ���Ӻ�ɨ����
# -----------------------------------------------
class AddBuffOdds3:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[119], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[119], param )

# -----------------------------------------------
# ����̩ɽѹ������
# -----------------------------------------------
class AddBuffOdds4:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[120], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[120], param )

# -----------------------------------------------
# ���Ӿ�������
# -----------------------------------------------
class AddBuffOdds5:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[121], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[121], param )

# -----------------------------------------------
# ������������
# -----------------------------------------------
class AddBuffOdds6:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[122], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[122], param )

# -----------------------------------------------
# ������������
# -----------------------------------------------
class AddBuffOdds7:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[123], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[123], param )

# -----------------------------------------------
# ���ӿ콣����
# -----------------------------------------------
class AddBuffOdds8:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[124], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[124], param )

# -----------------------------------------------
# �������ལ����
# -----------------------------------------------
class AddBuffOdds9:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[125], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[125], param )

# -----------------------------------------------
# ����׷���������
# -----------------------------------------------
class AddBuffOdds10:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[126], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[126], param )

# -----------------------------------------------
# ���ӻ���������
# -----------------------------------------------
class AddBuffOdds11:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[127], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[127], param )


# -----------------------------------------------
# ���ӵ��������
# -----------------------------------------------
class AddBuffOdds12:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[128], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[128], param )


# -----------------------------------------------
# ���ӷ���������
# -----------------------------------------------
class AddBuffOdds13:
	@staticmethod
	def description( param ):
		return _fFormatter( lbs_EquipEffects[129], param )

	@staticmethod
	def descriptionList( param ):
		return _fListFormatter( lbs_EquipEffects[129], param )

#����
class AddValueReduceRoleD:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[130], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[130], param )
	
#�Ƶ�
class AddValueAddRoleD:
	@staticmethod
	def description( param ):
		return _iFormatter( lbs_EquipEffects[131], param )

	@staticmethod
	def descriptionList( param ):
		return _iListFormatter( lbs_EquipEffects[131], param )
