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
	骑宠装备-马鞍
	"""
	def __init__( self, srcData ):
		"""
		"""
		CVehicleEquip.__init__( self, srcData )

	def getWieldOrder( self ):
		"""
		获取装备位置
		"""
		return ItemTypeEnum.VEHICLE_CWT_SADDLE

	def getResistGiddy( self ):
		"""
		获取马鞍附加眩晕抗性值
		"""
		return self.query( "vehicle_resist_giddy", 0.0 )

	def getExtraMount( self ):
		"""
		获取马鞍附加装载人数
		"""
		return self.query( "vehicle_max_mount", 0 )

	def wield( self, owner, update = True ):
		"""
		装备马鞍，马鞍附加眩晕抗性和最大装载人数
		@param owner	: 骑宠
		@type owner		: Vehicle Entity
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
		玩家下马。相当于卸载马鞍
		玩家下马之前得调用该接口
		@param owner	: 骑宠
		@type owner		: Vehicle Entity
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

# $Log: not supported by cvs2svn $
# Revision 1.4  2008/09/04 06:37:53  yangkai
# add method unWield()
#
# Revision 1.3  2008/08/30 07:51:10  yangkai
# 去掉了调试代码
#
# Revision 1.2  2008/08/29 07:23:25  yangkai
# add method: wield
#
# Revision 1.1  2008/08/28 08:58:51  yangkai
# no message
#
