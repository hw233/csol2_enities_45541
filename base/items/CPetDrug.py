# -*- coding: gb18030 -*-

from CItemBase import CItemBase

class CPetDrug( CItemBase ):
	"""
	宠物一次性消耗品
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )