# -*- coding: gb18030 -*-

# $Id: CRing.py,v 1.11 2008-09-04 07:44:43 kebiao Exp $

from bwdebug import *
from COrnament import COrnament
import csconst
from ItemSystemExp import EquipIntensifyExp
g_equipIntensify = EquipIntensifyExp.instance()
import ItemTypeEnum
from ItemSystemExp import EquipExp

class CRing( COrnament ):
	"""
	��ָ
	"""
	def __init__( self, srcData ):
		COrnament.__init__( self, srcData )

	def wield( self, owner, update = True ):
		"""
		װ����ָ

		@param  owner: ��ָӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    True װ���ɹ���False װ��ʧ��
		@return:    BOOL
		"""
		# ��װ���������ٴ�װ���������Ч���Ƿ�������⣬��װ��Ҫ�󳶲��ϣ���˲�����onWield��
		if not COrnament.wield( self, owner, update ): return False
		# ��ָֻ����DPS���㣬������DPS�����������ٶȣ����벻�������

		exp = EquipExp( self, owner )
		param1 = int( self.query( "param1", 0 ) )

		intensifyLevel = self.getIntensifyLevel()
		if intensifyLevel != 0:
			# ǿ�����ӱ���
			if param1 == 0:
				# �����ָ
				owner.damage_min_value += exp.getIntensifyDamageInc()
				owner.damage_max_value += exp.getIntensifyDamageInc()
			if param1 == 1:
				# ������ָ
				owner.magic_damage_value += exp.getIntensifyMagicDamageInc()

		owner.physics_dps_value += exp.getDPSValue()
		owner.magic_damage_value += exp.getMagicDamageValue()
		
		# �Ƶе���
		owner.add_role_damage_value += exp.getAddRoleD()
		
		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		ж�½�ָ

		@param  owner: ��ָӵ����
		@type   owner: Entity
		@param update: �Ƿ�������Ч
		@type  update: bool
		@return:    ��
		"""
		# ���û��װ��Ч������unwield
		if not self.isAlreadyWield(): return

		exp = EquipExp( self, owner )
		param1 = int( self.query( "param1", 0 ) )

		intensifyLevel = self.getIntensifyLevel()
		if intensifyLevel != 0:
			if param1 == 0:
				# �����ָ
				owner.damage_min_value -= exp.getIntensifyDamageInc()
				owner.damage_max_value -= exp.getIntensifyDamageInc()
			if param1 == 1:
				# ������ָ
				owner.magic_damage_value -= exp.getIntensifyMagicDamageInc()

		owner.physics_dps_value -= exp.getDPSValue()
		owner.magic_damage_value -= exp.getMagicDamageValue()
		# �Ƶе���
		owner.add_role_damage_value -= exp.getAddRoleD()
		
		COrnament.unWield( self, owner, update )

		return True
