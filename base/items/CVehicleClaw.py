# -*- coding: gb18030 -*-

from CVehicleEquip import CVehicleEquip
import ItemTypeEnum

class CVehicleClaw( CVehicleEquip ):
	"""
	���װ��-צ��
	"""
	def __init__( self, srcData ):
		"""
		"""
		CVehicleEquip.__init__( self, srcData )

	def getWieldOrder( self ):
		"""
		��ȡװ��λ��
		"""
		return ItemTypeEnum.VEHICLE_CWT_CLAW

	def wield( self, owner ):
		"""
		װ��צ��
		@param owner	: ӵ����
		@type owner		: Entity
		@return			: None
		"""
		pass

	def unWield( self, owner ):
		"""
		ж��צ��
		@param owner	: ӵ����
		@type owner		: Entity
		@return			: None
		"""
		pass
