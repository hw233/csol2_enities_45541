# -*- coding: gb18030 -*-

# $Id: CEquipMakeScroll.py,v 1.1 2008-10-23  huangdong Exp $

from CItemBase import CItemBase

class CEquipMakeScroll( CItemBase ):
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