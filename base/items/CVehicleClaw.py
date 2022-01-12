# -*- coding: gb18030 -*-

from CVehicleEquip import CVehicleEquip
import ItemTypeEnum

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

	def wield( self, owner ):
		"""
		装备爪环
		@param owner	: 拥有者
		@type owner		: Entity
		@return			: None
		"""
		pass

	def unWield( self, owner ):
		"""
		卸下爪环
		@param owner	: 拥有者
		@type owner		: Entity
		@return			: None
		"""
		pass
