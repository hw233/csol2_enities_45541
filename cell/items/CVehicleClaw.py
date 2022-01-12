# -*- coding: gb18030 -*-

from CItemBase import CItemBase
from CVehicleEquip import CVehicleEquip
import ItemTypeEnum
from EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()

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

	def wield( self, owner, update = True ):
		"""
		װ��צ��
		@param owner	: ӵ����
		@type owner		: Entity
		@return			: None
		"""
		if owner is None: return

		# �����Ч��
		extraEffect = self.getExtraEffect()
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.attach( owner, value, self )

		# pet��Ч��
		actPet = owner.pcg_getActPet()
		if actPet: actPet.entity.onVehicleAddEquips( [self.id] )

	def unWield( self, owner, update = True ):
		"""
		ж��צ��
		@param owner	: ӵ����
		@type owner		: Entity
		@return			: None
		"""
		if owner is None: return

		# �Ƴ����Ч��
		extraEffect = self.getExtraEffect()
		for key, value in extraEffect.iteritems():
			effectClass = g_equipEffect.getEffect( key )
			if effectClass is None: continue
			effectClass.detach( owner, value, self )

		# �Ƴ�petЧ��
		actPet = owner.pcg_getActPet()
		if actPet: actPet.entity.onVehicleRemoveEquips( [self.id] )