# -*- coding: gb18030 -*-

from CVehicleEquip import CVehicleEquip
import ItemTypeEnum

class CVehicleNecklace( CVehicleEquip ):
	"""
	���װ��-����
	"""
	def __init__( self, srcData ):
		"""
		"""
		CVehicleEquip.__init__( self, srcData )

	def getWieldOrder( self ):
		"""
		��ȡװ��λ��
		"""
		return ItemTypeEnum.VEHICLE_CWT_NECKLACE

	def wield( self, owner ):
		"""
		װ������
		@param owner	: ӵ����
		@type owner		: Entity
		@return			: None
		"""
		pass

	def unWield( self, owner ):
		"""
		ж������
		@param owner	: ӵ����
		@type owner		: Entity
		@return			: None
		"""
		pass
