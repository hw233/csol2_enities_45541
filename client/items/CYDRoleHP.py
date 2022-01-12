# -*- coding: gb18030 -*-

# $Id: CYDRoleHP.py

from CYaoDing import CYaoDing
import ItemTypeEnum
from bwdebug import *

class CYDRoleHP( CYaoDing ):
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
		if item.getType() != ItemTypeEnum.ITEM_DRUG_ROLE_HP:
			return False
		return CYaoDing.checkItem( self, item, owner, target )