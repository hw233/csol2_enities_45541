# -*- coding: gb18030 -*-

# $Id: CItemPicture.py,v 1.1 2008-08-04 06:29:33 zhangyuxing Exp $

from CItemBase import CItemBase


class CItemPicture( CItemBase ):
	"""
	照片物品
	"""
	def __init__( self, srcData ):
		"""
		"""
		CItemBase.__init__( self, srcData )
#
# $Log: not supported by cvs2svn $