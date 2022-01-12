# -*- coding: gb18030 -*-

from CVehicleEquip import CVehicleEquip
import ItemTypeEnum

class CVehicleNecklace( CVehicleEquip ):
	"""
	骑宠装备-项链
	"""
	def __init__( self, srcData ):
		"""
		"""
		CVehicleEquip.__init__( self, srcData )

	def getWieldOrder( self ):
		"""
		获取装备位置
		"""
		return ItemTypeEnum.VEHICLE_CWT_NECKLACE

	def wield( self, owner ):
		"""
		装备项链
		@param owner	: 拥有者
		@type owner		: Entity
		@return			: None
		"""
		pass

	def unWield( self, owner ):
		"""
		卸下项链
		@param owner	: 拥有者
		@type owner		: Entity
		@return			: None
		"""
		pass
