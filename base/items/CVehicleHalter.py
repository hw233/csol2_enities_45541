# -*- coding: gb18030 -*-

# $Id: CVehicleHalter.py,v 1.1 2008-08-28 08:58:34 yangkai Exp $

from CVehicleEquip import CVehicleEquip
import ItemTypeEnum

class CVehicleHalter( CVehicleEquip ):
	"""
	���װ��-��ͷ
	"""
	def __init__( self, srcData ):
		"""
		"""
		CVehicleEquip.__init__( self, srcData )
		
	def getWieldOrder( self ):
		"""
		��ȡװ��λ��
		"""
		return ItemTypeEnum.VEHICLE_CWT_HALTER

# $Log: not supported by cvs2svn $