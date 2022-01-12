# -*- coding: gb18030 -*-

from CItemBase import CItemBase

class CPetBook( CItemBase ):
	"""
	制作卷
	"""
	"""
	具有大额数值能使用多次的补药
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )