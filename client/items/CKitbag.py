# -*- coding: gb18030 -*-

# $Id: CKitbag.py,v 1.4 2008-05-30 03:07:15 yangkai Exp $

from CItemBase import CItemBase

class CKitbag( CItemBase ):
	"""
	背包物品
	"""
	def __init__( self, srcData ):
		CItemBase.__init__( self, srcData )
