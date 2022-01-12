# -*- coding: gb18030 -*-

# $Id: CYDRoleMP.py

from CYaoDing import CYaoDing
import ItemTypeEnum
from bwdebug import *

class CYDRoleMP( CYaoDing ):
	"""
	����ҩ��
	"""
	def __init__( self, srcData ):
		CYaoDing.__init__( self, srcData )

	def checkItem( self, item, owner, target ):
		"""
		�����Ʒ�Ƿ�����Ҫ������
		@type  item : ITEM
		@param item : Ҫ������Ʒ
		"""
		if item.getType() != ItemTypeEnum.ITEM_DRUG_ROLE_MP:
			return False
		return CYaoDing.checkItem( self, item, owner, target )