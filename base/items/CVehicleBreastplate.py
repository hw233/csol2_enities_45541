# -*- coding: gb18030 -*-

from CVehicleEquip import CVehicleEquip
import ItemTypeEnum

class CVehicleBreastplate( CVehicleEquip ):
	"""
	骑宠装备-护甲
	"""
	def __init__( self, srcData ):
		"""
		"""
		CVehicleEquip.__init__( self, srcData )

	def getWieldOrder( self ):
		"""
		获取装备位置
		"""
		return ItemTypeEnum.VEHICLE_CWT_BREASTPLATE

	def wield( self, owner ):
		"""
		装备护甲
		@param owner	: 拥有者
		@type owner		: Entity
		@return			: None
		"""
		pass

	def unWield( self, owner ):
		"""
		卸下护甲
		@param owner	: 拥有者
		@type owner		: Entity
		@return			: None
		"""
		pass
