# -*- coding: gb18030 -*-

# $Id: CVehicleSaddle.py,v 1.1 2008-08-28 08:58:34 yangkai Exp $

from CVehicleEquip import CVehicleEquip
import ItemTypeEnum

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

# $Log: not supported by cvs2svn $
