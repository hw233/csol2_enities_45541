# -*- coding: gb18030 -*-

# $Id: CYDPetMP.py

from CYaoDing import CYaoDing
import ItemTypeEnum
from bwdebug import *

class CYDPetMP( CYaoDing ):
	"""
	��������ҩ��
	"""
	def __init__( self, srcData ):
		CYaoDing.__init__( self, srcData )

	def checkItem( self, item ):
		"""
		�鿴����Ʒ�Ƿ��������ʹ�÷�Χ����
		"""
		if item.getType() != ItemTypeEnum.ITEM_DRUG_PET_MP:
			ERROR_MSG("CYDPetMP try to use a wrong item id = %s!" % item.id )
			return False
		return True