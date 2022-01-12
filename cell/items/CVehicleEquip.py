# -*- coding: gb18030 -*-

# $Id: CVehicleEquip.py,v 1.3 2008-08-29 07:23:32 yangkai Exp $

from CItemBase import CItemBase
from EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()
import ItemTypeEnum
import items

class CVehicleEquip( CItemBase ):
	"""
	骑宠装备
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def getWieldOrder( self ):
		"""
		获取装备位置
		"""
		return None

	def wield( self, owner, update = True ):
		"""
		装备笼头，笼头附加移动效果
		@param owner	: 骑宠
		@type owner		: Vehicle Entity
		@return			: None
		"""
		pass

	def unWield( self, owner, update = True ):
		"""
		卸下笼头，笼头附加移动效果
		@param owner	: 骑宠
		@type owner		: Vehicle Entity
		@return			: None
		"""
		pass

	def canWield( self, owner ):
		"""
		是否能装备该骑宠装备
		"""
		return True

	def getExtraEffect( self ):
		"""
		获取装备附加属性
		@return:    dict
		"""
		return self.query( "eq_extraEffect", {} )

# $Log: not supported by cvs2svn $
# Revision 1.2  2008/08/28 08:19:38  yangkai
# no message
#
# Revision 1.1  2008/08/28 08:17:15  yangkai
# no message
#
