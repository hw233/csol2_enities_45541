# -*- coding: gb18030 -*-

from CItemBase import CItemBase
from CVehicleEquip import CVehicleEquip
import ItemTypeEnum
from EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()

class CVehicleClaw( CVehicleEquip ):
	"""
	骑宠装备-爪环
	"""
	def __init__( self, srcData ):
		"""
		"""
		CVehicleEquip.__init__( self, srcData )

	def getWieldOrder( self ):
		"""
		获取装备位置
		"""
		return ItemTypeEnum.VEHICLE_CWT_CLAW

	def wield( self, owner, update = True ):
		"""
		装备爪环
		@param owner	: 拥有者
		@type owner		: Entity
		@return			: None
		"""
		if owner is None: return

		# 玩家起效果
		extraEffect = self.getExtraEffect()
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.attach( owner, value, self )

		# pet起效果
		actPet = owner.pcg_getActPet()
		if actPet: actPet.entity.onVehicleAddEquips( [self.id] )

	def unWield( self, owner, update = True ):
		"""
		卸下爪环
		@param owner	: 拥有者
		@type owner		: Entity
		@return			: None
		"""
		if owner is None: return

		# 移除玩家效果
		extraEffect = self.getExtraEffect()
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.detach( owner, value, self )

		# 移除pet效果
		actPet = owner.pcg_getActPet()
		if actPet: actPet.entity.onVehicleRemoveEquips( [self.id] )