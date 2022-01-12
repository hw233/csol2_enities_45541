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
	项链
	"""
	def __init__( self, srcData ):
		COrnament.__init__( self, srcData )

	def wield( self, owner, update = True ):
		"""
		装备项链

		@param  owner: 项链拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    True 装备成功，False 装备失败
		@return:    BOOL
		"""
		if not COrnament.wield( self, owner, update ):
			return False
			
		exp = EquipExp( self, owner )

		#项链物理防御值
		owner.armor_base += exp.getArmorBase()

		#项链法术防御值
		owner.magic_armor_base += exp.getMagicArmorBase()

		#降低对方法术命中点数
		owner.receive_magic_be_hit_value -= exp.getReduceTargetMagicHit()
		
		# 御敌点数
		owner.reduce_role_damage_value += exp.getReduceRoleD()

		if update: owner.calcDynamicProperties()
		return True

	def unWield( self, owner, update = True ):
		"""
		卸下项链

		@param  owner: 项链拥有者
		@type   owner: Entity
		@param update: 是否立即生效
		@type  update: bool
		@return:    无
		"""
		# 如果没有装备效果则不用unwield
		if not self.isAlreadyWield(): return
		
		exp = EquipExp( self, owner )

		# 项链物理防御值
		owner.armor_base -= exp.getArmorBase()

		# 项链法术防御值
		owner.magic_armor_base -= exp.getMagicArmorBase()

		# 降低对方法术命中点数
		owner.receive_magic_be_hit_value += exp.getReduceTargetMagicHit()
		
		# 御敌点数
		owner.reduce_role_damage_value -= exp.getReduceRoleD()

		COrnament.unWield( self, owner, update )

		return True
