# -*- coding: gb18030 -*-

# $Id: CVehicleEquip.py,v 1.3 2008-08-29 07:23:32 yangkai Exp $

from CItemBase import CItemBase
from EquipEffectLoader import EquipEffectLoader
g_equipEffect = EquipEffectLoader.instance()
import ItemTypeEnum
import items

class CVehicleEquip( CItemBase ):
	"""
	���װ��
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )

	def getWieldOrder( self ):
		"""
		��ȡװ��λ��
		"""
		return None

	def wield( self, owner, update = True ):
		"""
		װ����ͷ����ͷ�����ƶ�Ч��
		@param owner	: ���
		@type owner		: Vehicle Entity
		@return			: None
		"""
		pass

	def unWield( self, owner, update = True ):
		"""
		ж����ͷ����ͷ�����ƶ�Ч��
		@param owner	: ���
		@type owner		: Vehicle Entity
		@return			: None
		"""
		pass

	def canWield( self, owner ):
		"""
		�Ƿ���װ�������װ��
		"""
		return True

	def getExtraEffect( self ):
		"""
		��ȡװ����������
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
