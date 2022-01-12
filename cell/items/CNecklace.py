# -*- coding: gb18030 -*-

# $Id: CNecklace.py,v 1.10 2008-09-04 07:44:43 kebiao Exp $

from bwdebug import *
from COrnament import COrnament
from ItemSystemExp import EquipQualityExp
g_equipQuality = EquipQualityExp.instance()
from ItemSystemExp import ItemTypeAmendExp
g_armorAmend = ItemTypeAmendExp.instance()
from ItemSystemExp import EquipIntensifyExp
g_equipIntensify = EquipIntensifyExp.instance()
import math
import csconst
import csdefine
import ItemTypeEnum
from ItemSystemExp import EquipExp

class CNecklace( COrnament ):
	"""
	����
	"""
	def __init__( self, srcData ):
		COrnament.__init__( self, srcData )

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
		if not COrnament.wield( self, owner, update ):
			return False
			
		exp = EquipExp( self, owner )

		#�����������ֵ
		owner.armor_base += exp.getArmorBase()

		#������������ֵ
		owner.magic_armor_base += exp.getMagicArmorBase()

		#���ͶԷ��������е���
		owner.receive_magic_be_hit_value -= exp.getReduceTargetMagicHit()
		
		# ���е���
		owner.reduce_role_damage_value += exp.getReduceRoleD()

		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		ж������

		@param  owner: ����ӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		# ���û��װ��Ч������unwield
		if not self.isAlreadyWield(): return
		
		exp = EquipExp( self, owner )

		# �����������ֵ
		owner.armor_base -= exp.getArmorBase()

		# ������������ֵ
		owner.magic_armor_base -= exp.getMagicArmorBase()

		# ���ͶԷ��������е���
		owner.receive_magic_be_hit_value += exp.getReduceTargetMagicHit()
		
		# ���е���
		owner.reduce_role_damage_value -= exp.getReduceRoleD()

		COrnament.unWield( self, owner, update )

		return True
