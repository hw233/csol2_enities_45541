# -*- coding: gb18030 -*-

# $Id: CVehicleSaddle.py,v 1.3 2008-09-04 06:34:12 yangkai Exp $

from CVehicleEquip import CVehicleEquip
import ItemTypeEnum

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

# $Log: not supported by cvs2svn $
# Revision 1.2  2008/08/29 07:20:05  yangkai
# add method : getWieldOrder()
#
# Revision 1.1  2008/08/28 08:59:04  yangkai
# no message
#
