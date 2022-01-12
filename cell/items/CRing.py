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
	戒指
	"""
	def __init__( self, srcData ):
		COrnament.__init__( self, srcData )

	def wield( self, owner, update = True ):
		"""
		装备戒指

		@param  owner: 戒指拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    True 装备成功，False 装备失败
		@return:    BOOL
		"""
		# 已装备不可能再次装备，这个是效果是否产生问题，和装备要求扯不上，因此不放在onWield里
		if not COrnament.wield( self, owner, update ): return False
		# 戒指只参与DPS计算，其他的DPS波动，攻击速度，距离不参与计算

		exp = EquipExp( self, owner )
		param1 = int( self.query( "param1", 0 ) )

		intensifyLevel = self.getIntensifyLevel()
		if intensifyLevel != 0:
			# 强化附加比率
			if param1 == 0:
				# 物理戒指
				owner.damage_min_value += exp.getIntensifyDamageInc()
				owner.damage_max_value += exp.getIntensifyDamageInc()
			if param1 == 1:
				# 法术戒指
				owner.magic_damage_value += exp.getIntensifyMagicDamageInc()

		owner.physics_dps_value += exp.getDPSValue()
		owner.magic_damage_value += exp.getMagicDamageValue()
		
		# 破敌点数
		owner.add_role_damage_value += exp.getAddRoleD()
		
		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		卸下戒指

		@param  owner: 戒指拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		# 如果没有装备效果则不用unwield
		if not self.isAlreadyWield(): return

		exp = EquipExp( self, owner )
		param1 = int( self.query( "param1", 0 ) )

		intensifyLevel = self.getIntensifyLevel()
		if intensifyLevel != 0:
			if param1 == 0:
				# 物理戒指
				owner.damage_min_value -= exp.getIntensifyDamageInc()
				owner.damage_max_value -= exp.getIntensifyDamageInc()
			if param1 == 1:
				# 法术戒指
				owner.magic_damage_value -= exp.getIntensifyMagicDamageInc()

		owner.physics_dps_value -= exp.getDPSValue()
		owner.magic_damage_value -= exp.getMagicDamageValue()
		# 破敌点数
		owner.add_role_damage_value -= exp.getAddRoleD()
		
		COrnament.unWield( self, owner, update )

		return True
