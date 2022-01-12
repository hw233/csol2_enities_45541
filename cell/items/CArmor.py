# -*- coding: gb18030 -*-

# $Id: CArmor.py,v 1.15 2008-09-04 07:44:43 kebiao Exp $

"""

"""
from CEquip import *
from ItemSystemExp import EquipQualityExp
g_equipQuality = EquipQualityExp.instance()
from ItemSystemExp import ItemTypeAmendExp
g_armorAmend = ItemTypeAmendExp.instance()
from ItemSystemExp import EquipQualityExp
g_itemQualityExp = EquipQualityExp.instance()
import math
import csconst
import csdefine
import Const
import ItemTypeEnum
from ItemSystemExp import EquipIntensifyExp
from ItemSystemExp import EquipExp
g_equipIntensify = EquipIntensifyExp.instance()
import CombatUnitConfig

class CArmor( CEquip ):
	"""
	���׻�����

	"""
	def __init__( self, srcData ):
		CEquip.__init__( self, srcData )

	def getFDict( self ):
		"""
		Virtual Method
		��ȡ����Ч�������Զ������ݸ�ʽ
		���ڷ��͵��ͻ���
		return ARMOR_EFFECT FDict, Define in alias.xml
		"""
		data = { 	"modelNum"		:	self.model(),
					"iLevel"		:	self.getIntensifyLevel(),
					}

		return data

	def addGodEffect( self, owner ):
		"""
		���ӷ�����װ10%�ӳ�Ч��
		7������ȫ���� ͬһ��10����Χ�ڣ�����ǰ׺������������ǰ׺��Ҳ��ͬʱ
		���ж������װЧ����10%HP���ޣ�10%MP���� by���㣩
		"""
		# ֻ��װ�ϣ����������������װ��ʱ���Żᴥ��Ч�����
		if owner.godSuitEquipActive: return
		type = self.getType()
		if type not in ItemTypeEnum.ARMOR_SUIT: return
		preFix = self.getPrefix()
		if preFix != ItemTypeEnum.CPT_MYGOD: return
		iPrefix = self.query( "propertyPrefix", 0 )
		iLevel = self.getLevel() / 10
		ARMOR_ORDER = [	ItemTypeEnum.CEL_HEAD,
						ItemTypeEnum.CEL_BODY,
						ItemTypeEnum.CEL_BREECH,
						ItemTypeEnum.CEL_VOLA,
						ItemTypeEnum.CEL_HAUNCH,
						ItemTypeEnum.CEL_CUFF,
						ItemTypeEnum.CEL_FEET,
						]
		for index in ARMOR_ORDER:
			item = owner.getItem_( index )
			if item is None: return
			if item.getLevel()/10 != iLevel: return
			if item.getPrefix() != preFix: return
			if item.query( "propertyPrefix", 0 ) != iPrefix: return

		# ������װЧ�� ����ֵ�ͷ���ֵ �������� ���10%
		# ��������ͬ����ǰ׺��װ Ѫ �� 10% �ӳ�Ч��
		owner.HP_Max_percent += Const.ALL_GOD_PROP_EFFECT
		owner.MP_Max_percent += Const.ALL_GOD_PROP_EFFECT
		# ��������������Ա��
		owner.godSuitEquipActive = True

	def wield( self, owner, update = True ):
		"""
		װ������

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    True װ���ɹ���False װ��ʧ��
		@return:    BOOL
		"""
		if not CEquip.wield( self, owner, update ): return False

		exp = EquipExp( self, owner )

		# type( armor_base ) = INT16
		# �������ֵ
		owner.armor_base += exp.getArmorBase()

		# type( magic_armor_base ) = INT16
		# ��������ֵ
		owner.magic_armor_base += exp.getMagicArmorBase()

		# �ֿ���Ĭ
		owner.resist_chenmo_probability_value += exp.getResistMagicHushProb()

		# �ֿ�ѣ��
		owner.resist_giddy_probability_value += exp.getResistGiddyProb()

		# �ֿ�����
		owner.resist_fix_probability_value += exp.getResistFixProb()

		# ���ͶԷ��������е���
		owner.receive_be_hit_value -= exp.getReduceTargetHit()

		# �ֿ���˯
		owner.resist_sleep_probability_value += exp.getResistSleepProb()

		# �мܵ���
		owner.resist_hit_probability_value += exp.getResistHitProb()

		# ���ܵ���
		owner.dodge_probability_value += exp.getDodgeProb()
		
		# ���е���
		owner.reduce_role_damage_value += exp.getReduceRoleD()

		# ����ͬǰ׺��װ���Լӳ� by ����
		self.addGodEffect( owner )

		# ���¼�������
		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		ж��װ�����ýӿڱ��̳к󣬱�����󱻵��ã��Ա�֤���¼������Ե�ʱ�����е�װ���������Զ��Ǳ�ȥ���˵ģ�

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		# ���û��װ��Ч������unwield
		if not self.isAlreadyWield(): return

		exp = EquipExp( self, owner )

		# �������ֵ
		owner.armor_base -= exp.getArmorBase()

		# ��������ֵ
		owner.magic_armor_base -= exp.getMagicArmorBase()

		# �ֿ���Ĭ
		owner.resist_chenmo_probability_value -= exp.getResistMagicHushProb()

		# �ֿ�ѣ��
		owner.resist_giddy_probability_value -= exp.getResistGiddyProb()

		# �ֿ�����
		owner.resist_fix_probability_value -= exp.getResistFixProb()

		# ���ͶԷ��������е���
		owner.receive_be_hit_value += exp.getReduceTargetHit()

		# �ֿ���˯
		owner.resist_sleep_probability_value -= exp.getResistSleepProb()

		# �мܵ���
		owner.resist_hit_probability_value -= exp.getResistHitProb()

		# ���ܵ���
		owner.dodge_probability_value -= exp.getDodgeProb()

		# ���е���
		owner.reduce_role_damage_value -= exp.getReduceRoleD()
		
		
		# ����ͬǰ׺��װ���Լӳɵ����� by ����
		if owner.godSuitEquipActive:
			owner.HP_Max_percent -= Const.ALL_GOD_PROP_EFFECT
			owner.MP_Max_percent -= Const.ALL_GOD_PROP_EFFECT
			owner.godSuitEquipActive = False

		# ������õ���� �Ա�֤���е�װ�����ӵ����Զ�ȥ���ˣ�
		CEquip.unWield( self, owner, update )
		return True

	def CalculateHardiness( self, owner ):
		"""
		�����;ö�(Ʒ�ʸı�ʱҪ���¼����;ö�)
		"""
		m_type  = self.getType()
		m_level = self.getLevel()
		m_BaseRate = self.getBaseRate()

		func = CombatUnitConfig.FUNC_CALCHARDINESS_MAPS.get( m_type, None )
		if func is None: return
		hardiness = func( m_level, m_BaseRate )

		self.updataHardiness( hardiness, owner )

	def setQuality( self, quality, owner = None ):
		"""
		���÷���Ʒ�� by����
		"""
		CEquip.setQuality( self, quality, owner )


