# -*- coding: gb18030 -*-

# $Id: CVehicleSaddle.py,v 1.5 2008-09-04 07:44:43 kebiao Exp $

from CVehicleEquip import CVehicleEquip
import ItemTypeEnum
from CItemBase import CItemBase
import csconst
from EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()

class CVehicleSaddle( CVehicleEquip ):
	"""
	���װ��-��
	"""
	def __init__( self, srcData ):
		"""
		"""
		CVehicleEquip.__init__( self, srcData )

	def getWieldOrder( self ):
		"""
		��ȡװ��λ��
		"""
		return ItemTypeEnum.VEHICLE_CWT_SADDLE

	def getResistGiddy( self ):
		"""
		��ȡ������ѣ�ο���ֵ
		"""
		return self.query( "vehicle_resist_giddy", 0.0 )

	def getExtraMount( self ):
		"""
		��ȡ������װ������
		"""
		return self.query( "vehicle_max_mount", 0 )

	def wield( self, owner, update = True ):
		"""
		װ������������ѣ�ο��Ժ����װ������
		@param owner	: ���
		@type owner		: Vehicle Entity
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
		��������൱��ж����
		�������֮ǰ�õ��øýӿ�
		@param owner	: ���
		@type owner		: Vehicle Entity
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

# $Log: not supported by cvs2svn $
# Revision 1.4  2008/09/04 06:37:53  yangkai
# add method unWield()
#
# Revision 1.3  2008/08/30 07:51:10  yangkai
# ȥ���˵��Դ���
#
# Revision 1.2  2008/08/29 07:23:25  yangkai
# add method: wield
#
# Revision 1.1  2008/08/28 08:58:51  yangkai
# no message
#
