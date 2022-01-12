# -*- coding: gb18030 -*-

# $Id: CYDPetMP.py

from CYaoDing import CYaoDing
import ItemTypeEnum
from bwdebug import *

class CYDPetMP( CYaoDing ):
	"""
	宠物蓝灵药鼑
	"""
	def __init__( self, srcData ):
		CYaoDing.__init__( self, srcData )

	def checkItem( self, item ):
		"""
		查看该物品是否与该鼑的使用范围符合
		"""
		if item.getType() != ItemTypeEnum.ITEM_DRUG_PET_MP:
			ERROR_MSG("CYDPetMP try to use a wrong item id = %s!" % item.id )
			return False
		return True