### end of class: CArmor ###


#
# $Log: not supported by cvs2svn $
# Revision 1.14  2008/07/09 03:22:28  wangshufeng
# armor_value -> armor_base
# magic_armor_value -> magic_armor_base
#
# Revision 1.13  2008/04/25 04:02:36  yangkai
# no message
#
# Revision 1.12  2008/04/25 04:01:43  yangkai
# no message
#
# Revision 1.11  2008/04/23 03:58:16  yangkai
# no message
#
# Revision 1.10  2008/04/22 10:46:13  yangkai
# no message
#
# Revision 1.9  2008/02/22 01:30:42  yangkai
# װ���ϼ�����ˢһ�������������
#
# Revision 1.8  2008/01/11 03:38:05  yangkai
# ���� �������magic_armor_base �� armor_base ��ֵ���ʹ���
#
# Revision 1.7  2007/12/19 01:52:26  yangkai
# ������ȡ��Ʒ���Ե�Ĭ������
#
# Revision 1.6  2007/11/24 03:06:25  yangkai
# ���ʵ��װ��/ж�� ���ߴ���
#
# Revision 1.5  2007/11/08 06:20:30  yangkai
# ���ӽӿڣ�
# - intensify()
#
# Revision 1.4  2007/08/15 07:52:03  yangkai
# �޸�:
#     - ���������޸�
#     - ����װ��/ж�º�������
#
# Revision 1.3  2006/08/18 07:01:05  phw
# �޸Ľӿڣ�
#     wield()
#     unwield()
#     ɾ���˶�������ǰװ������ļ��
#
# Revision 1.2  2006/08/11 02:57:34  phw
# ���Ը������޸�����itemInstance.keyName��itemInstance.id()ΪitemInstance.id
#
# Revision 1.1  2006/08/09 08:23:37  phw
# no message
#
#
