# -*- coding: gb18030 -*-

# $Id: CYDRoleHP.py

from CYaoDing import CYaoDing
import ItemTypeEnum
from bwdebug import *

class CYDRoleHP( CYaoDing ):
	"""
	红灵药鼑
	"""
	def __init__( self, srcData ):
		CYaoDing.__init__( self, srcData )

	def checkItem( self, item, owner, target ):
		"""
		检查物品是否是想要的类型
		@type  item : ITEM
		@param item : 要检查的物品
		"""
		if item.getType() != ItemTypeEnum.ITEM_DRUG_ROLE_HP:
			return False
		return CYaoDing.checkItem( self, item, owner, target )