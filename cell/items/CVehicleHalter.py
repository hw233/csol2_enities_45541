# -*- coding: gb18030 -*-

# $Id: CVehicleHalter.py,v 1.4 2008-09-04 06:37:53 yangkai Exp $

from CVehicleEquip import CVehicleEquip
import ItemTypeEnum
import csconst
from EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()

class CVehicleHalter( CVehicleEquip ):
	"""
	骑宠装备-笼头
	"""
	def __init__( self, srcData ):
		"""
		"""
		CVehicleEquip.__init__( self, srcData )

	def getWieldOrder( self ):
		"""
		获取装备位置
		"""
		return ItemTypeEnum.VEHICLE_CWT_HALTER

	def getAddMoveSpeed( self ):
		"""
		获取笼头的附加移动速度
		"""
		return self.query( "vehicle_move_speed", 0.0 )

	def wield( self, owner, update = True ):
		"""
		装备笼头，笼头附加移动效果
		@param owner	: 骑宠
		@type owner		: Vehicle Entity
		@return			: None
		"""
		if owner is None: return
		owner.move_speed_percent += self.getAddMoveSpeed() * csconst.FLOAT_ZIP_PERCENT
		owner.calcMoveSpeed()

	def unWield( self, owner, update = True ):
		"""
		卸下笼头，笼头附加移动效果
		@param owner	: 骑宠
		@type owner		: Vehicle Entity
		@return			: None
		"""
		if owner is None: return
		owner.move_speed_percent -= self.getAddMoveSpeed() * csconst.FLOAT_ZIP_PERCENT
		owner.calcMoveSpeed()


# $Log: not supported by cvs2svn $
# Revision 1.3  2008/08/30 07:51:10  yangkai
# 去掉了调试代码
#
# Revision 1.2  2008/08/29 07:23:25  yangkai
# add method: wield
#
# Revision 1.1  2008/08/28 08:58:51  yangkai
# no message
#