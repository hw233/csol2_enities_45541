# -*- coding: gb18030 -*-

# $Id: CYDPetHP.py

from CYaoDing import CYaoDing
import ItemTypeEnum
from bwdebug import *

class CYDPetHP( CYaoDing ):
	"""
	�������ҩ��
	"""
	def __init__( self, srcData ):
		CYaoDing.__init__( self, srcData )

	def checkItem( self, item ):
		"""
		�鿴����Ʒ�Ƿ��������ʹ�÷�Χ����
		"""
		if item.getType() != ItemTypeEnum.ITEM_DRUG_PET_HP:
			ERROR_MSG("CYDPetHP try to use a wrong item id = %s!" % item.id )
			return False
		return True