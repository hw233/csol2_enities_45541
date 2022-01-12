# -*- coding: gb18030 -*-

# $Id: CWeapon.py,v 1.22 2008-09-04 07:44:43 kebiao Exp $

"""

"""
from bwdebug import *
import csconst
import ItemTypeEnum
from ItemSystemExp import EquipIntensifyExp

from config.item.GodWeaponSkillModel import Datas as gw_SM

from CEquip import CEquip
from Love3 import g_skills
from ItemSystemExp import EquipExp

g_equipIntensify = EquipIntensifyExp.instance()

class CWeapon( CEquip ):
	"""
	������

	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getFDict( self ):
		"""
		Virtual Method
		��ȡ����Ч�������Զ������ݸ�ʽ
		���ڷ��͵��ͻ���
		return WEAPON_EFFECT FDict, Define in alias.xml
		"""
		modelNum = self.model()
		gw_sk = self.getGodWeaponSkillID()
		if gw_sk in gw_SM:
			modelNum += gw_SM[gw_sk]
		data = { 	"modelNum"		:	modelNum,
					"iLevel"		:	self.getIntensifyLevel(),
					"stAmount"		:	self.getBjExtraEffectCount(),
					}

		return data

	def wield( self, owner, update = True ):
		"""
		װ������

		@param    owner: ����ӵ����
		@type     owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    True װ���ɹ���False װ��ʧ��
		@return:    BOOL
		"""
		if not CEquip.wield( self, owner, update ):
			return False

		exp = EquipExp( self, owner )

		intensifyLevel = self.getIntensifyLevel()
		if intensifyLevel != 0: #��ǿ��������ǿ��DPS��ֵ
			# Note: damage_min_base ֵ�� dps * speed �������
			# �������� damage_min_base �Ǻ��������
			owner.damage_min_value += exp.getIntensifyDamageInc()
			owner.damage_max_value += exp.getIntensifyDamageInc()
			if ItemTypeEnum.ITEM_WEAPON_STAFF:
				owner.magic_damage_value += exp.getIntensifyMagicDamageInc()

		# ����������dps��ֵ
		owner.physics_dps_value += exp.getDPSValue()

		# CombatUnit��DPS������ֵ = ������ȡ��DPS����
		owner.wave_dps_base = exp.getDPSFluctuation()

		# ����������ħ����ֵ
		owner.magic_damage_value += exp.getMagicDamageValue()

		# CombatUnit�Ĺ����ٶȻ���ֵ = ������ȡ�Ĺ����ٶ�
		owner.hit_speed_base = exp.getHitSpeedBase()

		# CombatUnit�Ĺ����������ֵ = ������ȡ�Ĺ�������
		owner.range_base = exp.getAttackRangeBase()
		
		# �Ƶе���
		owner.add_role_damage_value += exp.getAddRoleD()
		
		"""# ����������� by ����
		skillID = self.getGodWeaponSkillID()
		if skillID > 0:
			skill = g_skills[skillID]
			owner.appendAttackerHit( skill )
		"""

		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		ж��װ��

		@param    owner: ����ӵ����
		@type     owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		# ���û��װ��Ч������unwield
		if not self.isAlreadyWield(): return

		exp = EquipExp( self, owner )

		intensifyLevel = self.getIntensifyLevel()
		if intensifyLevel != 0:
			owner.damage_min_value -= exp.getIntensifyDamageInc()
			owner.damage_max_value -= exp.getIntensifyDamageInc()
			if ItemTypeEnum.ITEM_WEAPON_STAFF:
				owner.magic_damage_value -= exp.getIntensifyMagicDamageInc()
		try:
			owner.physics_dps_value -= exp.getDPSValue()
		except:
			owner.physics_dps_value = 0  #��ֹ�޸�������Ե����������
		# ����ж�����ʾ����
		# ���ֵ�DPS��������ֵ�͹����ٶȺ͹�������Ϊ�̶�ֵ
		owner.wave_dps_base = exp.getDefaultDPSFluctuation()
		owner.hit_speed_base = exp.getDefaultHitSpeedBase()
		owner.range_base = exp.getDefaultAttackRangeBase()

		owner.magic_damage_value -= exp.getMagicDamageValue()
		
		# �Ƶе���
		owner.add_role_damage_value -= exp.getAddRoleD()

		"""# ж����������
		skillID = self.getGodWeaponSkillID()
		if skillID > 0:
			owner.removeAttackerHitByID( skillID )
		"""

		CEquip.unWield( self, owner, update )
		return True

	def CalculateHardiness( self, owner ):
		"""
		�����;ö�(Ʒ�ʸı�ʱҪ���¼����;ö�)
		"""
		m_type  = self.getType()
		m_level = self.getLevel()
		m_BaseRate = self.getBaseRate()
		# ���ֽ������ȡ����ָ�������
		w_types = [ItemTypeEnum.ITEM_WEAPON_SWORD1, ItemTypeEnum.ITEM_WEAPON_STAFF, ItemTypeEnum.ITEM_WEAPON_AXE1, ItemTypeEnum.ITEM_WEAPON_LONGBOW]
		if m_type in w_types:
			hardiness = int( ( pow( m_BaseRate, 1.54 ) * pow( m_level, 1.2 ) * 20 + 20000 ) * 100 )
		else:
			ERROR_MSG( "The type of weapon(%s) is wrong!" % self.id )
			return
		self.updataHardiness( hardiness, owner )

	def setGodWeapon( self, skillID, owner = None ):
		"""
		������������
		"""
		self.set( "param1", skillID, owner )

	def getGodWeaponSkillID( self ):
		"""
		��ȡ�������Լ���ID
		"""
		return self.query( "param1", 0 )

#
#������������ʱ����Ϊ������Ǽ���ID����UID����BUG����������ȡ���ˣ�����������ȥ�����ӡ�ж���������ܵĲ�������grl20140408
#
# $Log: not supported by cvs2svn $
# Revision 1.21  2008/07/17 07:50:47  yangkai
# ����װ��ǿ����Ч����
#
# Revision 1.20  2008/07/09 03:26:37  wangshufeng
# damage_min_value -> damage_min_base
# damage_max_value -> damage_max_base
# magic_damage_value -> magic_damage_base
#
# Revision 1.19  2008/04/22 10:46:13  yangkai
# no message
#
# Revision 1.18  2008/04/12 02:14:10  yangkai
# ���������ǿ�����ԵĴ���
#
# Revision 1.17  2008/03/29 08:36:47  yangkai
# װ��ǿ������
#
# Revision 1.16  2008/03/08 06:24:23  yangkai
# no message
#
# Revision 1.15  2008/03/01 02:34:33  yangkai
# �����õ�DPS = ������DPS * �������Ա���
#
# Revision 1.14  2008/02/22 01:37:21  yangkai
# װ���ϼ�����ˢһ�������������
#
# Revision 1.13  2007/12/19 01:52:41  yangkai
# ������ȡ��Ʒ���Ե�Ĭ������
#
# Revision 1.12  2007/12/14 08:05:41  yangkai
# ж��װ����hit_speed_base = 1.5
#
# Revision 1.11  2007/11/24 03:07:54  yangkai
# ���ʵ��װ��/ж�� ��������
#
# Revision 1.10  2007/11/08 06:21:28  yangkai
# ���ӽӿڣ�
# - intensify()
#
# Revision 1.9  2007/10/26 07:00:19  kebiao
# ����ȫ�µĲ߻�ս��ϵͳ������
#
# Revision 1.8  2007/08/28 02:32:01  kebiao
# ����ս����ʽ������
#
# Revision 1.7  2007/08/15 07:52:37  yangkai
# �޸�:
#     - ���������޸�
#     - ����װ��/ж�º�������
#
# Revision 1.6  2007/08/01 05:43:04  phw
# removed: import AttrDefine
#
# Revision 1.5  2007/01/03 04:01:45  phw
# �ָ���ʹ�������Ĺ����ӳ�
# ȡ���˿���ʱ����owner.range_baseֵ,ͳһ��role.py�ﴦ��
#
# Revision 1.4  2006/08/31 08:38:47  phw
# modify method:
#     wield()
#     unwield()
#     ʵ������������С����������˺���
#
# Revision 1.3  2006/08/18 06:59:21  phw
# �޸Ľӿڣ�
#     wield()
#     unwield()
#     ɾ���˾�ϵͳ���˺��жϷ�ʽ��������ϵͳ�����˼򻯡�
#
# Revision 1.2  2006/08/11 02:57:34  phw
# ���Ը������޸�����itemInstance.keyName��itemInstance.id()ΪitemInstance.id
#
# Revision 1.1  2006/08/09 08:23:37  phw
# no message
#
#
